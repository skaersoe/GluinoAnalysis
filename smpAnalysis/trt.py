from GluinoAnalysis.histo import Histogram
from math import sqrt, pow
class TRT(object):
    """TRT Subdetector study"""
    def __init__(self, evt, hist):
        super(TRT, self).__init__()
        self.evt = evt
        self.hist = hist
        
        bit_time = 3.125 #ns
        
        
        ## Histogram booking for TRT studies ##
        self.BoT = self.hist.push(Histogram("TH1F", "Bits over threshold", [300], [-20, 20]))
        self.invBeta = self.hist.push(Histogram("TH1F", "Inverse Beta", [300], [-20, 20]))
        self.BoTScatter = self.hist.push(Histogram("TH2F",{ "title" : "TRT Bits over Thr vs P", "xlabel" : "momentum [GeV/c]", "ylabel" : "BoT"}, [200, 200], [-1000, 1000], [-20, 20]))
        
        self.lastB = self.hist.push(Histogram("TH1F", "last bits", [300], [-20, 100]))
        
        self.trt_vs_pixel = self.hist.push(Histogram("TH2F", {"title" :"Pixel dEdx vs TRT ToT", "xlabel" : "Pixel dE/dx [MeV/mm]", "ylabel" : "TRT BoT"}, [200, 200], [0, 10], [-10, 5]))
        self.trt_vs_pixel.drawOptions = ["COL"]
        self.trt_length_in_straw = self.hist.push(Histogram("TH1F", {"title": "Length in straw", "xlabel" : "l [mm]", "ylabel" : "entries"}, [100], [0, 5]))
        
        self.trt_vs_p = self.hist.push(Histogram("TH2F", {"title" : "ToT/dx for largest island", "xlabel" : "p [GeV]", "ylabel" : "ToT/dx"}, [100, 100], [-1000, 1000], [0, 10]))
        self.trt_vs_p.drawOptions = ["COL"]

        self.trt_vs_p2 = self.hist.push(Histogram("TH2F", {"title" : "ToT/dx for last island", "xlabel" : "p [GeV]", "ylabel" : "ToT/dx"}, [100, 100], [-1000, 1000], [0, 10]))
        self.trt_vs_p2.drawOptions = ["COL"]
        
    def betastuff(self, trk):
        """docstring for betastuff
        
        *............................................................................*
        *Br  428 :InDetLowBetaCandidate_BitsOverThr :                                *
        *............................................................................*
        *Br  429 :InDetLowBetaCandidate_invBeta :                                    *
        *............................................................................*
        *Br  430 :InDetLowBetaCandidate_invBetaError :                               *
        *............................................................................*
        *Br  431 :InDetLowBetaCandidate_lastBits :                                   *
        *............................................................................*        
        """
        # print self.evt.InDetLowBetaCandidate_BitsOverThr[trk]
        self.BoT.fill(self.evt.InDetLowBetaCandidate_BitsOverThr[trk])
        self.invBeta.fill(self.evt.InDetLowBetaCandidate_invBeta[trk])
        self.BoTScatter.fill(self.evt.Trk_charge[trk] * self.evt.Trk_p[trk]/1000, self.evt.InDetLowBetaCandidate_BitsOverThr[trk])
        self.lastB.fill(self.evt.InDetLowBetaCandidate_lastBits[trk])
        
        if self.evt.Trk_dEdx[trk][0] > 0:
            self.trt_vs_pixel.fill(self.evt.Trk_dEdx[trk][0], self.evt.InDetLowBetaCandidate_BitsOverThr[trk])
            
        
    def dedx_bit(self, trk):
        """Get dE/dx from bit pattern
        
        *............................................................................*
        *Br  447 :TrackTrtHitBitPatterns :                                           *
        *............................................................................*
        *Br  448 :TrackTRTHitRawBitPatterns :                                        *
        *............................................................................*
        *Br  449 :TRTdriftTime :                                                     *
        *............................................................................*
        *Br  450 :TRThitX   :                                                        *
        *............................................................................*
        *Br  451 :TRThitY   :                                                        *
        *............................................................................*
        *Br  452 :TRThitZ   :                                                        *
        *............................................................................*
        *Br  453 :TRTdriftCircleRadius :                                             *
        *............................................................................*
        *Br  454 :TRTtrackRadius :                                                   *
        *............................................................................*
        *Br  455 :TRTbec    :                                                        *
        *............................................................................*
        *Br  456 :TRTphimod :                                                        *
        *............................................................................*
        *Br  457 :TRTstrawlayer :                                                    *
        *............................................................................*
        *Br  458 :TRTlayer  :                                                        *
        *............................................................................*
        *Br  459 :TRTstr    :                                                        *
        *............................................................................*
        *Br  460 :TRTt0     :                                                        *
        *............................................................................*
        *Br  461 :TRTleadtime :                                                      *
        *............................................................................*
        *Br  462 :TRTre     :                                                        *
        *............................................................................*
        *Br  463 :TRTfe     :                                                        *
        *............................................................................*
        """
        for hit in xrange(len(self.evt.TrackTRTHitRawBitPatterns[trk])):
            raw_bits = bs(self.evt.TrackTRTHitRawBitPatterns[trk][hit])
            drift_R = abs(self.evt.TRTdriftCircleRadius[trk][hit])
            straw_R = 2.0 #mm
            # print "TRTdriftCircleRadius=%f, TRTtrackRadius=%f" % (abs(self.evt.TRTdriftCircleRadius[trk][hit]), abs(self.evt.TRTtrackRadius[trk][hit]))

            if drift_R > 0:
                d = 2.0 * sqrt(straw_R**2 - drift_R**2)
            else:
                d = -999
            
            self.trt_length_in_straw.fill(d)
            # print "----"
            # print "Distance in straw=%f" % d
            # print raw_bits
            nB_islands = [0]
            nB_all = 0
            nHLT = 0
            exclude = [0, 9, 18] # HL bins
            for b in xrange(len(raw_bits)):
                if not b in exclude:
                    if raw_bits[b] == "1":
                        nB_all += 1
                        nB_islands[len(nB_islands)-1] += 1
                    else:
                        nB_islands.append(0)
                else:
                    if raw_bits[b] == "1":
                        nHLT +=1
            # print nB_islands
            nB_islands = filter (lambda a: a != 0, nB_islands) # remove zeros
            # print nB_islands
            if not len(nB_islands) == 0:
                largest_island = max(nB_islands)
                last_island = nB_islands[-1]
                first_island = nB_islands[0]
                # print "Largest island %d\nLast island %d\nFirst island %d" % (largest_island, last_island, first_island)
            # print "nB_all=%d, nHLT=%d" % (nB_all, nHLT)
            
                self.trt_vs_p.fill(self.evt.Trk_charge[trk] * self.evt.Trk_p[trk]/1000, largest_island/d)
                self.trt_vs_p2.fill(self.evt.Trk_charge[trk] * self.evt.Trk_p[trk]/1000, last_island/d)
    
def bs(s):
    """ Convert int to string bit pattern"""
    return str(s) if s<=1 else bs(s>>1) + str(s&1)
    
    
