#! /usr/bin/env python

import numpy as np
from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Input, concatenate
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

    parser.add_argument('-s','--shared-layer', dest='shared_layers',
                        metavar = 'NSH', action='append',
                        type=int,
                        help='Specify a layer with %(metavar)s hidden layers for shared network.  ')

    parser.add_argument('-l','--layer', dest='layers',
                        metavar = 'NH', action='append',
                        type=int,
                        help='Specify a layer with %(metavar)s hidden layers for merged network.  ')

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

    inputMeans = inputs[0:int(inputs.shape[0]*args.train_fraction),:].mean(axis=0)
    inputStdDevs = inputs[0:int(inputs.shape[0]*args.train_fraction),:].std(axis=0)
    inputs = (inputs-inputMeans)/inputStdDevs

    outputMeans = outputs[0:int(outputs.shape[0]*args.train_fraction),:].mean(axis=0)
    outputStdDevs = outputs[0:int(outputs.shape[0]*args.train_fraction),:].std(axis=0)
    outputs = (outputs-outputMeans)/outputStdDevs

    npFileName = 'std.npz'
    outFileList.append(npFileName)
    np.savez_compressed(os.path.join(tmpDirName,npFileName),
                        inputMeans=inputMeans,
                        inputStdDevs=inputStdDevs,
                        outputMeans=outputMeans,
                        outputStdDevs=outputStdDevs,
                        inputs=inputs,
                        outputs=outputs)

    # Initialize the appropriate regularizer (if any)
    reg = None
    if args.reg_type == "l1":
        reg = l1(args.reg_penalty)
    elif args.reg_type == "l2":
        reg = l1(args.reg_penalty)
    elif args.reg_type == "l1_l2":
        reg = l1_l2(args.reg_penalty)

    inputA = inputs[:,0:3]
    inputB = inputs[:,3:6]

    # Check the requested layers.  If none, make the simplest
    # possible: 1 layer with number of nodes equal to the size of the
    # input.
    if hasattr(args,'shared_layers') and args.shared_layers != None:
        layers = args.shared_layers
    else:
        layers = [inputA.shape[1]]

    # Build a model
    shared_model = Sequential()

    # First layer
    shared_model.add(Dense(layers[0],
                    input_dim=inputA.shape[1],
                    kernel_regularizer = reg))
    shared_model.add(Activation('relu'))

    for l in layers[1:]:
        shared_model.add(Dense(l,kernel_regularizer = reg))
        shared_model.add(Activation('relu'))

    input_layerA = Input(shape=(inputA.shape[1],))
    input_layerB = Input(shape=(inputB.shape[1],))
    
    encodedA = shared_model(input_layerA)
    encodedB = shared_model(input_layerB)

    merged_vector = concatenate([encodedA, encodedB])

    # Now figure out how many layers to put into the merged network
    # If nothing is specified, assume one layer with nodes equal to the total number of inputs
    if hasattr(args,'layers') and args.layers != None:
        layers = args.layers
    else:
        layers = [inputs.shape[1]]

    # First layer
    new_layer = Dense(layers[0], activation='relu', kernel_regularizer = reg)(merged_vector)

    for l in layers[1:]:
        new_layer = Dense(layers[0], activation='relu', kernel_regularizer = reg)(new_layer)

    output_layer = Dense(outputs.shape[1],activation='linear')(new_layer)

    model = Model(inputs=[input_layerA, input_layerB], outputs=output_layer)

    model.compile(loss='mse',
                  optimizer='adam')

    
    filepath = 'model.h5'
    outFileList.append(filepath)
    checkpoint = ModelCheckpoint(os.path.join(tmpDirName,filepath), monitor = 'val_loss', mode = 'min', save_best_only = True)
    model.summary()    
    print 'Saving model structure and parameters:'

    hist = model.fit([inputA, inputB], outputs, validation_split=(1-args.train_fraction),
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

