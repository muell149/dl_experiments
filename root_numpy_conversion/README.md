# Converting ROOT trees to numpy array (.npz) files

Convert ROOT TTrees into numpy arrays for NN training. 

## Convert 

This script reads in the signal and background ROOT files and saves them as a single .npz file. Note the convention of '1' for signal
and '0' for background. This script should be run on earth after installing pip, root_numpy.

Install pip from your home area on earth:

```
wget -O - https://bootstrap.pypa.io/get-pip.py|python - --user
```

This installs pip in your ~/.local directory. In order to access these executables, add them to your path with:

```
export PATH=$HOME/.local/bin:$PATH
``` 

Install numpy:

```
pip install --user root_numpy
```

Now you're ready to convert some ROOT files into npz files. Look inside root_to_npz.py adjust which files are used and the name of
the TTree:


```
./root_to_npz.py -1 training.npz
```

## Train NN

This script trains the NN and saves the model for later use. These instructions will now be the same as the v_to_v experiments. From
a CRC machine, load python and root with:

```
module load python
module load root
```

Start training:

```
./train.py training.npz -o test1
./train.py training.npz -l 10 -l 5 -o two_layer
```

The first option trains a basic NN with 1 hidden layer (3 nodes).  The second option trains a neural network with two hidden layers with 10 nodes in the first and 5 in the second.

## Validate NN

This script compares the performance of the NN on an independent sample you supply.  (Don't use your training file for this!)

```
./root_to_npz.py 10000 validate10k.npz
./validate.py testv1_N10_b256_l3_frac0.900000.tgz validate10k.npz
```

The first line generates a validation sample.  The second line runs the validation on the simple model (single layer with 3 hidden nodes).  The output is saved to a file that has the same name as the training file but the `.tgz` is replaced by `.root`.

## Print NN

This is a very simple (and not well designed) script that prints out the NN weights and verifies if the solution makes sense.  It **only** works for the simple one layer, 3 node network.  It won't produce sensible output for anything else.

```
./print.py testv1_N10_b256_l3_frac0.900000.tgz
```

