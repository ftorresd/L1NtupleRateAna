#!/usr/bin/env python

"""
Example L1TNtuple analysis program
"""

import threading
import ROOT, os, math, sys
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

def l1PtCutDoubleMuAss(ptCutLeading, ptCutTrailling, muons):
    checker = False
    try:
        if(muons[0].lorentzVector.Pt() >= ptCutLeading and muons[1].lorentzVector.Pt() >= ptCutTrailling):
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

def l1PtCutIsoEG(ptCut, egs):
    checker = False
    try:
        isoegslist = [eg for eg in egs if eg.iso == 1]
        if(isoegslist[0].lorentzVector.Pt() >= ptCut):
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
        # self.lumiSec = -1
        # self.nBunches = -1
        # histo members
        self.histos = {}
        # self.histosCumulative = {}

        self.histos["h_muon1Pt_" + self.name] = ROOT.TH1F("h_muon1Pt_" + self.name, "Leading Muon Pt ("+self.name+"); Pt (GeV); NEvts", 80, 0., 80.)
        # self.histosCumulative["h_cumulative_muon1Pt_" + self.name] = ROOT.TH1F("h_cumulative_muon1Pt_" + self.name, "Leading Muon Pt ("+self.name+"); Pt (GeV); Rate (Hz)", 80, 0., 80.)

        self.histos["h_muon2Pt_" + self.name] = ROOT.TH1F("h_muon2Pt_" + self.name, "Trailing Muon Pt ("+self.name+"); Pt (GeV); NEvts", 80, 0., 80.)
        # self.histosCumulative["h_cumulative_muon2Pt_" + self.name] = ROOT.TH1F("h_cumulative_muon2Pt_" + self.name, "Trailing Muon Pt ("+self.name+"); Pt (GeV); Rate (Hz)", 80, 0., 80.)

        self.histos["h_egPt_" + self.name] = ROOT.TH1F("h_egPt_" + self.name, "EG Pt ("+self.name+"); Pt (GeV); NEvts", 80, 0., 80.)
        # self.histosCumulative["h_cumulative_egPt_" + self.name] = ROOT.TH1F("h_cumulative_egPt_" + self.name, "EG Pt ("+self.name+"); Pt (GeV); Rate (Hz)", 80, 0., 80.)

        self.histos["h_dimuonPtSpread_" + self.name] = ROOT.TH1F("h_dimuonPtSpread_" + self.name, "Dimuon Pt Spread ("+self.name+"); Pt (GeV); NEvts", 80, 0., 80.)
        # self.histosCumulative["h_cumulative_dimuonPtSpread_" + self.name] = ROOT.TH1F("h_cumulative_dimuonPtSpread_" + self.name, "Dimuon Pt Spread ("+self.name+"); Pt (GeV); Rate (Hz)", 80, 0., 80.)

        self.histos["h_dimuonMass_" + self.name] = ROOT.TH1F("h_dimuonMass_" + self.name, "Dimuon Mass ("+self.name+"); Pt (GeV); NEvts", 120, 0., 120.)
        # self.histosCumulative["h_cumulative_dimuonMass_" + self.name] = ROOT.TH1F("h_cumulative_dimuonMass_" + self.name, "Dimuon Mass ("+self.name+"); Pt (GeV); Rate (Hz)", 80, 0., 80.)


        #self.histos["h_lumiSec_" + self.name] = ROOT.TH1F("h_lumiSec_" + self.name, "Lumi Section ("+self.name+"); Lumi Section ; NEvts", 10000000, 0., 10000000.)
        #self.histos["h_nBunches_" + self.name] = ROOT.TH1F("h_nBunches_" + self.name, "Lumi Section ("+self.name+"); Lumi Section ; NEvts", 10000000, 0., 10000000.)
    
    def __str__(self):
        return "Name: " + self.name + " \n Expression: " + self.expression 

    def fillHistograms(self, muonList, egList):
        #print self.expression
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

    def printHistograms(self, ouputFile, histoScale):
        ouputFile.cd()
        os.system("mkdir l1Plots_"+dataSetName+"/" + self.name)
        for histName, hist in self.histos.iteritems():
            hist.Write()
            hist.Draw('HIST')
            ROOT.gPad.SetLogy()
            ROOT.gPad.SaveAs("l1Plots_"+dataSetName+"/" + self.name + "/" + histName + ".png")
            # cumulative histo
            cumulativeHisto = hist.GetCumulative(ROOT.kFALSE, "_cumulative")
            cumulativeHisto.GetYaxis().SetTitle("Rate (Hz)")
            cumulativeHisto.Scale(histoScale)
            cumulativeHisto.Write()
            cumulativeHisto.Draw('HIST')
            ROOT.gPad.SetLogy()
            ROOT.gPad.SaveAs("l1Plots_"+dataSetName+"/" + self.name + "/" + histName + "_cumulative.png")



    # allevents = float(treeEvent.GetEntries() if nevents<0 else nevents)
    # print "allevents: ", allevents
    # bins_eg = []
    # for bin in range(h_RateVsegPt.GetNbinsX()):
    #     bins_eg.append(float(h_RateVsegPt.GetBinContent(bin+1)))
    # rates_eg = []
    # for i, bin in enumerate(bins_eg):
    #     rates_eg.append(total_rate * sum(bins_eg[i:])/ allevents)
    #     print "total_rate:",total_rate,"; ",bins_eg[i:]
    # for bin in range(cumulative_rateVsegPt.GetNbinsX()):
    #     cumulative_rateVsegPt.SetBinContent(bin+1, rates_eg[bin])
    # ROOT.gPad.SetLogy()
    # cumulative_rateVsegPt.Write()
    # cumulative_rateVsegPt.Draw('HIST')
    # ROOT.gPad.SaveAs('rate_egPt.pdf')



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
    countEvts = 0
    lumiMin = -1
    lumiMax = -1
    # nThresholds = 80;
    # EtMin = 0.;
    # EtMax = 20.;
    # lumiBinMax = 700


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
        lumiBlock = ev.lumi
        # nBunches = ev.bx
        

        # define objects
        ### Taus ###
        if verbose: print '\nevent: %d, nTaus: %d' %(ev.event, sim.nTaus)
        
        taus = []
        
        for i in range(sim.nTaus):
            taus.append(L1Tau(sim.tauEt[i], sim.tauEta[i], sim.tauPhi[i], sim.tauIso[i], sim.tauBx[i]))
        
        taus.sort(key=lambda x: x.et, reverse=True)
                
        for i, tau in enumerate(taus):
            if verbose: print '\ttau %d \t' %i, tau
        
        isotaus = [tau for tau in taus if tau.iso == 1 and abs(tau.eta) < 2.17 and tau.bx == 0]
        #############

        ### Egs ###
        if verbose: print '\nevent: %d, nEGs: %d' %(ev.event, sim.nEGs)
        
        egs = []
        
        for i in range(sim.nEGs):
            egs.append(L1Eg(sim.egEt[i], sim.egEta[i], sim.egPhi[i], sim.egIso[i], sim.egBx[i]))
        
        egs.sort(key=lambda x: x.et, reverse=True)
                
        for i, eg in enumerate(egs):
            if verbose: print '\teg %d \t' %i, eg
        
        isoegs = [eg for eg in egs if eg.iso == 1]
        #############

        ### Muons ###
        if verbose: print '\nevent: %d, nMuons: %d' %(ev.event, sim.nMuons)
        
        muons = []
        
        for i in range(sim.nMuons):
            muons.append(L1Muon(sim.muonEt[i], sim.muonEta[i], sim.muonPhi[i], sim.muonChg[i], sim.muonQual[i], sim.muonIso[i], sim.muonBx[i]))
        
        muons.sort(key=lambda x: x.et, reverse=True)

                
        for i, muon in enumerate(muons):
            if verbose: print '\tmuon %d \t' %i, muon
        
        isomuons = [muon for muon in muons if muon.iso == 1]
        #############


        countEvts+=1
        if(lumiMin < 0):
          lumiMin = lumiBlock 
        if(lumiMin >= 0 and lumiBlock < lumiMin) :
          lumiMin = lumiBlock

        if(lumiMax < 0):
          lumiMax = lumiBlock 
        if(lumiMax >= 0 and lumiBlock > lumiMax):
          lumiMax = lumiBlock

        for config in l1Configs: 
            config.fillHistograms(muons, egs)

    # end of events loop

    #  effTrigBitL1 = nPassedTrigBitL1/countEvts
    # float(effTrigBitL1)
    # print "Efficiency of TrigBit L1 :", float(effTrigBitL1)
    # #func_effTrigBitL1.SetParameter(0,float(effTrigBitL1))
    
    lumiLength = 23.31 #s
    deltaLumi = lumiMax - lumiMin
    Lum = 1 #10^33cms-2s-1
    lumiRef = 1 #10^33cms-2s-1 
    nBunches = 2592
    if nBunches < 0 :
      histoScale = (-1.*nBunches)/(deltalumi*23.31)  
    else:
       histoScale = 11246. #ZB per bunch in Hz
       histoScale /= countEvts # in Hz
       histoScale *= nBunches
       
    
    # histoScale = (1./(deltaLumi*lumiLength)*(Lum/lumiRef))
    for config in l1Configs:
        config.printHistograms(outfile, histoScale)

    #os.system("tar -zcvf l1Plots.tar.gz l1Plots/")

