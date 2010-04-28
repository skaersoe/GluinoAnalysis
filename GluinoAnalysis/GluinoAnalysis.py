#!/usr/bin/env python
# encoding: utf-8
"""
GluinoAnalysis.py

Created by Morten Dam Jørgensen on 2010-04-28.
Copyright (c) 2010 Dam Consult. All rights reserved.
"""
import ROOT
from jobhandler import JobHandler
import ConfigParser
import string

        
class GluinoAnalysis(object):
    """Main method for GluinoAnalysis"""
    def __init__(self, job, options="RunOptions.cfg"):
        super(GluinoAnalysis, self).__init__()
        
        config = ConfigParser.ConfigParser()
        config.read(options)
        
        self.InteractivePlots = config.getboolean("output", "interactive")
        self.SaveToFile = config.getboolean("output", "SaveToFile")
        self.OutputFileName = config.get("output", "filename")
        self.processors = config.getint("settings", "processors")
        self.filestring = config.get("input", "files")
        
        # User options parsed into the analysis jobs
        self.joboptions = config.items("joboptions")
        
        self.main(job)
    
    def printBanner(self, args):
        """docstring for print"""
        print 90 *"="
        print
        print "\tpyGluino NTuple Analysis Framework\n\n"
        print "\tAuthor: Morten Dam Joergensen, 2010\n"
        print "\thttp://gluino.com"
        print
        print 90*"="
        print
        print " Initializing Analysis with the following conditions: "
        print
        print "Number of jobs specified = %d" % args["jobs"]        
        print "Number of input files: %d" % args["ninputfiles"]
        if self.InteractivePlots:
            print "Displaying results on screen."
        if self.SaveToFile:
            print "Writing output to file : %s" % self.OutputFileName
        print

    def main(self, job):

        # Try to handle <vector<vector float> > structures in ROOT
        ROOT.gROOT.ProcessLine('.L GluinoAnalysis/Loader.C+')

        # input (grid specific list:   file1,file2,file3,etc....)
        inputFiles = self.filestring.split(',')
            
        if self.processors > 0:
            jobs = self.processors
        else:
            print "[INFORMATION] No number of processes specified using available on system, using all available CPUs."
            jobs = -1

        # Initialize the Job handler
        runner = JobHandler(output=self.OutputFileName, 
                            DisplayResult = self.InteractivePlots, 
                            SaveResult = self.SaveToFile, 
                            joboptions = self.joboptions)
                            
        if jobs == -1: #  Print a better number then zero
            jobs = runner.getCPUs()
        self.printBanner({"jobs" : jobs, "ninputfiles" : len(inputFiles)})

        # Add the analysis job to the queue (which is redundant at the moment... [remove?])
        runner.addJob(job)
        for filename in inputFiles:
            runner.addInputFile(filename)

        # Execute!
        runner.executeJobs(jobs)

        print 90*"="
