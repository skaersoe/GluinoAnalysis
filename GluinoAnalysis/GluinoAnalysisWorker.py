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

        # # Initialize the Job handler
        runner = JobHandler(output="",
                            DisplayResult = False,
                            SaveResult = False, 
                            joboptions = config["joboptions"])

        # # Add the analysis job to the queue (which is redundant at the moment... [remove?])
        runner.addJob(job)
        for filename in config["input"]:
            runner.addInputFile(filename)
            
        print "[INFO] Ready to run GluinoAnalysisWorker"
        # Execute!
        out = runner.executeJobs(config["maxcores"])
        print "[INFO] Job done, sending output to client..."
        return out

