#! /usr/bin/env python

import random, math
import ROOT
from root_numpy import root2array, tree2array, testdata


ROOT.PyConfig.IgnoreCommandLineOptions = True

import argparse
import json

import numpy as np

def tree_to_array(nEvts, intree, category):
    arr1 = tree2array(intree,branches=['nonTop_lepChild.obj.pt()','nonTop_lepChild.obj.eta()','nonTop_lepChild.obj.phi()',
                                         'leptop_lep.obj.pt()','leptop_lep.obj.eta()','leptop_lep.obj.phi()',
                                         'leptop_b.obj.pt()','leptop_b.obj.eta()','leptop_b.obj.phi()',
                                         'hadtop_b.obj.pt()','hadtop_b.obj.eta()','hadtop_b.obj.phi()',
                                         'hadtop_w1.obj.pt()','hadtop_w1.obj.eta()','hadtop_w1.obj.phi()',
                                         'hadtop_w2.obj.pt()','hadtop_w2.obj.eta()','hadtop_w2.obj.phi()',
                                         'gen_leps[0].obj.pt()','gen_leps[0].obj.eta()','gen_leps[0].obj.phi()',
                                         'gen_leps[1].obj.pt()','gen_leps[1].obj.eta()','gen_leps[1].obj.phi()',
                                         'gen_jets[0].obj.pt()','gen_jets[0].obj.eta()','gen_jets[0].obj.phi()',
                                         'gen_jets[1].obj.pt()','gen_jets[1].obj.eta()','gen_jets[1].obj.phi()',
                                         'gen_jets[2].obj.pt()','gen_jets[2].obj.eta()','gen_jets[2].obj.phi()',
                                         'gen_jets[3].obj.pt()','gen_jets[3].obj.eta()','gen_jets[3].obj.phi()'],                        
                        selection='nonTop_lepChild.obj.pt()*leptop_lep.obj.pt()*leptop_b.obj.pt()*hadtop_b.obj.pt()*hadtop_w1.obj.pt()*hadtop_w2.obj.pt() > 0.',
                        start=0,stop=nEvts,step=1)

    #set object types to floats, may not be necessary...
    # arr1 = np.asarray(arr1, dtype=[('nonTop_lepChild.obj.pt()', 'float32'), ('nonTop_lepChild.obj.eta()', 'float32'), ('nonTop_lepChild.obj.phi()', 'float32'),
    #                                ('leptop_lep.obj.pt()', 'float32'), ('leptop_lep.obj.eta()', 'float32'), ('leptop_lep.obj.phi()', 'float32'),
    #                                ('leptop_b.obj.pt()', 'float32'), ('leptop_b.obj.eta()', 'float32'), ('leptop_b.obj.phi()', 'float32'),
    #                                ('hadtop_b.obj.pt()', 'float32'), ('hadtop_b.obj.eta()', 'float32'), ('hadtop_b.obj.phi()', 'float32'),
    #                                ('hadtop_w1.obj.pt()', 'float32'), ('hadtop_w1.obj.eta()', 'float32'), ('hadtop_w1.obj.phi()', 'float32'),
    #                                ('hadtop_w2.obj.pt()', 'float32'), ('hadtop_w2.obj.eta()', 'float32'), ('hadtop_w2.obj.phi()', 'float32'),
    #                                ('gen_leps[0].obj.pt()', 'float32'), ('gen_leps[0].obj.eta()', 'float32'), ('gen_leps[0].obj.phi()', 'float32'),
    #                                ('gen_leps[1].obj.pt()', 'float32'), ('gen_leps[1].obj.eta()', 'float32'), ('gen_leps[1].obj.phi()', 'float32'),
    #                                ('gen_jets[0].obj.pt()', 'float32'), ('gen_jets[0].obj.eta()', 'float32'), ('gen_jets[0].obj.phi()', 'float32'),
    #                                ('gen_jets[1].obj.pt()', 'float32'), ('gen_jets[1].obj.eta()', 'float32'), ('gen_jets[1].obj.phi()', 'float32'),
    #                                ('gen_jets[2].obj.pt()', 'float32'), ('gen_jets[2].obj.eta()', 'float32'), ('gen_jets[2].obj.phi()', 'float32'),
    #                                ('gen_jets[3].obj.pt()', 'float32'), ('gen_jets[3].obj.eta()', 'float32'), ('gen_jets[3].obj.phi()', 'float32')])

    arr1 = [x for xs in arr1 for x in xs]
    arr1 = np.array(arr1)
    arr1.shape = (-1,36)
    arr2 = np.empty([len(arr1), 1], dtype='int'); arr2.fill(category)
    arr2.shape = (-1,1)
    return arr1, arr2

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Convert root files containing TTree to numpy array in .npz format')
    parser.add_argument('nEvt', metavar='N', type=int, default=-1, nargs='?',
                        help='Number of events to generate.')
    parser.add_argument('outfile', default='outfile.npz', nargs='?',
                        help='File name for saving output.  Will be a compressed numpy file (.npz).  Extension will be added for you if ommitted')

    args = parser.parse_args()

    signal_file = ROOT.TFile('/scratch365/cmuelle2/bdt_test/dec5_DLv0/tth_powheg_genFilter2lss_training_loose_tree2.root')
    signal_tree = signal_file.Get('ss2l_tree')
    background_file = ROOT.TFile('/scratch365/cmuelle2/bdt_test/dec5_DLv0/ttw_mg5_genFilter2lss_training_loose_tree14.root')
    background_tree = background_file.Get('ss2l_tree')

    sig_in, sig_out = tree_to_array(args.nEvt, signal_tree, 1)
    bkg_in, bkg_out = tree_to_array(args.nEvt, background_tree, 0)
    
    inputs = np.concatenate((sig_in,bkg_in))
    outputs = np.concatenate((sig_out,bkg_out))
    np.savez_compressed(args.outfile,inputs=inputs,outputs=outputs)

    print 'Done!'
