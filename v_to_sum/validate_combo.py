#! /usr/bin/env python

import numpy as np
from keras.models import load_model
import argparse, tarfile, os, tempfile, shutil

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Validate ANN auto-encoder')

    parser.add_argument('model2',
                        help='Squared model tarfile')
    parser.add_argument('modelAdd',
                        help='Addition model tarfile')
    parser.add_argument('infile',
                        help='File name for reading events.')


    args = parser.parse_args()

    # Keep ROOT from intercepting the command line args...
    from ROOT import TH1F, TH2F, TProfile, TFile

    # Untar the squared model files into a tmp directory
    tempDir2 = tempfile.mkdtemp()
    tar = tarfile.open(args.model2)
    tar.extractall(tempDir2)
    tar.close()

    # Untar the sum model files into a temp directory
    tempDirAdd = tempfile.mkdtemp()
    tar = tarfile.open(args.modelAdd)
    tar.extractall(tempDirAdd)
    tar.close()

    # Unload data and models
    npfile2 = np.load(os.path.join(tempDir2,'std.npz'))
    inputMeans = npfile2['inputMeans']
    inputStdDevs = npfile2['inputStdDevs']
    
    npfileAdd = np.load(os.path.join(tempDirAdd,'std.npz'))
    outputMeans = npfileAdd['outputMeans']
    outputStdDevs = npfileAdd['outputStdDevs']

    model2 = load_model(os.path.join(tempDir2,'model.h5'))
    modelAdd = load_model(os.path.join(tempDirAdd,'model.h5'))

    shutil.rmtree(tempDir2)

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
    output2 = model2.predict(inputs, batch_size=256)
    outputAdd = modelAdd.predict(output2, batch_size=256)

    # Unscale the outputs
    output = outputAdd*outputStdDevs+outputMeans
    
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
    histFile = args.modelAdd.replace('.tgz','.root')
    
    rootFile = TFile.Open(histFile,'RECREATE')
    rootFile.cd()
    for hist in diffHists:
        hist.Write()
    for hist in vsHists:
        hist.Write()
    for hist in diffProf:
        hist.Write()

    rootFile.Close()

    
