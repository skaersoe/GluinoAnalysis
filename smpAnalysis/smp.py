from GluinoAnalysis.histo import *
import math

class Particle(object):
    """Generic Particle classs"""
    def __init__(self):
        super(Particle, self).__init__()
        self.truth = False
        self.status = None
        self.charge = None
        self.pdg = None
        self.E = None
        self.ET = None
        self.pT = None
        self.p = None
        self.eta = None
        self.phi = None
        self.mass = None
        self.beta = None
        self.mirror = None
        
class SMPEvent(object):
    """Experimental SMP event class"""
    def __init__(self, evt, histSrv):
        super(SMPEvent, self).__init__()
        self.evt = evt
        self.hist = histSrv
        
            
        self.tru_beta_hist = self.hist.push(Histogram("TH1F", "True Beta", [300], [0, 1.1]))
        
    def GetEntry(self):
        """Update for each event"""
        # Clear for every event
        
        self.truth_particles = []
        self.tracks = []
        
        for i in xrange(len(self.evt.Tru_pdgId)):
            
            if (isRhadron(self.evt.Tru_pdgId[i]) or isSlepton(self.evt.Tru_pdgId[i])) and self.evt.Tru_status[i] == 1 and math.sqrt(self.evt.Tru_verX[i]**2 + self.evt.Tru_verY[i]**2) < 5:
                # print "Found truth..."
                truePart = Particle()
                truePart.truth = True
                truePart.pdg = self.evt.Tru_pdgId[i]
                truePart.status = self.evt.Tru_status[i]
                truePart.E = self.evt.Tru_E[i]/1000.0
                truePart.mass = self.evt.Tru_m[i]/1000.0
                truePart.p = math.sqrt((self.evt.Tru_E[i]/1000.0)**2 - (self.evt.Tru_m[i]/1000.0)**2)
                truePart.pT = self.evt.Tru_p_T[i]/1000.0
                truePart.eta = self.evt.Tru_eta[i]
                truePart.phi = self.evt.Tru_phi[i]
                truePart.charge = self.evt.Tru_charge[i]
                truePart.verX = self.evt.Tru_verX[i]
                truePart.verY = self.evt.Tru_verY[i]            
                truePart.verZ = self.evt.Tru_verZ[i]
                truePart.verR = math.sqrt(self.evt.Tru_verX[i]**2 + self.evt.Tru_verY[i]**2 + self.evt.Tru_verZ[i]**2)
                truePart.beta = math.sqrt(1.0 -1.0/(self.evt.Tru_E[i]/self.evt.Tru_m[i])**2)
                
                self.truth_particles.append(truePart)
                
                self.tru_beta_hist.fill(math.sqrt(1.0 -1.0/(self.evt.Tru_E[i]/self.evt.Tru_m[i])**2))
    
        # print "Collected %d R-Hadrons." % len(self.truth_particles)
        
        for t in xrange(self.evt.Trk_N):
            track = Particle()
            track.truth = False
            track.phi = self.evt.Trk_phi[t]
            track.eta = self.evt.Trk_eta[t]
            
            for tru in self.truth_particles:
                dRad = dR(track.eta, track.phi, tru.eta, tru.phi)
                if dRad < 0.1:
                    track.truth_link = tru
                    tru.track_link = track



### UTILITY METHODS #################################################################################
    
def isRMeson(pdg):
    """Check for RMeson"""
    if  pdg == 1000993 or pdg == 1009113 or pdg == 1009213 or pdg == 1009223 or pdg == 1009313 or pdg == 1009323 \
    or pdg == 1009333 or pdg == 1000612 or pdg == 1000622 or pdg == 1000632 or pdg == 1000642 or pdg == 1000652:
        return True
    else:
		return False
		
def isSlepton(pdg):
    """CHeck for slepton PDG code"""
    if pdg ==1000011 or pdg ==1000013 or pdg ==1000015 or pdg == 2000011  or pdg ==2000013 or pdg ==2000015:
        return True
    else:
        return False
            
def isRhadron(pdg):
    """docstring for isRhadron"""
    if pdg == 1000993 or pdg == 1009113 or pdg == 1009213 or pdg == 1009223 or pdg == 1009313 or pdg == 1009323 or pdg == 1009333 or pdg == 1091114 	or pdg == 1092114 or pdg == 1092214 or pdg 	== 1092224 or pdg == 1093114     or pdg == 1093214 or pdg == 1093224 or pdg == 1093314 or pdg == 1093324 or pdg == 1093334 or pdg == 1000612	or pdg == 1000622 or pdg == 1000632 or pdg	== 1000642 or pdg == 1000652 or pdg == 1006113  or pdg == 1006211 or pdg == 1006213 or pdg == 1006223 or pdg == 1006311 or pdg == 1006313 or pdg == 1006321 or pdg == 1006323 or pdg == 1006333:
        return True
    else:
        return False

def dR(eta1, phi1, eta2, phi2):
    """Calculate the distance between two tracks in eta/phi space"""
    dPhi = math.fabs(phi1 - phi2)
    while dPhi > math.pi:
        dPhi = math.fabs(dPhi - 2.0*math.pi)
    
    return math.sqrt((eta1-eta2)**2 + dPhi**2)
