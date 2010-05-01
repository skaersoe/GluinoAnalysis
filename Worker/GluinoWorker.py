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

def printBanner(addr = None):
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
    print 90*"="
    

def main():

    sys.path.append('workdir')
    from GluinoAnalysis.GluinoAnalysisWorker import GluinoAnalysisWorker
    
    port = 1137
    ipaddress = ''
    address = (ipaddress, port)     # family is deduced to be 'AF_INET'
    listener = Listener(address, authkey='glue balls')

    printBanner(address)
    while 1:
        print "[INFO] Listening on port %d..." % port
        # print dir()

        ## FIXME Classes do not reload properly after each job...
        conn = listener.accept()

        print 90*"-"
        print '[INFO] Connection accepted from', listener.last_accepted

        conn.send(["[INFO] %s Ready to compute (%d cores available)" % (ipaddress, mp.cpu_count()), mp.cpu_count()])

        fin = open("job.tar.gz",'wb')
        fin.write(conn.recv_bytes())
        fin.close()



        # extract file
        tf =tarfile.open("job.tar.gz", 'r:gz')
        tf.extractall("workdir")
        tf.close()

        conn.send(["[INFO] %s Files received and extracted..." % ipaddress])
        
        # Import file
        _imp = __import__('runGluinoAnalysis', globals(), locals(), [], -1)

        # print dir(_imp.UserAnalysis)
        
        # Receiving object
        job = conn.recv()

        print "[INFO] Number of inputfiles received: %d" % len(job[1]["input"])
        
        out = GluinoAnalysisWorker(job[0], job[1])

        conn.send([out.output])
        conn.close()
        
        # Clear directory
        for fileName in os.listdir("workdir"):
            if fileName not in ["GluinoAnalysis"]  and not fileName[0] == ".":
                try:
                    os.remove("workdir/%s" % fileName)
                except OSError:
                    shutil.rmtree("workdir/%s" % fileName)
        try:
            os.remove("job.tar.gz")
        except OSError:
            print "[ERROR] Unable to remove job.tar.gz"

        # print dir(_imp.UserAnalysis)
        
        del out, job
        print 90*"-"
    listener.close()

if __name__ == '__main__':
	main()
    
