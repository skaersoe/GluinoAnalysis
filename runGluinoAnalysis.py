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
import ROOT
from GluinoAnalysis.GluinoAnalysis import GluinoAnalysis

################################################################################
## Your analysis, edit to suit your needs
from userAnalysis import UserAnalysis

################################################################################
######################### DO NOT EDIT BELOW THIS LINE ##########################
################################################################################
def main():
    """Execute the analysis"""
    dir()
    gluino = GluinoAnalysis(UserAnalysis)
    
if __name__ == "__main__":
    main()