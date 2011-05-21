#!/usr/bin/env python
# encoding: utf-8
"""
UserAnalysis.py

Created by Morten Dam Jørgensen on 2010-04-29.
Copyright (c) 2010 Niels Bohr Institute. All rights reserved.
"""

from GluinoAnalysis.histo import HistogramService, Histogram
import ROOT
import os, sys
import array
import math


        
class UserAnalysis(object):
    """docstring for UserAnalysis"""
    def __init__(self, input):
        super(UserAnalysis, self).__init__()
        self.input = input
                
        self.analysis(self.input) # Execute analysis
        

    def analysis(self, input):
        """User Analysis method"""

        print "Entering Analysis"
        print "Jobs:"
        print input["input"]
        ############## REQUIRED BY GluinoAnalysis ##################
        # Add the input files to the ROOT chain
        chain = ROOT.TChain("CollectionTree")      ## Add your TTree name here
        for inputFile in input["input"]:
            chain.AddFile(inputFile)

        # Intitialize histogramService
        histoSrv = HistogramService()
        
        
        ## Use custom variables from configuration file in analysis...
        if input.has_key("joboptions"):
            options = {}
            for opt in xrange(len(input["joboptions"])):
                options[input["joboptions"][opt][0]] = input["joboptions"][opt][1]
        
            print options
        # Get the number of events to process
        N_evts = chain.GetEntries()
        if options.has_key("maxeventsperjob") and int(options["maxeventsperjob"]) > 0 and not N_evts == 0:
            N_evts = int(options["maxeventsperjob"])
        print "Events: %d selected out of %d" % (N_evts, chain.GetEntries())

        ########### END OF REQUIRED BY GluinoAnalysis #############


        # Select all branches from ROOT files
        chain.SetBranchStatus("*", 1)

        # mAnaly = MortenAnalysisGamma(chain, histoSrv, userOptions=options)

        ## event loop  
        try:  
            for i in xrange(N_evts):
                if i % int(N_evts/10.0) == 0:
                    print "At %d of %d events" % (i, N_evts)
                chain.GetEntry(i)
                
                for trk_i in xrange(chain.Trk_N):
                    print chain.Trk_p[trk_i]/1000.0
                
                
            

        except:
            print "Event loop error", sys.exc_info()


        # Return histogram service for merging (REQUIRED)
        self.histSrv =  histoSrv.returnTree()

        