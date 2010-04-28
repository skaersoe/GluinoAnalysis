import ROOT
import math
from copy import deepcopy

class Histogram(object):
    """Histogram class"""
    def __init__(self, htype="TH1F", title="Histogram", nbin=[10], hxrange=[], hyrange=[], hzrange=[]):
        super(Histogram, self).__init__()
        self.type = htype
        self.nbin = nbin
        self.xrange = hxrange
        self.yrange = hyrange
        self.zrange = hzrange
        self.drawOptions = [] # Options unrolled on Draw(self.drawOptions)
        # Default values
        self.xlabelstr = "x axis"
        self.ylabelstr = "y axis"
        self.zlabelstr = "z axis"
        self.title = "histogram title"
        if isinstance(title, dict):
            if title.has_key("title"):  self.title = title["title"]
            if title.has_key("xlabel"): self.xlabelstr = title["xlabel"]
            if title.has_key("ylabel"): self.ylabelstr = title["ylabel"]
            if title.has_key("zlabel"): self.zlabelstr = title["zlabel"]
        elif isinstance(title, str):
            self.title = title
            
        elif isinstance(title, tuple):
            self.title = title[0]
            if len(title) > 1: self.xlabelstr = title[1]
            if len(title) > 2: self.ylabelstr = title[2]
            if len(title) > 3: self.zlabelstr  = title[3]
        else:
            print "Histogram title type not found, catastrophic..(!)"
            
        
        self.dim = len(nbin) # Dimension of histogram
        if self.dim == 1:
            self.hist = getattr(ROOT, htype)(self.title, self.title,  self.nbin[0], self.xrange[0], self.xrange[1])
        elif self.dim == 2: 
            self.hist = getattr(ROOT, htype)(self.title, self.title,  self.nbin[0], self.xrange[0], self.xrange[1], self.nbin[1], self.yrange[0], self.yrange[1])
        elif self.dim == 3:
            self.hist = getattr(ROOT, htype)(self.title, self.title,  self.nbin[0], self.xrange[0], self.xrange[1], self.nbin[1], self.yrange[0], self.yrange[1], self.nbin[2], self.zrange[0], self.zrange[1])            
        else:
            print "Error, wrong number of arguments for histogram %s." % title
        
        # self.hist.Sumw2() # Error weights
        
        # Apply options to histogram
        self.xlabel()
        self.ylabel()
        self.zlabel()
    
    def xlabel(self, text = None):
        """set/get xlabel"""
        if text: self.xlabelstr = text
        self.hist.GetXaxis().SetTitle(self.xlabelstr)
        return self.xlabelstr

    def ylabel(self, text = None):
        """set/get ylabel"""
        if text: self.ylabelstr = text
        self.hist.GetYaxis().SetTitle(self.ylabelstr)
        return self.ylabelstr

    def zlabel(self, text = None):
        """set/get zlabel"""
        if text: self.zlabelstr = text
        self.hist.GetZaxis().SetTitle(self.zlabelstr)
        return self.zlabelstr

    def title(self, text = None):
        """docstring for title"""
        if text: self.title = text
        self.hist.SetTitle(self.title)
        return self.title

    def get(self):
        """Return histogram handle"""
        return self.hist
    
    def fill(self, *args):
        """Generic fill method"""
        self.hist.Fill(*args)
        return self.hist
        
    def draw(self, *args):
        """docstring for draw"""
        self.hist.Draw(*args)
        return self.hist
        
    def drawCopy(self, *args):
        """docstring for drawCop"""
        return self.hist.DrawCopy(*args)

    def drawNormalized(self, *args):
        """docstring for drawCop"""
        return self.hist.DrawNormalized(*args)

    def scale(self, factor):
        """Scale the histogram by a factor"""
        self.hist.Scale(factor)
        return self.hist
        
    def rebin(self, factor):
        """Rebin the histogram"""
        self.hist.Rebin(factor)
        return self.hist
        
    def saveAsPdf(self, filename=None):
        """docstring for saveAsPdf"""
        pass


# Interface classes
class TP(Histogram):
    """TProfile Class"""
    def __init__(self, title="TProfile", xbin=10, hxrange=[0, 10]):
        super(TP, self).__init__("TProfile", title, [xbin], hxrange)

class TH1(Histogram):
    """TH1 Class"""
    def __init__(self, title="TH1F Histo", xbin=10, hxrange=[0, 10]):
        super(TH1, self).__init__("TH1F", title, [xbin], hxrange)
        
