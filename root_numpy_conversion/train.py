#! /usr/bin/env python

import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.optimizers import SGD
from keras.regularizers import l1, l2, l1_l2
from keras.callbacks import EarlyStopping, ModelCheckpoint
import argparse, tarfile, os, tempfile, shutil

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Train ANN auto-encoder.')
    parser.add_argument('infile',
                        help='File name for reading events.')

    parser.add_argument('-o','--out', dest='outbase', metavar='OUTBASE',
                        default='model',
                        help='File name base (no extension) ' +
                        'for saving model structure and weights (two separate ' +
                        'files).')
    
    parser.add_argument('-N','--num-epochs',
                        default=10, type=int,
                        help='Number of epochs')

    parser.add_argument('-b','--batch-size',
                        default=256, type=int,
                        help='Minibatch size')

    parser.add_argument('-l','--layer', dest='layers',
                        metavar = 'NH', action='append',
                        type=int,
                        help='Specify a layer with %(metavar)s hidden layers.  ' +
                        'Multiple layers can be specified')

    parser.add_argument('--reg-type', choices = ['l1','l2','l1_l2'],
                        help='Type of regularization to apply')

    parser.add_argument('--reg-penalty',type=float, default=0.001,
                        help='Regularization penalty')

    def restricted_float(x):
        x = float(x)
        if x < 0.0 or x > 1.0:
            raise argparse.ArgumentTypeError("%r not in range [0.0, 1.0]"%(x,))
        return x

    parser.add_argument('--train-fraction',type=restricted_float,
                        default = 0.9,
                        help='Fraction (between 0. and 1.) of the examples in '+
                        'the input file to use for training.  The rest is used '+
                        'for testing.')

    args = parser.parse_args()

    # Keep track of all the output files generate so they can be
    # stuffed into a tar file.  (Yes, a tarfile.  I'm old, OK?)
    outFileList = []
    tmpDirName = tempfile.mkdtemp()

    # Load the data
    npfile = np.load(args.infile)

    inputs = npfile['inputs']
    outputs = npfile['outputs']

    # Standardize the input so that it has mean 0 and std dev. of 1.  This helps
    # tremendously with training performance.
    print inputs.shape
    print int(inputs.shape[0]*args.train_fraction)
    print len(inputs)
    inputMeans = inputs[0:int(inputs.shape[0]*args.train_fraction),:].mean(axis=0)
    inputStdDevs = inputs[0:int(inputs.shape[0]*args.train_fraction),:].std(axis=0)
    inputs = (inputs-inputMeans)/inputStdDevs
    outputMeans = outputs[0:int(outputs.shape[0]*args.train_fraction)].mean(axis=0)
    outputStdDevs = outputs[0:int(outputs.shape[0]*args.train_fraction)].std(axis=0)
    outputs = (outputs-outputMeans)/outputStdDevs

    npFileName = 'std.npz'
    outFileList.append(npFileName)
    np.savez_compressed(os.path.join(tmpDirName,npFileName),
                        inputMeans=inputMeans,
                        inputStdDevs=inputStdDevs,
                        outputMeans=outputMeans,
                        outputStdDevs=outputStdDevs)

    # Initialize the appropriate regularizer (if any)
    reg = None
    if args.reg_type == "l1":
        reg = l1(args.reg_penalty)
    elif args.reg_type == "l2":
        reg = l1(args.reg_penalty)
    elif args.reg_type == "l1_l2":
        reg = l1_l2(args.reg_penalty)

    # Check the requested layers.  If none, make the simplest
    # possible: 1 layer with number of nodes equal to the size of the
    # input.
    if hasattr(args,'layers') and args.layers != None:
        layers = args.layers
    else:
        layers = [inputs.shape[1]]

    
    # Build a model
    model = Sequential()
    print layers
    # First layer
    model.add(Dense(1,input_dim=36))
    model.add(Activation('linear'))

    model.compile(loss='mse',
                  optimizer='adam')

    # Add callbacks
    filepath = 'model.h5'
    outFileList.append(filepath)
    checkpoint = ModelCheckpoint(os.path.join(tmpDirName,filepath), monitor = 'val_loss', mode = 'min', save_best_only = True)
    model.summary()
    
    hist = model.fit(inputs, outputs, validation_split=(1-args.train_fraction),
              epochs=args.num_epochs, batch_size=args.batch_size, verbose=2, callbacks=[checkpoint])
 
    print 'Tarring outfiles...'
    outfile_name = '{}_N{}_b{}_l{}_frac{:f}'.format(args.outbase,
                                                  args.num_epochs,
                                                  args.batch_size,
                                                  '_'.join([str(l) for l in layers]),
                                                  args.train_fraction)
    if hasattr(args,'reg_type') and args.reg_type != None:
        outfile_name += ('{}{:f}'.format(args.reg_type,args.reg_penalty))

    outfile_name += '.tgz'                                               
                                                          
    with tarfile.open(outfile_name,'w:gz') as tar:
        for f in outFileList:
            tar.add(os.path.join(tmpDirName,f),f)

        shutil.rmtree(tmpDirName)

    print 'Done.'

