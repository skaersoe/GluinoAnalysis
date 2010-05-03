#!/usr/bin/env python
# encoding: utf-8
"""
GluinoAnalysis.py

Created by Morten Dam Jørgensen on 2010-04-28.
Copyright (c) 2010 Dam Consult. All rights reserved.
"""
import ROOT
from jobhandler import JobHandler
from JobHandlerDist import JobHandlerDist
import ConfigParser
import string
import sys
        
class GluinoAnalysis(object):
    """Main method for GluinoAnalysis"""
    def __init__(self, job, options="RunOptions.cfg"):
        super(GluinoAnalysis, self).__init__()

        # Commandline override of runOptions
        if len(sys.argv) > 1:
            if sys.argv[1][-3:] == "cfg":
                options = sys.argv[1]
        
        config = ConfigParser.ConfigParser()
        config.read(options)
        
        # Parse options file
        if config.has_section("output"):
            
            if config.has_option("output", "interactive"):
                self.InteractivePlots = config.getboolean("output", "interactive")
            else:
                self.InteractivePlots = False
            
            if config.has_option("output", "SaveToFile"):
                self.SaveToFile = config.getboolean("output", "SaveToFile")
                if self.SaveToFile and config.has_option("output", "filename"):
                    self.OutputFileName = config.get("output", "filename")
                elif self.SaveToFile and not config.has_option("output","filename"):
                    self.OutputFileName = "histograms.root"
                    print "[WARNING] No output file specified, using default: %s" % self.OutputFileName
                else:
                    self.SaveToFile = False
        else:
            print '[ERROR] No "output" section in configuration file: %s' % options
            return
        
        if config.has_section("settings"):
            self.processors = config.getint("settings", "processors")
            
            if config.has_option("settings", "runtype"):
                self.runtype = config.get("settings", "runtype")
                if self.runtype == "distributed" and config.has_option("distributed", "hosts"):
                    self.distributed = True
                    self.local = False
                    self.grid = False
                    self.distributed_hosts = config.get("distributed", "hosts")
                elif self.runtype == "local":
                    self.local = True
                    self.distributed = False
                    self.grid = False
                else:
                    self.local = True
                    self.distributed = False
                    self.grid = False
            else:
                self.local = True
                self.distributed = False
                self.grid = False

        else:
            print '[ERROR] No "settings" section in configuration file: %s' % options
            return

        
        if config.has_section("input"):
            self.filestring = config.get("input", "files")
        else:
            print '[ERROR] No "input" section in configuration file: %s' % options
            return
        
        
        # User options parsed into the analysis jobs
        if config.has_section("joboptions"):
            self.joboptions = config.items("joboptions")
        else:
            print '[INFO] No "joboptions" section in configuration file: %s' % options
        
        if self.local:
            print "[INFO] Running locally"
            self.localStart(job)
        elif self.distributed:
            print "[INFO] Running distributed"
            self.distributedStart(job)
        elif self.grid:
            print "[ERROR] Grid run not implemented"
    
    def distributedStart(self, job):
        """Run distributed"""
        
        # input (grid specific list:   file1,file2,file3,etc....)
        inputFiles = self.filestring.split(', ')
        
        run = JobHandlerDist(output=self.OutputFileName, 
                            DisplayResult = self.InteractivePlots, 
                            SaveResult = self.SaveToFile, 
                            joboptions = self.joboptions)
        
        run.addHosts(self.distributed_hosts)
        
        run.addJob(job)
        for filename in inputFiles:
            run.addInputFile(filename)
        
        self.printBanner({"jobs" : 1, "ninputfiles" : len(inputFiles)})
        
        run.executeJobs()
        
    def gridStart(self, job):
        """Create grid-submittable job"""
        pass
        
    def localStart(self, job):

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


        # runner.prepareSubmission()
        # Execute!
        runner.executeJobs(jobs)

        print 90*"="

    def printBanner(self, args):
        """docstring for print"""
        print 90 *"="
        print
        print "\tGluinoAnalysis NTuple Analysis Framework\n\n"
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
        