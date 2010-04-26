import multiprocessing as mp
import ROOT
from copy import deepcopy


    
    
class JobHandler(object):
    """
    
    Handles distributed analysis jobs.
    
    """
    def __init__(self, output="merged.root", DisplayResult = False, SaveResult = True):
        super(JobHandler, self).__init__()
        
        # User opt
        self.DisplayResult = DisplayResult
        self.SaveResult = SaveResult
        
        self.inputFiles = []
        self.inputJob = []
        self.outputFile = output

        
    def addInputFile(self, filename, priority = None):
        """Add input file to list"""
        self.inputFiles.append(filename)


    def addJob(self, job):
        """Add a python definition to be run..."""
        self.inputJob.append(job)

    
    def executeJobs(self, threads = 0):
        """Execute the jobs on len(self.inputFiles) / filesPerJob threads"""
        if threads == 0:
            threads = mp.cpu_count()

        files =  list(split(self.inputFiles, threads))
        inputobj = []
        for f in files:
            inputobj.append({"input" : f})#, "output" : outName})

        p = mp.Pool(threads)
        for job in self.inputJob:
            out = p.map(job, inputobj)
        
        # When jobs are done, merge histograms
        for i in xrange(1,len(out)):
            out[0].addToSelf(out[i])
        
        # Save results to ROOT file
        if self.SaveResult:
            out[0].write(self.outputFile)
            print "Output written to: %s" % self.outputFile

        # Display results on the screen 
        if self.DisplayResult:
            out[0].draw()


## AUX Stuff

def split(a, n):
    """Split a list into n lists (Generator...)"""
    k, m = len(a) / n, len(a) % n
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n))