#!/usr/bin/env python
# encoding: utf-8
"""
UserAnalysis.py

Created by Morten Dam Jørgensen on 2010-04-29.
Copyright (c) 2010 Niels Bohr Institute. All rights reserved.
"""

from GluinoAnalysis.histo import HistogramService, Histogram
import ROOT

## User imports (Change, remove, play around)
from mymethods.test import Test

class UserAnalysis(object):
    """docstring for UserAnalysis"""
    def __init__(self, input):
        super(UserAnalysis, self).__init__()
        self.input = input
        self.analysis(self.input)
        

    def analysis(self, input):
        """User Analysis method"""

        ############## REQUIRED BY GluinoAnalysis ##################
        # Add the input files to the ROOT chain
        chain = ROOT.TChain("CollectionTree")     
        for inputFile in input["input"]:
            chain.AddFile(inputFile)

        # Intitialize histogramService
        histoSrv = HistogramService()
        ########### END OF REQUIRED BY GluinoAnalysis #############


        # Select all branches from ROOT files
        chain.SetBranchStatus("*", 1)

        # Create Histogram branches
        histoTesting = histoSrv.branch("Testing Histograms")

        # Initialize tools
        test = Test(chain, histoTesting)


        # Histograms
        histoHandle = histoSrv.push(Histogram("TH2F",{ "title" : "My histogram", "xlabel" : "x axis", "ylabel" : "y axis"}, [300, 300], [0, 100], [10, 193]))
        histoHandle.drawOptions = ["COL"]    # Plot setting

        
        ## Use custom variables from configuration file in analysis... (dirty joboptions parsing for now...)
        N_evts = chain.GetEntries()
        if input.has_key("joboptions"):
            if int(input["joboptions"][0][1]) < N_evts and int(input["joboptions"][0][1]) > 0:
                N_evts = int(input["joboptions"][0][1])
        print "Events: %d selected out of %d" % (N_evts, chain.GetEntries())

        ## event loop         
        for i in xrange(N_evts):
            if i % int(N_evts/10.0) == 0:
                print "At %d of %d events" % (i, N_evts)
            chain.GetEntry(i)


            ## Cuts
            # if chain.PassedL1_MU40 == 0: continue

            # Loop over tracks
            for trk in xrange(chain.Trk_N):

                # Track cuts for High_pT analysis
                if chain.Trk_p_T[trk] > 40000 and chain.Trk_eta[trk] < 1.7:
                    test.doTrkStuff(trk)
                
                # Fill 2D histogram
                if chain.Trk_dEdx[trk][j] >= 0:
                    histoHandle.fill(chain.Trk_charge[trk] * chain.Trk_p[trk]/1000.0, chain.Trk_dEdx[trk][j])



        # Return histogram service for merging (REQUIRED)
        self.histSrv =  histoSrv.returnTree()
