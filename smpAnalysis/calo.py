from GluinoAnalysis.histo import *
# print [val for val in chain.Trk_dEdx[trk]] # Print all dE/dx values for track

class Calo(object):
    """docstring for Calo"""
    def __init__(self, evt, histBranch):
        super(Calo, self).__init__()
        self.evt = evt
        self.hist = histBranch
      
        self.histoLAr = self.hist.branch("Liquid Argon Calorimeters")
        self.histoTile = self.hist.branch("Tile Calorimeters")
        
        self.histoLowPT = self.hist.branch("Low momentum dEdx")
        
        # self.histoLArPre = self.histoLAr.branch("LAr presampler", "A bit more a but the pre"
        
        hxrange = [-800, 800]
        hyrange = [0, 20]
        
        self.h = {
            # LAr histograms
            "larl2" : self.histoLAr.push(Histogram("TProfile", "LAr Layer 2 dEdx", [100], hxrange)),
            "larl2scatter" : self.histoLAr.push(Histogram("TH2F", "LAr Layer 2 dEdx Scatter", [100, 100], hxrange, hyrange)),
            
            # Tile histograms
            "tilel2" : self.histoTile.push(Histogram("TProfile", "Tile Layer 2 dEdx", [100], hxrange)),
            "tilel2scatter" : self.histoTile.push(Histogram("TH2F", "Tile Layer 2 dEdx Scatter", [100, 100], hxrange, hyrange))
            
        }
        
        names = ["pixel", "SCT", "TRT", "ps", "em1", "em2", "em3", "tile1", "tile2", "tile3", "hec0", "hec1", "hec2", "hec3", "Muon"]
        self.cellN = len(names)
        self.calos = []
        for i in xrange(self.cellN):
            self.calos.append(self.hist.push(Histogram("TH2F",{ "title" : "Calo %s" % names[i], "xlabel" : "momentum [GeV/c]", "ylabel" : "dE/dx [MeV/mm]"}, [200, 200], hxrange, hyrange)))
            self.calos[i].drawOptions = ["COL"]
        
        hxrange = [-10000, 10000]
        hyrange = [0, 20]
        
        self.lcalos = []
        for i in xrange(self.cellN):
            self.lcalos.append(self.histoLowPT  .push(Histogram("TH2F",{ "title" : "Low pT Calo %s" % names[i], "xlabel" : "momentum [MeV/c]", "ylabel" : "dE/dx [MeV/mm]"}, [200, 200], hxrange, hyrange)))
            self.calos[i].drawOptions = ["COL"]
            
    def dedxTile(self, trk):
        """Tile Calorimeter dE/dx stuff"""
        if self.evt.Trk_dEdx[trk][8] >= 0:
            self.h["tilel2"].fill(self.evt.Trk_charge[trk] * self.evt.Trk_p[trk]/1000, self.evt.Trk_dEdx[trk][8])
            self.h["tilel2scatter"].fill(self.evt.Trk_charge[trk] * self.evt.Trk_p[trk]/1000, self.evt.Trk_dEdx[trk][8])
        

    def dedxLAr(self, trk):
        """docstring for dedxLAr"""
        # print "Event number=%d" % self.evt.EventNumber
        if self.evt.Trk_dEdx[trk][5] >= 0:
            self.h["larl2"].fill(self.evt.Trk_charge[trk] * self.evt.Trk_p[trk]/1000, self.evt.Trk_dEdx[trk][5])
            self.h["larl2scatter"].fill(self.evt.Trk_charge[trk] * self.evt.Trk_p[trk]/1000, self.evt.Trk_dEdx[trk][5])
    
    def alldedx(self, trk):
        """All dEdx hits"""
        for i in xrange(self.cellN):
            if self.evt.Trk_dEdx[trk][i] >= 0:
                self.calos[i].fill(self.evt.Trk_charge[trk] * self.evt.Trk_p[trk]/1000, self.evt.Trk_dEdx[trk][i])
                
    def lowdedx(self, trk):
        """docstring for lowdedx"""
        for i in xrange(self.cellN):
            if self.evt.Trk_dEdx[trk][i] >= 0:
                self.lcalos[i].fill(self.evt.Trk_charge[trk] * self.evt.Trk_p[trk], self.evt.Trk_dEdx[trk][i])