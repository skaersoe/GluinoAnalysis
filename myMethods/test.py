from GluinoAnalysis.histo import Histogram

class Test(object):
    def __init__(self, chain, histoSrv):
        
        self.evt = chain
        self.hist = histoSrv

        self.variable = 10
        self.name = "Testing"

        # Create some histograms in the "Testing Histograms" Folder
        self.h1 = self.hist.push(Histogram("TH2F",{ "title" : "Test histogram", "xlabel" : "x axis", "ylabel" : "y axis"}, [300, 300], [0, 100], [10, 193]))

        self.h2 = self.hist.push(Histogram("TH2F",{ "title" : "Test histogram 2", "xlabel" : "x axis", "ylabel" : "y axis"}, [300, 300], [0, 100], [10, 193]))


    def doTrkStuff(self, trk):
        self.h1.fill(self.evt.Trk_charge[trk], self.evt.Trk_p_t[trk])


        
