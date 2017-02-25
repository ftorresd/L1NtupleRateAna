#!/usr/bin/env python

"""
Example L1TNtuple analysis program
"""

import threading
import ROOT, os, math
from copy import deepcopy as dc

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2(True)
ROOT.gStyle.SetOptStat(0)


def l1DoubleMu(muons):
    checker = False
    if (len(muons) >= 2):
        checker = True
    return checker  

def l1OS(muons):
    checker = False
    try:
        if (muons[0].chg*muons[1].chg < 1.0):
            checker = True
    except:
        checker = False
    return checker  

def l1QualityDoubleMu(muons):
    checker = False
    try:
        if ((8 <= muons[0].qual <= 15) and (8 <= muons[1].qual <= 15)):
            checker = True
    except:
        checker = False
    return checker  

def l1PtCutDoubleMu(ptCut, muons):
    checker = False
    try:
        if(muons[0].lorentzVector.Pt() >= ptCut and muons[1].lorentzVector.Pt() >= ptCut):
            checker = True
    except:
        checker = False
    return checker  

def l1PtCutEG(ptCut, egs):
    checker = False
    try:
        if(egs[0].lorentzVector.Pt() >= ptCut):
            checker = True
    except:
        checker = False
    return checker  



class l1Config(object):
    def __init__(self, name, expression):
        self.name  = name
        self.expression = expression
        # self.muonList = muonList
        # self.egList = egList
        self.count = 0
        # histo members
        self.histos = {}
        self.histos["h_muon1Pt_" + self.name] = ROOT.TH1F("h_muon1Pt_" + self.name, "Leading Muon Pt ("+self.name+"); Pt (GeV); NEvts", 80, 0., 80.)
        self.histos["h_muon2Pt_" + self.name] = ROOT.TH1F("h_muon2Pt_" + self.name, "Trailing Muon Pt ("+self.name+"); Pt (GeV); NEvts", 80, 0., 80.)
        self.histos["h_egPt_" + self.name] = ROOT.TH1F("h_egPt_" + self.name, "EG Pt ("+self.name+"); Pt (GeV); NEvts", 80, 0., 80.)
        self.histos["h_dimuonPtSpread_" + self.name] = ROOT.TH1F("h_dimuonPtSpread_" + self.name, "Dimuon Pt Spread ("+self.name+"); Pt (GeV); NEvts", 80, 0., 80.)
        self.histos["h_dimuonMass_" + self.name] = ROOT.TH1F("h_dimuonMass_" + self.name, "Dimuon Mass ("+self.name+"); Pt (GeV); NEvts", 80, 0., 80.)
    
    def __str__(self):
        return "Name: " + self.name + " \n Expression: " + self.expression 

    def fillHistograms(self, muonList, egList):
        if(eval(self.expression)):
            self.count += 1
            if (len(muonList) >= 1):
                self.histos["h_muon1Pt_" + self.name].Fill(muonList[0].lorentzVector.Pt())
            if (len(muonList) >= 2):
                self.histos["h_muon2Pt_" + self.name].Fill(muonList[1].lorentzVector.Pt())
                self.histos["h_dimuonPtSpread_" + self.name].Fill(math.fabs(muonList[0].lorentzVector.Pt() - muonList[1].lorentzVector.Pt()))
                self.histos["h_dimuonMass_" + self.name].Fill((muonList[0].lorentzVector + muonList[1].lorentzVector).M())
            if (len(egList) >= 1):
                self.histos["h_egPt_" + self.name].Fill(egList[0].lorentzVector.Pt())

    def printHistograms(self, ouputFile):
        ouputFile.cd()
        os.system("mkdir l1Plots/" + self.name)
        for histName, hist in self.histos.iteritems():
            hist.Write()
            hist.Draw('HIST')
            ROOT.gPad.SetLogy()
            ROOT.gPad.SaveAs("l1Plots/" + self.name + "/" + histName + ".png")




class L1Tau(object):
    def __init__(self, et = -99., eta = -99., phi = -99. , iso = -1, bx = -99):
        self.et  = et 
        self.eta = eta
        self.phi = phi
        self.iso = iso
        self.bx  = bx
        self.lorentzVector = ROOT.TLorentzVector()
        self.lorentzVector.SetPtEtaPhiM(et, eta, phi, 1.77682)

    
    def __str__(self):
        return 'Et = %.2f \t eta %.2f \t phi %.2f \t iso %d \t bx %d' %(self.et , self.eta, self.phi, self.iso, self.bx)

class L1Muon(object):
    def __init__(self, et = -99., eta = -99., phi = -99. , chg = -99, qual = -99, iso = -1, bx = -99):
        self.et  = et 
        self.eta = eta
        self.phi = phi
        self.chg = chg
        self.qual = qual
        self.iso = iso
        self.bx  = bx
        self.lorentzVector = ROOT.TLorentzVector()
        self.lorentzVector.SetPtEtaPhiM(et, eta, phi, 0.1056583745)
    
    def __str__(self):
        return 'Et = %.2f \t eta %.2f \t phi %.2f \t Chg = %.2f \t Qual = %.2f \t iso %d \t bx %d' %(self.et , self.eta, self.phi, self.chg, self.qual, self.iso, self.bx)

class L1Eg(object):
    def __init__(self, et = -99., eta = -99., phi = -99., iso = -1, bx = -99):
        self.et  = et 
        self.eta = eta
        self.phi = phi
        self.iso = iso
        self.bx  = bx
        self.lorentzVector = ROOT.TLorentzVector()
        self.lorentzVector.SetPtEtaPhiM(et, eta, phi, 0.0)

    def __str__(self):
        return 'Et = %.2f \t eta %.2f \t phi %.2f \t iso %d \t bx %d' %(self.et , self.eta, self.phi, self.iso, self.bx)



