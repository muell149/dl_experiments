# Vector-to-Vector experiment

The goal of this experiment is test how well an neural network (NN) can reproduce a vector (3-components).  The vector is implemented using ROOT's TLorentzVector so that you can easily change from (pt,eta,phi) representation to (px,py,pz).

If you want to see what options are available for any script in this directory, just try calling the script with `-h`.

## Generate Vectors

This script generates a file with random vectors.  The file is stored in compressed numpy format.

```
./toy_mc.py 1000000 train1M.npz
```

The command above generates 1 million random vectors for training.

## Train NN

This script trains the NN and saves the model for later use.

```
./train.py train1M.npz -o test1
./train.py train1M.npz -l 10 -l 5 -o two_layer
```

The first option trains a basic NN with 1 hidden layer (3 nodes).  The second option trains a neural network with two hidden layers with 10 nodes in the first and 5 in the second.

## Validate NN

This script compares the performance of the NN on an independent sample you supply.  (Don't use your training file for this!)

```
./toy_mc.py 10000 validate10k.npz
./validate.py testv1_N10_b256_l3_frac0.900000.tgz validate10k.npz
```

The first line generates a validation sample.  The second line runs the validation on the simple model (single layer with 3 hidden nodes).  The output is saved to a file that has the same name as the training file but the `.tgz` is replaced by `.root`.

## Print NN

This is a very simple (and not well designed) script that prints out the NN weights and verifies if the solution makes sense.  It **only** works for the simple one layer, 3 node network.  It won't produce sensible output for anything else.

```
./print.py testv1_N10_b256_l3_frac0.900000.tgz
```

## Using HTCondor to Submit batch jobs

You can submit multiple runs as separate batch jobs using the NDCMS cluster from earth.  This lets you do many runs much more rapidly.

### Prepare your work area

Before you can submit any jobs, you need to prepare your work area.  Start by issuing the following commands to get your AFS permissions set properly:

```
pushd ~
find . -path ./YESTRDAY -prune -o -type d -exec fs sa {} nd_campus rl \;
find . -path ./YESTRDAY -prune -o -type d -exec fs sa {} system:authuser rl \;
popd
```

Then, in your `v_to_v` directory, you should create two sub directories:

```
mkdir condorLogs
mkdir results
```

Finally, set the permissions on these so that HTCondor can write into them:

```
fs sa condorLogs nd_campus rlidwk
fs sa condorLogs system:administrators rlidwka
fs sa condorLogs system:authuser rlidwk
fs sa results nd_campus rlidwk
fs sa results system:administrators rlidwka
fs sa results system:authuser rlidwk
```

### Prepare your submission

The `train.submit` file tells HTCondor what jobs to submit and how.  Most of what's there can just be kept the same from one run to the next.  The things that you might want to change include

* The `queue` statement is where you specify which jobs you want to run.  

```  
queue arguments from (  
[args job 1]  
[args job 2]  
[args job 3]  
.  
.  
.  
```  

Where the `[args job N]' entries are just the command line arguments from the `trail.py` command.

* The `transfer_input_files` entry should be updated if you change the script `train.csh` to do different things that require different files (e.g. change the name of the training for validation set, etc.)

* As of this writing (Jun. 1, 2017) there is an issue with some of the CRC hosts.  We are working around this with a `requirements` line to select only the hosts that don't cause `Theano` to crash.


You might also want to make changes to `train.csh`.  Right now the script runs `train.py` and `validate.py` but you could make it do other things as well.

My suggestion is to make a copy of `train.submit` and edit that for each distinct type of run.  That way, if you want to go back and rerun a run, you can just resubmit the appropriate `.submit` file.


### HTCondor Commands

* Submit your job:  
```  
condor_submit train.submit  
```  
Change `train.submit` to be the name of whatever file you want to submit.

* Check on your jobs:  
```  
condor_q  
```  
This tells you about how many jobs are done, running, or idle (not started yet).

* Watch your jobs:
```  
watch condor_q  
```  
This let's you keep an eye on your jobs and notice when they're done.  The `watch` command runs forever, so when you're done watching, use `control-C` to get out of it.

## Using UGE to send jobs to the GPU machines

We will use UGE to submit jobs to machines with GPUs.  The relevant script is `train_gpu.csh`.  You need to modify train_gpu.csh with the list of jobs you want to run.  You control which jobs from the list are run with the `#$ -t 1-11` line.  Those two lines need to be consistent.  You can change the `#$ -N test` line to choose a more descriptive name for your jobs.  This name will go in the logs.

### Preparing to submit

UGE doesn't have the same permissions issues you find in HTCondor, so all you need to do is make `sgeLogs` and (if not already present) `results` directories, and you should be good to go.  Don't forget to modify (a copy of) the `train_gpu.csh` file to be appropriate for the submission you desire.

### UGE Commands 

* Submit your job  
```  
qsub train_gpu.csh  
```  

* Check you jobs  
```  
qstat -u $USER  
```  
Note:  `$USER` is just your user name.  You can replace it with someone elses user name to spy on their jobs or leave it off to see all jobs.  

* Watch you jobs
```
watch qstat -u $USER  
``` 


