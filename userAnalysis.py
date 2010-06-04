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

class BaseProperties(EventAnalysis):
    """Various basic information needed to construct other analyses"""
    def __init__(self, evt, histoSrv, branchName = None, userOptions = None):
        super(BaseProperties, self).__init__(evt, histoSrv, branchName, userOptions)
        
        # dE/dx vs phi and eta
        self.names = ["pixel", "SCT", "TRT", "ps", "em1", "em2", "em3", "tile1", "tile2", "tile3", "hec0", "hec1", "hec2", "hec3", "Muon"]
        self.active = [0, 3,4,5,6,7,8,9]
        
        self.dxHisto = self.histoSrv.branch("dEdx dx")
        
        self.dEdx_phi = []
        self.dEdx_eta = []

        for i in self.active:
            self.dEdx_eta.append(self.histoSrv.push(Histogram("TProfile", "dEdx for %s vs #eta" % self.names[i], [200], [0, 3])))
            self.dEdx_phi.append(self.histoSrv.push(Histogram("TProfile", "dEdx for %s vs #phi" % self.names[i], [200], [0, 4])))


        

    def event(self):
        """Event level"""
        pass
            
    def track(self, trk):
        """docstring for track"""
        
        
        # Plot dE/dx vs phi and vs eta to look for variations
        for i in xrange(len(self.dEdx_eta)):
            if self.evt.Trk_dEdx[trk][self.active[i]] > 0:
                self.dEdx_eta[i].fill(self.evt.Trk_eta[trk], self.evt.Trk_dEdx[trk][self.active[i]])
                self.dEdx_phi[i].fill(self.evt.Trk_phi[trk], self.evt.Trk_dEdx[trk][self.active[i]])
        
    def finalize(self):
        """docstring for finalize"""
        pass


class MortenAnalysisGamma(EventAnalysis):
    """Master analysis Gamma"""
    def __init__(self, evt, histoSrv, branchName = None, userOptions = None):
        super(MortenAnalysisGamma, self).__init__(evt, histoSrv, branchName, userOptions)
        self.HistoMetaSrv = self.histoSrv.branch("Meta")
        self.metaHist = {
        "events" : self.HistoMetaSrv.push(Histogram("TH1F",  {"title" : "Events", "xlabel" : "", "ylabel" : "Events"}, [3], [0, 2])),
        "events_passed_triggers" : self.HistoMetaSrv.push(Histogram("TH1F",  {"title" : "Events passed triggers", "xlabel" : "", "ylabel" : "Events"}, [3], [0, 2])),
        "event_pass_track_cuts" :  self.HistoMetaSrv.push(Histogram("TH1F",  {"title" : "Events passed Track cut", "xlabel" : "", "ylabel" : "Events"}, [3], [0, 2]))
        }
        
        self.basePlots = BaseProperties(self.evt, self.histoSrv, "Base plots", self.userOptions)
        
    def doEntryAnalysis(self):
        """Analysis happening on event level"""
        
        # Meta data
        self.metaHist["events"].fill(1)


        # Pre trigger study
        for trk in xrange(self.evt.Trk_N):
            self.basePlots.track(trk)
        
        if self.evt.PassedL1_J75 == 1:  ## Kill J5 background in LAr, add more triggers here
            return
        
        ### POST TRIGGER ###
        
        self.metaHist["events_passed_triggers"].fill(1)
        
        candidates = [] # Regular candidates
        for trk in xrange(self.evt.Trk_N):
            if self.evt.Mu_N >= 2 and self.evt.Trk_p_T[trk] > 75000: # and self.evt.Trk_N >= 2 
                candidates.append(trk)
        
        same_charge = False
        charge = 0
        for trk in xrange(len(candidates)-1):
            if self.evt.Trk_charge[trk] == self.evt.Trk_charge[trk + 1]:
                same_charge = True
                charge = self.evt.Trk_charge[trk]
        
        for trk in candidates:
            if same_charge and len(candidates) >= 2:
                self.doTrackAnalysis(trk)
                self.metaHist["event_pass_track_cuts"].fill(1)

                
    def doTrackAnalysis(self, trk):
        """Analysis happenig per track"""
        pass
    
    def doFinalize(self):
        """Run when eventloop is over"""
        pass
            
   
        
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
        chain = ROOT.TChain("CollectionTree")     
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

        mAnaly = MortenAnalysisGamma(chain, histoSrv, userOptions=options)

        ## event loop  
        try:  
            for i in xrange(N_evts):
                if i % int(N_evts/10.0) == 0:
                    print "At %d of %d events" % (i, N_evts)
                chain.GetEntry(i)
                mAnaly.doEntryAnalysis() # Analysis per event
            

        except:
            print "Event loop error", sys.exc_info()
        mAnaly.doFinalize() # Run Post Event loop methods

        # Return histogram service for merging (REQUIRED)
        self.histSrv =  histoSrv.returnTree()

        