#!/usr/bin/env python
# encoding: utf-8
"""
GluinoWorker.py

Created by Morten Dam Jørgensen on 2010-04-29.
Copyright (c) 2010 Niels Bohr Institute. All rights reserved.
"""

import sys
import os
import multiprocessing as mp
from multiprocessing.connection import Listener
from array import array
import tarfile
import shutil
import ConfigParser

def printBanner(addr = None, maxcores = mp.cpu_count()):
    """docstring for print"""
    print 90 *"="
    print
    print " Worker Node"
    print 
    print "\tGluinoAnalysis NTuple Analysis Framework\n\n"
    print "\tAuthor: Morten Dam Joergensen, 2010\n"
    print "\thttp://gluino.com"
    print
    print "\tLaunching on %s:%d" % addr
    print "\tUsing %d (of %d) cores" %  (maxcores, mp.cpu_count())
    print 90*"="
    

def main():
    # Commandline override
    if len(sys.argv) > 1:
        if sys.argv[1][-3:] == "cfg":
            options = sys.argv[1]
        else:
            options = "WorkerSettings.cfg"
    else:
        options = "WorkerSettings.cfg"
    
    config = ConfigParser.ConfigParser()
    config.read(options)
    
    # Parse options file
    if config.has_section("settings"):
        ipaddress = config.get("settings", "ipaddress")
        port = config.getint("settings", "port")
        password = config.get("settings", "password")
        
        maxcores = mp.cpu_count()    
        if config.has_option("settings", "maxcores"):
            if config.getint("settings","maxcores") < 0:
                maxcores = mp.cpu_count() + config.getint("settings", "maxcores")
            elif config.getint("settings", "maxcores") > 0 and config.getint("settings", "maxcores") <= maxcores:
                maxcores = config.getint("settings", "maxcores")
                
    else:
        print "[WARNING] No input file detected, using default settings."    
        port = 1137
        ipaddress = ''
        password = 'glue balls'
        

    sys.path.append('workdir')
    from GluinoAnalysis.GluinoAnalysisWorker import GluinoAnalysisWorker
    
    
    address = (ipaddress, port)     # family is deduced to be 'AF_INET'
    listener = Listener(address, authkey=password)

    printBanner(address, maxcores)
    
    while 1:
        #TODO Add timeout for unresponsive masters
        print "[INFO] Listening on port %d..." % port
        try:
            conn = listener.accept()

            print 90*"-"
            print '[INFO] Connection accepted from', listener.last_accepted

            conn.send(["[INFO] '%s' Ready to compute (%d cores available)" % (ipaddress, maxcores), maxcores])

            with open("job.tar.gz",'wb') as fin:
                fin.write(conn.recv_bytes())
            fin.close()

            # extract file
            tf = tarfile.open("job.tar.gz", 'r:gz')
            tf.extractall("workdir")
            tf.close()

            conn.send(["[INFO] '%s' Files received and extracted..." % ipaddress])
        
            _imp = __import__('userAnalysis', globals(), locals(), [], -1)      # Import file
            reload(_imp)                    # Make sure the new userAnalysis is active
        
            
            job = conn.recv()                # Receiving object (job[0] is the userAnalysis instance, and job[1] is configuration data (dict))
            job[1]["maxcores"] = maxcores    # pass on the amount of cores to the jobhandler
        
            print "[INFO] Number of inputfiles received: %d" % len(job[1]["input"])

            out = GluinoAnalysisWorker(job[0], job[1])  # Execute the job

            conn.send([out.output])         # Return the histogram data (HistogramService obb)
            del out, job                    # FIXME might not be needed at all
        except EOFError:
            print "[ERROR] Connection lost prematurely"
        except mp.AuthenticationError:
            print "[ERROR] Authentication Error"
        finally:
            try:
                conn.close()
            except:
                pass # Already caught above...
            # Clear directory
            for fileName in os.listdir("workdir"):
                        if fileName not in ["GluinoAnalysis"]  and not fileName[0] == ".":
                            try:
                                os.remove("workdir/%s" % fileName)
                            except OSError:
                                try:
                                    shutil.rmtree("workdir/%s" % fileName)
                                except:
                                    print "[ERROR] Error deleting file or directory: %s" % fileName
            try:
                os.remove("job.tar.gz")
            except OSError:
                print "[ERROR] Unable to remove job.tar.gz"
        
            print 90*"-"
    listener.close()

if __name__ == '__main__':
	main()
    