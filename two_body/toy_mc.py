#! /usr/bin/env python

import random, math
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

import argparse
import json

import numpy as np

# Useful constants
twoPi = 2*math.pi

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate toy two-body decay MC')
    parser.add_argument('nGen', metavar='N', type=int,
                        help='Number of events to generate.')
    parser.add_argument('outfile',
                        help='File name for saving output.  Will be a compressed numpy file (.npz).  Extension will be added for you if ommitted.')

    parser.add_argument('-c','--cartesian', action='store_true',
                        help='Outputs are px, py, pz, E instead of pt, eta, phi, and mass')

    args = parser.parse_args()

    # Inputs are always pt, eta, and phi of first vector and then second.
    # Vectors are ordered by pt, so highest pt is always first.
    inputs = np.empty([args.nGen, 6], dtype='float32')

    # Either pt, eta, phi, and mass of the original particle, or px, py, pz and E,
    # depending on whether "-c" is used.
    outputs = np.empty([args.nGen, 4], dtype='float32')

    for iEvt in xrange(args.nGen):

        if iEvt%1000 == 0:
            print 'Generating event {}'.format(iEvt)

        # Make a particle X
        xMass = random.uniform(0,500)
        xPt = random.uniform(0,300)
        xPhi = random.uniform(0,twoPi)
        xEta = random.uniform(-2.5,2.5)

        #Start with a null vector and then set pt, eta, phi, and mass
        xVect = ROOT.TLorentzVector(0,0,0,0)
        xVect.SetPtEtaPhiM(xPt,xEta,xPhi,xMass)

        # Decay products in rest from of the particle
        phi = random.uniform(0,twoPi)
        theta = random.uniform(0,math.pi)
        decayA = ROOT.TLorentzVector(0,0,xMass/2,xMass/2)
        decayA.SetTheta(theta)
        decayA.SetPhi(phi)
        decayB = ROOT.TLorentzVector(0,0,xMass/2,xMass/2)
        decayB.SetTheta(theta+math.pi)
        decayB.SetPhi(phi+math.pi)

        #Now boost these decay products into lab frame
        
        # Now boost the W decay products based on the W boost
        decayA.Boost(xVect.BoostVector())
        decayB.Boost(xVect.BoostVector())

        if decayA.Pt() > decayB.Pt():
            inputs[iEvt,0:3] = [decayA.Pt(),decayA.Eta(), decayA.Phi()]
            inputs[iEvt,3:6] = [decayB.Pt(),decayB.Eta(), decayB.Phi()]
        else:
            inputs[iEvt,3:6] = [decayA.Pt(),decayA.Eta(), decayA.Phi()]
            inputs[iEvt,0:3] = [decayB.Pt(),decayB.Eta(), decayB.Phi()]

        if args.cartesian:
            outputs[iEvt,0:4] = [xVect.Px(),xVect.Py(), xVect.Pz(),xVect.E()]
        else:
            outputs[iEvt,0:4] = [xVect.Pt(),xVect.Eta(), xVect.Phi(),xVect.M()]


    # Check whether outfile has the right extension.  Also, mark whether its PtEtaPhiM or PxPyPzE
    outName = args.outfile.rsplit('.npz',1)[0]
    if args.cartesian:
        outName += '_PxPyPzE.npz'
    else:
        outName += '_PtEtaPhiM.npz'

    np.savez_compressed(outName,inputs=inputs,outputs=outputs)

    print 'Done!'