class TH2(Histogram):
    """TH2 Class"""
    def __init__(self, title="TH2F Histo", xbin=10, hxrange=[0, 10], ybin=10, hyrange=[0, 10]):
        super(TH2, self).__init__("TH2F", title, [xbin, ybin], hxrange, hyrange)
        self.drawOptions = ["COLS"]

class TH3(Histogram):
    """TH3 Class"""
    def __init__(self, title="TH3F Histo", xbin=10, hxrange=[0, 10], ybin=10, hyrange=[0, 10], zbin=10, hzrange=[0, 10]):
        super(TH3, self).__init__("TH3F", title, [xbin, ybin, zbin], hxrange, hyrange, hzrange)


class HistogramCollection(object):
    """A Branch collection of histograms (corresponds to a subfolder in a ROOT file)"""
    def __init__(self, name, parent=None, description = ""):
        super(HistogramCollection, self).__init__()
        self.name = name
        self.description = description
        self.collection = []
        self.nchild = 0
        self.parent = parent
        
    def branch(self, name, description = ""):
        """docstring for child"""
        child = HistogramCollection(name, self, description)
        self.collection.append(child)
        self.nchild += 1
        return child
        
    def push(self, histogram):
        """Push a histogram on stack"""
        self.collection.append(histogram)
        return histogram
    
    def draw(self, canvases):
        """Draw all elements on a canvas, and call sub branches"""
        elm = len(self.collection) - self.nchild # Number of histograms
        if elm > 0: # Don't draw empty containers (a bit dirty, but hey this is all sugar...)
            canvas = ROOT.TCanvas(self.name, self.name)
            if elm > 2:
                ratio = 16.0/9.0
                ny = math.ceil(math.sqrt(elm) / math.sqrt(ratio))
                nx = math.ceil(math.sqrt(elm) * math.sqrt(ratio))
            else:
                nx = elm
                ny = 1
            canvas.Divide(int(nx), int(ny))
            canvases.append(canvas)
            i = 1
        for histo in self.collection:
            if not isinstance(histo, HistogramCollection) and elm > 0:
                canvas.cd(i)
                histo.drawCopy(*histo.drawOptions)
                i+=1
            else:
                canvases = histo.draw(canvases)
        if elm > 0: canvas.Update()
        return canvases
        
    def write(self):
        """Write to root file """
        self.root = self.parent.root.AddFolder(self.name, self.description)
        for coll in self.collection:
            if isinstance(coll, HistogramCollection):
                coll.write()
            else:
                self.root.Add(coll.hist)

    def addToSelf(self, otherHistogramCollection):
        """ Add another HistogramCollection to this one"""
        for i in xrange(len(self.collection)):
            if not isinstance(self.collection[i], HistogramCollection):
                self.collection[i].hist.Add(otherHistogramCollection.collection[i].hist)
            else:
                self.collection[i].addToSelf(otherHistogramCollection.collection[i])

        
        
class HistogramService(object):
    """HistogramService handles collections of histograms.
    Define structure to facilitate:
    Easy creation of histograms
    Easy grouping
    Easy ROOT file output structuring 
    Easy common options (fit n histograms with same fit (histo-map))
    """
    def __init__(self, name = "Analysis", description = "Analysis Folder"):
        super(HistogramService, self).__init__()
        self.name = name
        self.description = description
        self.collection = [] # NTuple of root branches (containing HistogramCollections)
        
        
    def branch(self, name):
        """Create a new collection at root level"""
        child = HistogramCollection(name, self)
        self.collection.append(child)
        return child
        
    def draw(self):
        """Draw all elements in tree on canvases"""
        ROOT.gROOT.SetStyle("Plain")
        ROOT.gStyle.SetPalette(1)
        ROOT.gROOT.ForceStyle()
        can = []
        for child in self.collection:
            can = (child.draw(can))
        rep = '' 
        while not rep in [ 'q', 'Q', '.q', ".Q" ]: 
            rep = raw_input( 'Interactive mode, enter "q" to quit: ' ) 
            if 2 < len(rep): 
                rep = rep[0]

    def write(self, filename='histograms.root'):
        histogramFile = ROOT.TFile(filename,'recreate')    
        self.root = ROOT.gROOT.GetRootFolder().AddFolder(self.name, self.description)
        for child in self.collection:
            child.write()
        print 90*"="
        print "ROOT file generated with directory structure:\n"
        self.root.ls()
        print 90*"="
        self.root.Write()

        histogramFile.Close("R");
    def addToSelf(self, otherHistSrv):
        """Add content of an identical histogram collection to self"""
        for i in xrange(len(self.collection)):
            self.collection[i].addToSelf(otherHistSrv.collection[i])

    def returnTree(self):
        """Return the data tree"""
        return self