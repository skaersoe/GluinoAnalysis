#!/usr/bin/env python
# encoding: utf-8
"""
JobHandlerDist.py

Created by Morten Dam Jørgensen on 2010-04-30.
Copyright (c) 2010 Niels Bohr Institute. All rights reserved.
"""

from jobhandler import JobHandler
import threading
import tarfile
from multiprocessing.connection import Client
import os, sys
import ROOT
import time
class WorkerDescription(object):
    """A Worker description"""
    def __init__(self, ipaddress, port = 1137, password = "glueball", poolsize = 1):
        super(WorkerDescription, self).__init__()
        self.ipaddress = ipaddress
        self.port = port
        self.password = password
        self.poolsize = poolsize
        self.jobFiles = []
        self.corecount = 0
        self.alive = False

class JobHandlerDist(JobHandler):
    """docstring for JobHandlerDist"""
    def __init__(self, output="merged.root", DisplayResult = False, SaveResult = True, joboptions = None):
        super(JobHandlerDist, self).__init__()
        
        
        # User opt
        self.DisplayResult = DisplayResult
        self.SaveResult = SaveResult
        
        self.workers = []
        self.inputStack = []

        self.outputFile = output
        self.joboptions= joboptions        
        
        # Wokrer meta info
        self.alive = 0 # Number of answering workers
        self.C = []  # Number of cores available per worker
        self.called = 0 # Number of worker tried (same as len(self.workers))
        self.success = 0
        # Thread
        self.wait_for_core_count = threading.Event()
        
        # Output
        self.output = []

    def calcFileDistribution(self):
        """Calculate how the input files should be distributed based on various parameters."""
        
        print 90*"-"
        # Sample a few files to get the number of entries 
        N_samp = 3 # Number of files to sample
        if len(self.inputFiles) < N_samp:
            N_samp = len(self.inputFiles)
        
        chain = ROOT.TChain("CollectionTree")     
        for f in xrange(N_samp):
            chain.AddFile(self.inputFiles[f])
        
        N_evt = chain.GetEntries()
        EpF = N_evt / N_samp # Events per file
        
        N_evt_Total = len(self.inputFiles) * EpF # Total number of events ('ish..)
        
        

        self.workers.sort(key=lambda worker: worker.corecount, reverse=True) # sort based on available cores
                    
        print "[INFO] Total number of events= %d, Event per file= %d" % (N_evt_Total, EpF)
        
        C = sum(self.C) # Total number of cores
        print "[INFO] Input files %f, cores %d" % (len(self.inputFiles), C)
        FpC = float(len(self.inputFiles)) / float(C) # Files per core
        
 
        print "[INFO] Files per core: %f" % FpC

        
        # Cores  / worker available
        
        print "[INFO] Worker alive: %s, with a total of %d cores." % (str(self.alive), sum(self.C))
        
        print "[INFO] Workers in list: %d " % len(self.workers)
        inpCount = 0
        for worker in self.workers:
            print "[INFO] Worker ip %s cores: %d" % (worker.ipaddress, worker.corecount)
            print "[INFO] Ideal number of files for this worker: %f" % (worker.corecount * FpC)
            if worker is self.workers[-1]:
                worker.jobFiles = self.inputFiles[inpCount:]
                # print self.inputFiles[inpCount:]
            else:
                # print self.inputFiles[inpCount:inpCount+int(worker.corecount * FpC)]
                worker.jobFiles =  self.inputFiles[inpCount:inpCount+int(worker.corecount * FpC)]
            inpCount = inpCount+int(worker.corecount * FpC)

        print 90*"-"

    def executeJobs(self):
        """Execute the various job connections thingies... stufff..self"""
        print "[INFO] Extracting analysis runtime environment"
        self.prepareSubmission()
        
        

        print "[INFO] Initializing connection to %d workers" % len(self.workers)
        
        self.wait_for_core_count.clear() # Lock 
        nStartTreads = threading.activeCount()
        for w in xrange(len(self.workers)):
            t = threading.Thread(target=self.workerConnection, args=(w,))
            t.start()
            self.alive += 1
        print "[INFO] Done submitting jobs"

        while self.alive > 0: # before: threading.active_count() > nStartTreads
            # Do something more interesting with this loop....

            if len(self.C) == self.alive and self.alive > 0 and not self.wait_for_core_count.isSet(): # When all threads have reported back the number of cores, ask threads to continue
                # print "clearing core count lock because: self.C (%d) == self.alive (%d)" % (len(self.C), self.alive)
                # Get som info about the input data
                self.calcFileDistribution()                
                self.wait_for_core_count.set()

                
            time.sleep(1) # Relax dude
            # print "Waiting for jobs to finish... (Threads = %d)" % threading.activeCount()
            
        
        if self.success > 0:
            print "[INFO] All jobs done, merging..."
            self.mergeHistograms()
        
            # Save results to ROOT file
            if self.SaveResult:
                self.writeHistogramsToFile()
                print "[INFO] Output written to: %s" % self.outputFile

            # Display results on the screen 
            if self.DisplayResult:
                self.displayHistograms()
        else:
            print "[ERROR] All jobs failed."
        
        self.clean()
            
        
    def mergeHistograms(self):
        """docstring for mergeHistograms"""
        # When jobs are done, merge histograms
        for i in xrange(1,len(self.output)):
            self.output[0].addToSelf(self.output[i])
        return self.output[0]

    def writeHistogramsToFile(self):
        """docstring for writeHistogramsToFile"""
        self.output[0].write(self.outputFile)

    def displayHistograms(self):
        """Display histograms on screen"""
        self.output[0].draw()

    def prepareSubmission(self):
        """docstring for prepareSubmission"""

        tar = tarfile.open("job.tar.gz", "w:gz")
        for fileName in os.listdir("."):
            if fileName not in ["GluinoAnalysis", "website", "extras", "Worker"] and fileName.find(".pyc") == -1 and fileName.find(".gz") == -1 and fileName.find(".root") == -1 and fileName.find(".cfg") == -1 and not fileName[0] == ".":
                tar.add(fileName)
        tar.close()
    
    def clean(self):
        """Clean up after jobs done"""
        os.remove("job.tar.gz")
    def addHosts(self, hosts):
        """Add hosts from input file format"""
        hosts = hosts.split(",")
        for host in hosts:
            host = host.strip() # remove excess spaces
            ipport, passwd = host.split(";")
            ip, port = ipport.split(":")
            self.addHost(ip, int(port), passwd)

    def addHost(self, ipaddress, port, password):
        """docstring for addHost"""
        self.workers.append(WorkerDescription(ipaddress, port, password))
        

    def workerConnection(self, wid):
        """Thread with worker connection"""
        worker = self.workers[wid]
        self.called += 1
        print "[INFO] Connecting to %s:%d..." % (worker.ipaddress, worker.port)
        #TODO make try except statement to catch unresponsive hosts
        address = (worker.ipaddress, worker.port)
        try:
            conn = Client(address, authkey=worker.password)
            worker.alive = True # Add a good flag
            
            # Connect and get ready token
            resp = conn.recv()
            print resp[0]
        
            worker.corecount = resp[1]
            self.C.append(resp[1]) # Add the number of available cores to collection

            with open("job.tar.gz", 'rb') as f:
                conn.send_bytes(f.read())
            f.close()
        
            # PAUSE HERE and wait for all threads to return core number
            self.wait_for_core_count.wait()
        
            print "[INFO] %d Job files allocated to worker %s" % (len(worker.jobFiles), worker.ipaddress)
        
            rec = conn.recv()
            print rec[0]

            conn.send([self.inputJob[0], {"input" : worker.jobFiles, "joboptions" : self.joboptions}])
 
            output = conn.recv()
            if output[0]:
                self.output.append(output[0]) #Write to stack of histograms
                self.success += 1
            else:
                print "[ERROR] Job failed at %s:%d" % address
                # TODO We should resubmit the jobs to another worker....
            conn.close()
            print "[INFO] Connection to %s closed" % worker.ipaddress

        except:
            print "[WARNING] Connection to %s:%d failed. q" % (address[0], address[1])#, sys.exc_info()[1][1])
        finally:
            self.alive -= 1
        
        
## AUX Stuff

def split(a, n):
    """Split a list into n lists (Generator...)"""
    k, m = len(a) / n, len(a) % n
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n))