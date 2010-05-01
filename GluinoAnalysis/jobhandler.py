import multiprocessing as mp
import ROOT
from copy import deepcopy

# new stuf for dist
import os, sys

class JobHandler(object):
    """
    
    Handles distributed analysis jobs.
    
    """
    def __init__(self, output="merged.root", DisplayResult = False, SaveResult = True, joboptions = None):
        super(JobHandler, self).__init__()
        
        # User opt
        self.DisplayResult = DisplayResult
        self.SaveResult = SaveResult
        
        self.inputFiles = []
        self.inputJob = []
        self.outputFile = output
        
        self.joboptions = joboptions
        
        # OUTPUT
        self.output = []
        
        
    def addInputFile(self, filename, priority = None):
        """Add input file to list"""
        # print "adding input file, %s" % filename
        self.inputFiles.append(filename)


    def addJob(self, job):
        """Add a python definition to be run..."""
        self.inputJob.append(job)

    def getCPUs(self):
        return mp.cpu_count()
    
    def executeJobs(self, threads = -1):
        """Execute the jobs on len(self.inputFiles) / filesPerJob threads"""
        if threads == -1:
            threads = mp.cpu_count()

        files =  list(split(self.inputFiles, threads))
        inputobj = []
        for f in files:
            inputobj.append({"input" : f, "joboptions" : self.joboptions})

        p = mp.Pool(threads)
        for job in self.inputJob:
            self.output = p.map(job, inputobj)
        
        # Merge the histograms into one file
        self.mergeHistograms()
        
        # Save results to ROOT file
        if self.SaveResult:
            self.writeHistogramsToFile()
            print "Output written to: %s" % self.outputFile

        # Display results on the screen 
        if self.DisplayResult:
            self.displayHistograms()

        # Return merged histogram structure
        return self.output[0].histSrv
        
    def mergeHistograms(self):
        """docstring for mergeHistograms"""
        # When jobs are done, merge histograms
        for i in xrange(1,len(self.output)):
            self.output[0].histSrv.addToSelf(self.output[i].histSrv)
        return self.output[0].histSrv

    def writeHistogramsToFile(self):
        """docstring for writeHistogramsToFile"""
        self.output[0].histSrv.write(self.outputFile)

    def displayHistograms(self):
        """Display histograms on screen"""
        self.output[0].histSrv.draw()
    
    
## AUX Stuff

def split(a, n):
    """Split a list into n lists (Generator...)"""
    k, m = len(a) / n, len(a) % n
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n))