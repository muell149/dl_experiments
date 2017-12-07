#! /usr/bin/env python

import numpy as np
from keras.models import load_model
import argparse, tarfile, os, tempfile, shutil

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Validate ANN auto-encoder')

    parser.add_argument('model',
                        help='Model tarfile')

    parser.add_argument('infile',
                        help='File name for reading events.')


    args = parser.parse_args()

    # Keep ROOT from intercepting the command line args...
    from ROOT import TH1F, TH2F, TProfile, TFile

    # Untar the model files into a tmp directory
    tempDir = tempfile.mkdtemp()
    tar = tarfile.open(args.model)
    tar.extractall(tempDir)
    tar.close()

    npfile = np.load(os.path.join(tempDir,'std.npz'))
    inputMeans = npfile['inputMeans']
    inputStdDevs = npfile['inputStdDevs']
    outputMeans = npfile['outputMeans']
    outputStdDevs = npfile['outputStdDevs']

    model = load_model(os.path.join(tempDir,'model.h5'))

    shutil.rmtree(tempDir)

    # Load the data
    npfile = np.load(args.infile)

    inputs = npfile['inputs']
    target = npfile['outputs']
   
    # Standardize the inputs.  We'll unstandardize the output to
    # compare to the target
    inputs = (inputs-inputMeans)/inputStdDevs
        
    # Now, let's spin through our validation dataset and see how the
    # model outputs compare to the target.

    # First, get the predictions:
    output = model.predict(inputs, batch_size=256)

    # Unscale the outputs
    output = output*outputStdDevs+outputMeans

    # Can Numpy do this?  Calculate the differences for every element
    # in one line!
    diff = target-output
    minDiff = np.amin(diff,axis=0)
    maxDiff = np.amax(diff,axis=0)
    stdDiff = np.std(diff,axis=0)
    meanDiff = np.mean(diff,axis=0)
    minTarget = np.amin(target,axis=0)
    maxTarget = np.amax(target,axis=0)
    minOutput = np.amin(output,axis=0)
    maxOutput = np.amax(output,axis=0)

    print stdDiff
    

    # Let's define a histogram for each output in the target.
    diffHists = []
    vsHists = []
    diffProf = []
    for itarg in range(target.shape[1]):
        hist = TH1F('diff{}'.format(itarg),
                    'T_{{{0}}}-O_{{{0}}}'.format(itarg),
                    100,meanDiff[itarg]-3*stdDiff[itarg],meanDiff[itarg]+3*stdDiff[itarg])
        diffHists.append(hist)
        hist = TH2F('vs{}'.format(itarg),
                    'O_{{{0}}} vs T_{{{0}}}'.format(itarg),
                    400,minTarget[itarg],maxTarget[itarg],
                    400,minOutput[itarg],maxOutput[itarg])
        vsHists.append(hist)
        hist = TProfile('prof{}'.format(itarg),
                    'Prof(O_{{{0}}}) vs T_{{{0}}}'.format(itarg),
                    400,minTarget[itarg],maxTarget[itarg])
        diffProf.append(hist)


    # Filling the old fashioned way...
    for irow in range(diff.shape[0]):
        for ivar in range(diff.shape[1]):
            diffHists[ivar].Fill(diff[irow][ivar])
            vsHists[ivar].Fill(target[irow][ivar],output[irow][ivar])
            diffProf[ivar].Fill(target[irow][ivar],diff[irow][ivar])
            
    # Finally, write out these diffHists to a file
    histFile = args.model.replace('.tgz','.root')
    
    rootFile = TFile.Open(histFile,'RECREATE')
    rootFile.cd()
    for hist in diffHists:
        hist.Write()
    for hist in vsHists:
        hist.Write()
    for hist in diffProf:
        hist.Write()

    rootFile.Close()

    