def eventLoop(files, l1Configs, outputFilename, total_rate = 1., nevents = -1, verbose = False):
    # load output file
    outfile = ROOT.TFile.Open(outputFilename, 'recreate')

    # load files
    print 'start loading %d files' %len(files)
    
    treeEvent = ROOT.TChain("l1EventTree/L1EventTree")
    treeL1up  = ROOT.TChain("l1UpgradeEmuTree/L1UpgradeTree")

    for file in files:
        treeEvent.Add(file)
        treeL1up.Add(file)

    print 'loaded %d files containing %d events' %(len(files), treeEvent.GetEntries())

    treeEvent.AddFriend(treeL1up)


    # actually loops
    for jentry, event in enumerate(treeEvent):
        if jentry%1000 == 0:
            print '=============================> event %d / %d' %(jentry, treeEvent.GetEntries())
        if nevents > 0 and jentry >= nevents:
            break
        
        ev  = treeEvent.Event
        sim = treeL1up.L1Upgrade
        

        # define objects
        ### Taus
        if verbose: print '\nevent: %d, nTaus: %d' %(ev.event, sim.nTaus)
        
        taus = []
        
        for i in range(sim.nTaus):
            taus.append(L1Tau(sim.tauEt[i], sim.tauEta[i], sim.tauPhi[i], sim.tauIso[i], sim.tauBx[i]))
        
        taus.sort(key=lambda x: x.et, reverse=True)
                
        for i, tau in enumerate(taus):
            if verbose: print '\ttau %d \t' %i, tau
        
        isotaus = [tau for tau in taus if tau.iso == 1 and abs(tau.eta) < 2.17 and tau.bx == 0]
        #############

        ### Egs
        if verbose: print '\nevent: %d, nEGs: %d' %(ev.event, sim.nEGs)
        
        egs = []
        
        for i in range(sim.nEGs):
            egs.append(L1Eg(sim.egEt[i], sim.egEta[i], sim.egPhi[i], sim.egIso[i], sim.egBx[i]))
        
        egs.sort(key=lambda x: x.et, reverse=True)
                
        for i, eg in enumerate(egs):
            if verbose: print '\teg %d \t' %i, eg
        
        isoegs = [eg for eg in egs if eg.iso == 1]
        #############

        ### Muons
        if verbose: print '\nevent: %d, nMuons: %d' %(ev.event, sim.nMuons)
        
        muons = []
        
        for i in range(sim.nMuons):
            muons.append(L1Muon(sim.muonEt[i], sim.muonEta[i], sim.muonPhi[i], sim.muonChg[i], sim.muonQual[i], sim.muonIso[i], sim.muonBx[i]))
        
        muons.sort(key=lambda x: x.et, reverse=True)

                
        for i, muon in enumerate(muons):
            if verbose: print '\tmuon %d \t' %i, muon
        
        isomuons = [muon for muon in muons if muon.iso == 1]
        #############

        for config in l1Configs: 
            config.fillHistograms(muons, egs)

    # end of events loop

 
    for config in l1Configs:
        config.printHistograms(outfile)

    #os.system("tar -zcvf l1Plots.tar.gz l1Plots/")

if __name__ == "__main__":
    l1NtupleFiles = ['file:/uscmst1b_scratch/lpc1/3DayLifetime/ftorresd/L1Ntuples/L1Ntuple_%d.root' % i for i in range(1,500)]

    #l1DoubleMu(muonList):
    #l1OS(muonList):
    #l1QualityDoubleMu(muonList):
    #l1PtCutDoubleMu(ptCut, muonList):
    #l1PtCutEG(ptCut, egList):

    l1DoubleMuConfigs = []
    for mupt in range(0,16):
        l1DoubleMuConfigs.append(l1Config("L1_DoubleMu"+str(mupt)+"", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu("+str(mupt)+".0, muonList)"))

    l1DoubleMuOSConfigs = []
    for mupt in range(0,16):
        l1DoubleMuOSConfigs.append(l1Config("L1_DoubleMu"+str(mupt)+"_OS", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu("+str(mupt)+".0, muonList)"))

    l1DoubleMuEGConfigs = []
    for mupt in range(0,16):
        for egpt in range(9,26):
            l1DoubleMuEGConfigs.append(l1Config("L1_DoubleMu"+str(mupt)+"_EG"+str(egpt), "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu("+str(mupt)+".0, muonList) and l1PtCutEG("+str(egpt)+", egList)"))

    l1DoubleMuOSEGConfigs = []
    for mupt in range(0,16):
        for egpt in range(9,26):
            l1DoubleMuOSEGConfigs.append(l1Config("L1_DoubleMu"+str(mupt)+"_OS_EG"+str(egpt), "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu("+str(mupt)+".0, muonList) and l1PtCutEG("+str(egpt)+", egList)"))


    l1Configs = l1DoubleMuConfigs+l1DoubleMuOSConfigs+l1DoubleMuEGConfigs+l1DoubleMuOSEGConfigs
    #l1Configs = l1DoubleMuConfigs
    #eventLoop(l1NtupleFiles, l1Configs)

    os.system("rm -rf l1Plots/*")

    nThreads = 20

    def split(a, n):
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n))

    l1ConfigsList = list(split(l1Configs, nThreads))
    #print l1ConfigsList

    threads = []
    for i in range(nThreads):
        threads.append(threading.Thread(target=eventLoop, args=(l1NtupleFiles, l1ConfigsList[i],"l1Plots/histograms_"+str(i)+".root",)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    os.system("tar -zcvf l1Plots.tar.gz l1Plots/")
    print "\nl1Plots.tar.gz created\n"





 