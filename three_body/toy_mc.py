#! /usr/bin/env python

import random, math
import ROOT 
ROOT.PyConfig.IgnoreCommandLineOptions = True

import argparse
import json

import numpy as np

# Useful constants
twoPi = 2*math.pi
beamE = 6500
xLambda = 50.
wMassConst = 81.
wWidthConst = 2.085
topMassConst = 172.5
topWidthConst = 1.41

maxTries = 500

# Get our ROOT random number generator set up
ROOT.gRandom.SetSeed(0)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate toy three body (e.g. top quark) decay')
    parser.add_argument('nGen', metavar='N', type=int,
                        help='Number of events to generate.')
    parser.add_argument('outfile',
                        help='File name for saving output.  Will be a compressed numpy file (.npz).  Extension will be added for you if ommitted.')
    parser.add_argument('-r','--random-mass', action='store_true',
                        help='Generate the masses randomly instead of assuming top quark decay.')
    parser.add_argument('-c','--cartesian', action='store_true',
                        help='Outputs are px, py, pz, E instead of pt, eta, phi, and mass')
    
    
    args = parser.parse_args()

    # Assume A->B + C, C->D+E
    # Inputs are always B, D, E, where D is the decay product of C with higher pt.
    inputs = np.empty([args.nGen, 9], dtype='float32')

    # Outputs are either pt, eta, phi, mass or px, py, pz, E depending on arguments
    outputs = np.empty([args.nGen, 4], dtype='float32')

    for iEvt in xrange(args.nGen):

        if iEvt%1000 == 0:
            print 'Generating event {}'.format(iEvt)

        if args.random_mass:
            topMass = random.uniform(0,300)
            wMass = random.uniform(topMass*0.25,topMass*0.75)
        else:
            wMass = ROOT.gRandom.BreitWigner(wMassConst,wWidthConst)
            iTry = 0
            # Guard against a silly big (or small) W mass
            while abs(wMass-wMassConst)/wWidthConst > 20:
                iTry += 1
                if iTry > maxTries:
                    raise RuntimeError('Exhausted {} tries in generating random number'.format(maxTries))
                wMass = ROOT.gRandom.BreitWigner(wMassConst,wWidthConst)

            topMass = ROOT.gRandom.BreitWigner(topMassConst,topWidthConst)
            iTry = 0
            # Again guard against silly big or small top masses
            while topMass < 1.1*wMass or topMass > 0.05*beamE:
                iTry += 1
                if iTry > maxTries:
                    message = 'Exhausted {} tries in generating random number\n'.format(maxTries)
                    message += ' wMass = {:.2f}'.format(topMass)
                    raise RuntimeError(message)
                topMass = ROOT.gRandom.BreitWigner(topMassConst,topWidthConst)                

        halfWMass = wMass/2
        pFromTopDecay = (topMass**2-wMass**2)/(2*topMass)
        wEnergyFromTop = math.sqrt(wMass**2+pFromTopDecay**2)
        fourTopMassSq = 4*topMass**2

        # Hadronic W (at rest)
        phi = random.uniform(0,twoPi)
        theta = random.uniform(0,math.pi)
        jet1FromW = ROOT.TLorentzVector(0,0,halfWMass,halfWMass)
        jet1FromW.SetTheta(theta)
        jet1FromW.SetPhi(phi)
        jet2FromW = ROOT.TLorentzVector(0,0,halfWMass,halfWMass)
        jet2FromW.SetTheta(theta+math.pi)
        jet2FromW.SetPhi(phi+math.pi)
        
        # Now make the W and b from a top quark decay (assume top quark at rest)
        phi = random.uniform(0,twoPi)
        theta = random.uniform(0,math.pi)
        bFromHadTop = ROOT.TLorentzVector(0,0,pFromTopDecay,pFromTopDecay)
        bFromHadTop.SetTheta(theta)
        bFromHadTop.SetPhi(phi)
        wFromHadTop = ROOT.TLorentzVector(0,0,pFromTopDecay,wEnergyFromTop)
        wFromHadTop.SetTheta(theta+math.pi)
        wFromHadTop.SetPhi(phi+math.pi)

        # Now boost the W decay products based on the W boost
        jet1FromW.Boost(wFromHadTop.BoostVector())
        jet2FromW.Boost(wFromHadTop.BoostVector())

        # OK, now I just need to generate the ttbar pair, first I need to
        # figure out how much available energy we have in the CM.

        # Initialize some dummy values just to get us into the while loop
        x1 = 9e20
        x2 = 9e20
        protonVect1 = ROOT.TLorentzVector()
        protonVect2 = ROOT.TLorentzVector()
        cmMass = 0

        # Keep picking random values until we get something reasonable
        iTry = 0
        while x1 > 1 or x2 > 1 or cmMass < 2*topMass or cmMass**2 < fourTopMassSq:

            iTry += 1
            if iTry > maxTries:
                message = 'Exhausted {} tries in generating random number\n'.format(maxTries)
                message += '  topMass = {:.2f}'.format(topMass)
                raise RuntimeError(message)

            x1 = random.expovariate(xLambda)
            x2 = random.expovariate(xLambda)

            protonVect1.SetPxPyPzE(0.,0.,x1*beamE,x1*beamE)
            protonVect2.SetPxPyPzE(0.,0.,-x2*beamE,x2*beamE)

            cmVect = protonVect1+protonVect2
            cmMass = cmVect.M()

        # Now generate a ttbar in the CM rest frame
        
        pFromCM = math.sqrt(cmMass**2-fourTopMassSq)/2
        phi = random.uniform(0,twoPi)
        theta = random.uniform(0,math.pi)
                
        # Set hadronic top vector
        hadTop = ROOT.TLorentzVector(0,0,pFromCM,cmMass/2)
        hadTop.SetTheta(theta+math.pi)
        hadTop.SetPhi(phi+math.pi)

        # Boost the lepTopDecayProducts
        jet1FromW.Boost(hadTop.BoostVector())
        jet2FromW.Boost(hadTop.BoostVector())
        bFromHadTop.Boost(hadTop.BoostVector())

        # Finally, boost everything into the lab frame
        jet1FromW.Boost(cmVect.BoostVector())
        jet2FromW.Boost(cmVect.BoostVector())
        bFromHadTop.Boost(cmVect.BoostVector())
        hadTop.Boost(cmVect.BoostVector())

        # Now let's store the input and outputs
        inputs[iEvt,0:3] = [bFromHadTop.Pt(), bFromHadTop.Eta(), bFromHadTop.Phi()]

        if jet1FromW.Pt() > jet2FromW.Pt():
            inputs[iEvt,3:6] = [jet1FromW.Pt(),jet1FromW.Eta(),jet1FromW.Phi()]
            inputs[iEvt,6:9] = [jet2FromW.Pt(),jet2FromW.Eta(),jet2FromW.Phi()]
        else :
            inputs[iEvt,6:9] = [jet1FromW.Pt(),jet1FromW.Eta(),jet1FromW.Phi()]
            inputs[iEvt,3:6] = [jet2FromW.Pt(),jet2FromW.Eta(),jet2FromW.Phi()]
            
        if args.cartesian:
            outputs[iEvt,0:4] = [hadTop.Px(),hadTop.Py(), hadTop.Pz(),hadTop.E()]
        else:
            outputs[iEvt,0:4] = [hadTop.Pt(),hadTop.Eta(), hadTop.Phi(),hadTop.M()]

        if (bFromHadTop.Pt() > beamE or
            jet1FromW.Pt() > beamE or
            jet2FromW.Pt() > beamE):

            print '-This looks wrong!!!----------------------'


            print 'bFromHadTop: {:.2f},{:.2f},{:.2f},{:.2f}'.format(bFromHadTop.Pt(),
                                                                    bFromHadTop.Eta(),
                                                                    bFromHadTop.Phi(),
                                                                    bFromHadTop.M())

            print 'jet1FromW: {:.2f},{:.2f},{:.2f},{:.2f}'.format(jet1FromW.Pt(),
                                                                  jet1FromW.Eta(),
                                                                  jet1FromW.Phi(),
                                                                  jet1FromW.M())

            print 'jet2FromW: {:.2f},{:.2f},{:.2f},{:.2f}'.format(jet2FromW.Pt(),
                                                                  jet2FromW.Eta(),
                                                                  jet2FromW.Phi(),
                                                                  jet2FromW.M())


            print 'hadTop: {:.2f},{:.2f},{:.2f},{:.2f}'.format(hadTop.Pt(),
                                                               hadTop.Eta(),
                                                               hadTop.Phi(),
                                                               hadTop.M())
            topCheck = bFromHadTop + jet1FromW + jet2FromW
            
            print 'topCheck: {:.2f},{:.2f},{:.2f},{:.2f}'.format(topCheck.Pt(),
                                                                 topCheck.Eta(),
                                                                 topCheck.Phi(),
                                                                 topCheck.M())
            
            print 'topMass = {:.2f}'.format(topMass)
            print 'wMass = {:.2f}'.format(wMass)
            print 'x1 = {:.2f}'.format(x1)
            print 'x2 = {:.2f}'.format(x2)
            print '----------------------------------------'
            print ''
            raise ValueError('Too much energy!')


    # Check whether outfile has the right extension.  Also, mark whether its PtEtaPhiM or PxPyPzE
    outName = args.outfile.rsplit('.npz',1)[0]
    if args.cartesian:
        outName += '_PxPyPzE.npz'
    else:
        outName += '_PtEtaPhiM.npz'


    np.savez_compressed(outName,inputs=inputs,outputs=outputs)

    print 'Done!'

