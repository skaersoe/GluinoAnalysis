#!/usr/bin/env python
# encoding: utf-8
"""
GluinoAnalysisWorker.py

Created by Morten Dam Jørgensen on 2010-04-30.
Copyright (c) 2010 Niels Bohr Institute. All rights reserved.
"""
from GluinoAnalysis import GluinoAnalysis
import ROOT
from jobhandler import JobHandler





class GluinoAnalysisWorker(GluinoAnalysis):
    """Gluino Analysis Worker instance"""
    def __init__(self, job, config):
        # super(GluinoAnalysisWorker, self).__init__()
        self.output = self.main(job, config)
        
    def main(self, job, config):

        # Try to handle <vector<vector float> > structures in ROOT
        ROOT.gROOT.ProcessLine('.L workdir/GluinoAnalysis/Loader.C+')

        # print job
        
        # print config
        
        # input (grid specific list:   file1,file2,file3,etc....)
        # inputFiles = self.filestring.split(',')
        # 
        # if self.processors > 0:
        #     jobs = self.processors
        # else:
        #     print "[INFORMATION] No number of processes specified using available on system, using all available CPUs."
        #     jobs = -1
        # 
        # # Initialize the Job handler
        runner = JobHandler(output="",
                            DisplayResult = False,
                            SaveResult = False, 
                            joboptions = config["joboptions"])
        # 
        # if jobs == -1: #  Print a better number then zero
        #     jobs = runner.getCPUs()
        # # self.printBanner({"jobs" : jobs, "ninputfiles" : len(inputFiles)})
        # 
        # # Add the analysis job to the queue (which is redundant at the moment... [remove?])
        runner.addJob(job)
        for filename in config["input"]:
            runner.addInputFile(filename)
            
        print "ready to run GluinoAnalysisWorker"
        # Execute!
        out = runner.executeJobs()
        print "Job done, sending output to client..."
        return out

