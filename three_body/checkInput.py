#! /usr/bin/env python

import numpy as np
import argparse

import ROOT 
ROOT.PyConfig.IgnoreCommandLineOptions = True

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Check that the input file looks OK')

    parser.add_argument('infile',
                        help='File name for reading events.')


    args = parser.parse_args()

    # Load the data
    npfile = np.load(args.infile)
    
    inputs = npfile['inputs']
    outputs = npfile['outputs']
        
    minOutput = np.amin(outputs,axis=0)
    maxOutput = np.amax(outputs,axis=0)
    minInput = np.amin(inputs,axis=0)
    maxInput = np.amax(inputs,axis=0)
   
    # Let's define a histogram for each output in the target.
    inputHists = []
    outputHists = []

    for itarg in range(inputs.shape[1]):
        hist = ROOT.TH1F('input{}Hist'.format(itarg),
                    'I_{{{0}}}'.format(itarg),
                    100,minInput[itarg],maxInput[itarg])
        inputHists.append(hist)

    for itarg in range(outputs.shape[1]):
        hist = ROOT.TH1F('output{}Hist'.format(itarg),
                    'O_{{{0}}}'.format(itarg),
                    100,minOutput[itarg],maxOutput[itarg])
        outputHists.append(hist)

    # Filling the old fashioned way...
    for irow in range(inputs.shape[0]):
        for ivar in range(inputs.shape[1]):
            inputHists[ivar].Fill(inputs[irow][ivar])
    for irow in range(outputs.shape[0]):
        for ivar in range(outputs.shape[1]):
            outputHists[ivar].Fill(outputs[irow][ivar])
            
    # Finally, write out these diffHists to a file
    histFile = args.infile.replace('.npz','_check.root')
    
    rootFile = ROOT.TFile.Open(histFile,'RECREATE')
    rootFile.cd()
    for hist in inputHists:
        hist.Write()
    for hist in outputHists:
        hist.Write()

    rootFile.Close()

    