if __name__ == "__main__":
    cfgVars= {}
    execfile(sys.argv[2], cfgVars)

    #l1NtupleFiles = ['file:/uscmst1b_scratch/lpc1/3DayLifetime/ftorresd/L1Ntuples/L1Ntuple_%d.root' % i for i in range(1,500)]
    #l1NtupleFiles = ['root://xrootd.unl.edu//store/user/sfonseca/ZeroBias/L1Ntuple_ZeroBias_Run2016G-v1_RAW-all-v4_newxmlAlessio_v9/170221_202210/0000/L1Ntuple_%d.root' % i for i in range(1,500)]
    # l1NtupleFiles = ['root://cmseos.fnal.gov//store/user/sfonseca/ZeroBias/L1Ntuple_ZeroBias_Run2016G-v1_RAW-all-v4_newxmlAlessio_v9/170221_202210/0000/L1Ntuple_%d.root' % i for i in range(1,500)]
    l1NtupleFiles = cfgVars['l1NtupleFiles'] 
    # dataSetName = "ZeroBias"
    dataSetName = cfgVars['dataSetName']

    
### Setup L1 Seeds ###

    #l1DoubleMu(muonList):
    #l1OS(muonList):
    #l1QualityDoubleMu(muonList):
    #l1PtCutDoubleMu(ptCut, muonList):
    #l1PtCutDoubleMuAss(ptCutLeading, ptCutTrailing, muonList):
    #l1PtCutEG(ptCut, egList):
    #l1IsoEG(egs):

    # l1DoubleMuConfigs = []
    # for mupt in range(0,16):
    #     l1DoubleMuConfigs.append(l1Config("L1_DoubleMu"+str(mupt)+"", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu("+str(mupt)+".0, muonList)"))

    # l1DoubleMuOSConfigs = []
    # for mupt in range(0,16):
    #     l1DoubleMuOSConfigs.append(l1Config("L1_DoubleMu"+str(mupt)+"_OS", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu("+str(mupt)+".0, muonList)"))

    # l1DoubleMuEGConfigs = []
    # for mupt in range(0,16):
    #     for egpt in range(9,26):
    #         l1DoubleMuEGConfigs.append(l1Config("L1_DoubleMu"+str(mupt)+"_EG"+str(egpt), "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu("+str(mupt)+".0, muonList) and l1PtCutEG("+str(egpt)+", egList)"))

    # l1DoubleMuOSEGConfigs = []
    # for mupt in range(0,16):
    #     for egpt in range(9,26):
    #         l1DoubleMuOSEGConfigs.append(l1Config("L1_DoubleMu"+str(mupt)+"_OS_EG"+str(egpt), "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu("+str(mupt)+".0, muonList) and l1PtCutEG("+str(egpt)+", egList)"))


    # l1Configs = l1DoubleMuConfigs+l1DoubleMuOSConfigs+l1DoubleMuEGConfigs+l1DoubleMuOSEGConfigs
    # #l1Configs = l1DoubleMuConfigs
    # #eventLoop(l1NtupleFiles, l1Configs)

    l1ZeroBiasConfigs = []
    l1ZeroBiasConfigs.append(l1Config("L1_ZeroBias", "True"))

    l1RefConfigs = []
    l1RefConfigs.append(l1Config("L1_DoubleMuX", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(0.0, muonList)"))
    # l1RefConfigs.append(l1Config("L1_DoubleMu0", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(0.0, muonList)"))
    # l1RefConfigs.append(l1Config("L1_DoubleMu0_OS", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(0.0, muonList)"))

    l1DoubleMuConfigs = []
    # l1DoubleMuConfigs.append(l1Config("L1_DoubleMu6", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(6.0, muonList)"))
    # l1DoubleMuConfigs.append(l1Config("L1_DoubleMu7", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(7.0, muonList)"))
    # l1DoubleMuConfigs.append(l1Config("L1_DoubleMu8", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(8.0, muonList)"))

    l1DoubleMuOSConfigs = []
    l1DoubleMuOSConfigs.append(l1Config("L1_DoubleMuX_OS", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(0.0, muonList)"))
    # l1DoubleMuOSConfigs.append(l1Config("L1_DoubleMu6_OS", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(6.0, muonList)"))
    # l1DoubleMuOSConfigs.append(l1Config("L1_DoubleMu7_OS", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(7.0, muonList)"))
    # l1DoubleMuOSConfigs.append(l1Config("L1_DoubleMu8_OS", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(8.0, muonList)"))

    l1DoubleMuEGConfigs = []
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu6_EGX", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(6.0, muonList) and l1PtCutEG(0.0, egList)"))
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu7_IsoEGX", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(7.0, muonList) and l1PtCutIsoEG(0.0, egList)"))   
    # l1DoubleMuConfigs.append(l1Config("L1_DoubleMu6_EG10", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(6.0, muonList) and l1PtCutEG(10.0, egList)"))
    # l1DoubleMuConfigs.append(l1Config("L1_DoubleMu7_IsoEG10", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(7.0, muonList) and l1PtCutEG(10.0, egList) and l1IsoEG(egList)"))   
    # l1DoubleMuConfigs.append(l1Config("L1_DoubleMu8_EG5", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(8.0, muonList) and l1PtCutEG(5.0, egList)"))

    l1DoubleMuOSEGConfigs = []
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu6_OS_EGX", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(6.0, muonList) and l1PtCutEG(0.0, egList)"))
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu7_OS_IsoEGX", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(7.0, muonList) and l1PtCutIsoEG(0.0, egList)"))
    # l1DoubleMuConfigs.append(l1Config("L1_DoubleMu6_OS_EG10", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(6.0, muonList) and l1PtCutEG(10.0, egList)"))
    # l1DoubleMuConfigs.append(l1Config("L1_DoubleMu7_OS_IsoEG10", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(7.0, muonList) and l1PtCutEG(10.0, egList) and l1IsoEG(egList)"))
    # l1DoubleMuConfigs.append(l1Config("L1_DoubleMu8_OS_EG5", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMu(8.0, muonList) and l1PtCutEG(5.0, egList)"))

    l1DoubleMuAssConfigs = []
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu10_X", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMuAss(10.0, 0.0, muonList)"))
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu8_X", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMuAss(8.0, 0.0, muonList)"))
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu6_X", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMuAss(6.0, 0.0, muonList)"))
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu4_X", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMuAss(4.0, 0.0, muonList)"))


    l1DoubleMuAssOSConfigs = []
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu10_X_OS", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMuAss(10.0, 0.0, muonList)"))
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu8_X_OS", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMuAss(8.0, 0.0, muonList)"))
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu6_X_OS", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMuAss(6.0, 0.0, muonList)"))
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu4_X_OS", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMuAss(4.0, 0.0, muonList)"))

    l1DoubleMuAssEGConfigs = []
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu8_6_EGX", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMuAss(8.0, 6.0, muonList) and l1PtCutEG(0.0, egList)"))
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu6_4_EGX", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMuAss(6.0, 4.0, muonList) and l1PtCutEG(0.0, egList)"))
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu4_2_EGX", "l1DoubleMu(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMuAss(4.0, 2.0, muonList) and l1PtCutEG(0.0, egList)"))

    l1DoubleMuAssOSEGConfigs = []
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu8_6_OS_EGX", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMuAss(8.0, 6.0, muonList) and l1PtCutEG(0.0, egList)"))
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu6_4_OS_EGX", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMuAss(6.0, 4.0, muonList) and l1PtCutEG(0.0, egList)"))
    l1DoubleMuConfigs.append(l1Config("L1_DoubleMu4_2_OS_EGX", "l1DoubleMu(muonList) and l1OS(muonList) and l1QualityDoubleMu(muonList) and l1PtCutDoubleMuAss(4.0, 2.0, muonList) and l1PtCutEG(0.0, egList)"))


    l1Configs = l1ZeroBiasConfigs + l1RefConfigs + l1DoubleMuConfigs + l1DoubleMuOSConfigs + l1DoubleMuEGConfigs + l1DoubleMuOSEGConfigs + l1DoubleMuAssConfigs + l1DoubleMuAssOSConfigs + l1DoubleMuAssEGConfigs + l1DoubleMuAssOSEGConfigs
    #l1Configs = l1DoubleMuConfigs
    #eventLoop(l1NtupleFiles, l1Configs)
   
### (END) Setup L1 Seeds ###



    os.system("rm -rf l1Plots_"+dataSetName+"")
    os.system("mkdir l1Plots_"+dataSetName+"")

    nThreads = int(sys.argv[1])

    def split(a, n):
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n))

    l1ConfigsList = list(split(l1Configs, nThreads))
    #print l1ConfigsList

    threads = []
    for i in range(nThreads):
        threads.append(threading.Thread(target=eventLoop, args=(l1NtupleFiles, l1ConfigsList[i],"l1Plots_"+dataSetName+"/histograms_"+str(i)+".root",)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()
 
    os.system("tar -zcvf l1Plots_"+dataSetName+".tar.gz l1Plots_"+dataSetName+"/")
    print "\nl1Plots_"+dataSetName+".tar.gz created\n"





 