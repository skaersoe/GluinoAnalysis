#!/usr/bin/env python
# encoding: utf-8
"""
 pyGluino
 PyGluino is a ROOT NTuple analysis framework, for high-energy physics analysis.
 
 Usage:
    Edit analysis()
    command: > python pyGluino.py input1.root,input2.root,input3.root n_threads


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
from histogramService import Histogram, HistogramService
from jobhandler import JobHandler


################################################################################
## User Options (EDIT)



# Show ROOT Session with histograms after completion
InteractivePlots = True

# Save histograms to ROOT file
SaveToFile = True
OutputFileName = "outputhistograms.root"



################################################################################
## Your analysis (EDIT THIS)


def analysis(input):
    """Analysis method"""
    
    # Add the input files to the ROOT chain
    chain = ROOT.TChain("CollectionTree")     
    for inputFile in input["input"]:
        chain.AddFile(inputFile)
    
    # Select all branches
    chain.SetBranchStatus("*", 1)
    
    # Intitialize histogramService
    histoSrv = HistogramService()
    
    # Create Histogram branches
    histoCalo = histoSrv.branch("Calorimeters")
    histoPixel = histoSrv.branch("Pixel detector")
    histoMuon = histoSrv.branch("Muon Detector")
    histoTruth = histoSrv.branch("Truth information")
    
    # Create histograms
    myProfilePlot = histoSrv.push(Histogram("TProfile", "My Profile Plot", [100], [-1, 1]))

    ## event loop    
    for i in xrange(chain.GetEntries()):
        chain.GetEntry(i)
        
        ## Cuts
        # if chain.PassedL1_MU40 == 0: continue
        
        # Loop over tracks
        for trk in xrange(chain.Trk_N):
            
            # Track cuts for High_pT analysis
            if chain.Trk_p_T[trk] > 40000 and chain.Trk_eta[trk] < 1.7:
                
                # Save some data to the histogram
                myProfilePlot.push(chain.Trk_charge[trk])
                
    
    # Return histogram service for merging
    return histoSrv.returnTree()












################################################################################
######################### DO NOT EDIT BELOW THIS LINE ##########################
################################################################################

def printBanner(args):
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
    if InteractivePlots:
        print "Displaying results on screen."
    if SaveToFile:
        print "Writing output to file : %s" % OutputFileName
    print
    
def main():
    
    # Try to handle <vector<vector float> > structures in ROOT
    ROOT.gROOT.ProcessLine('.L Loader.C+')

    # input (grid specific list:   file1,file2,file3,etc....)
    inputFiles = sys.argv[1].split(',')
    if len(sys.argv) > 2:
        if int(sys.argv[2]) > 0 and int(sys.argv[2]):
            jobs = int(sys.argv[2])
        else:
            print "[WARNING] Ilegal number of processes (must be larger then 1 and less then the number of input files) specified, using single threaded analysis."
            jobs = 1
    else:
        print "[INFORMATION] No number of processes specified using available on system, using all available CPUs."
        jobs = 0

    printBanner({"jobs" : jobs, "ninputfiles" : len(inputFiles)})
    runner = JobHandler(output=OutputFileName, DisplayResult = InteractivePlots, SaveResult = SaveToFile)
    runner.addJob(analysis)
    for filename in inputFiles:
        runner.addInputFile(filename)
    
    runner.executeJobs(jobs)

    print 90*"="

if __name__ == "__main__":
    main()
