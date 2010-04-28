#!/usr/bin/env python
# encoding: utf-8
"""
 pyGluino
 PyGluino is a ROOT NTuple analysis framework, for high-energy physics analysis.
 
 Usage:
    Edit analysis()
    command: > python myAnalysis.py input1.root,input2.root,input3.root n_threads


 Requirements:
     CERN ROOT 5.26 or later, compiled with PyROOT
     Python 2.6 or later
     
     Configured environment (Example assuming ROOT installed in /usr/local):
     export ROOTSYS=/usr/local
     export LD_LIBRARY_PATH=$ROOTSYS/lib:$ROOTSYS/lib/root:$PYTHONDIR/lib:$LD_LIBRARY_PATH
     export PYTHONPATH=$ROOTSYS/lib:$ROOTSYS/lib/root:$PYTHONPATH
     

 More info at: http://gluino.com

 Created by Morten Dam Jørgensen on 2010-04-24.
 Copyright (c) 2010 Dam Consult. All rights reserved.
"""

################################################################################
## System imports (DO NOT EDIT)
import sys
import user
import ROOT
from GluinoAnalysis.GluinoAnalysis import GluinoAnalysis
from GluinoAnalysis.histo import HistogramService, Histogram


################################################################################
## Your analysis, edit to suit your needs

## User imports
from smpAnalysis.calo import Calo
from smpAnalysis.pixel import Pixel
from smpAnalysis.trt import TRT
from smpAnalysis.smp import SMPEvent

def analysis(input):
    """Analysis method"""
    
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
    histoCalo = histoSrv.branch("Calorimeters")
    histoPixel = histoSrv.branch("Pixel detector")
    histoTRT = histoSrv.branch("TRT detector")
    histoTruth = histoSrv.branch("Truth information")
    # Initialize tools
    calo = Calo(chain, histoCalo)
    pixel = Pixel(chain, histoPixel)
    trt = TRT(chain, histoTRT)

    smpEvent = SMPEvent(chain, histoTruth)
    
    ## Use custom variables from configuration file in analysis... (dirty joboptions parsing for now...)
    if input.has_key("joboptions"):
        N_evts = int(input["joboptions"][0][1])
    else:
        N_evts = -1
        
    if N_evts == -1 or N_evts > chain.GetEntries():
        N_evts = chain.GetEntries()
        
    print "Events: %d" % N_evts
    
    ## event loop         
    for i in xrange(N_evts):
        chain.GetEntry(i)
        smpEvent.GetEntry()
        
        ## Cuts
        # if chain.PassedL1_MU40 == 0: continue
        
        # Loop over tracks
        for trk in xrange(chain.Trk_N):
            
            # Track cuts for High_pT analysis
            if chain.Trk_p_T[trk] > 40000 and chain.Trk_eta[trk] < 1.7:
                calo.dedxLAr(trk)
                calo.dedxTile(trk)
                calo.alldedx(trk)
                pixel.dedx(trk)
                
                trt.betastuff(trk)
                trt.dedx_bit(trk)
               
            # Low pT plots 
            elif chain.Trk_p_T[trk] <= 10000:
                calo.lowdedx(trk)
    
    
    
    # Return histogram service for merging (REQUIRED)
    return histoSrv.returnTree()



################################################################################
######################### DO NOT EDIT BELOW THIS LINE ##########################
################################################################################
def main():
    """Execute the analysis"""
    gluino = GluinoAnalysis(analysis, "RunOptions.cfg")
    
if __name__ == "__main__":
    main()