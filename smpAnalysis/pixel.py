from GluinoAnalysis.histo import Histogram

class Pixel(object):
    """Pixel Detector analysis"""
    def __init__(self, evt, histBranch):
        super(Pixel, self).__init__()
        self.evt = evt
        self.histBranch = histBranch
        
        self.h = {
            # dE/dx histograms
            "pixeldedx" : self.histBranch.push(Histogram("TProfile", "Pixel 2 dEdx", [200], [-800, 800])),
            "pixeldedxscatter" : self.histBranch.push(Histogram("TH2F", "Pixel dEdx Scatter", [100, 100], [-800, 800], [0, 20]))
        }
    def dedx(self, trk):
        """docstring for dedx"""
        if self.evt.Trk_dEdx[trk][0] >= 0: 
            self.h["pixeldedx"].fill(self.evt.Trk_charge[trk] * self.evt.Trk_p[trk]/1000, self.evt.Trk_dEdx[trk][0])
            self.h["pixeldedxscatter"].fill(self.evt.Trk_charge[trk] * self.evt.Trk_p[trk]/1000, self.evt.Trk_dEdx[trk][0])