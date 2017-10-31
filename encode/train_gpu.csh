#!/bin/csh
#$ -pe smp 6             # 24 cores and 4 GPUs per machine 
                         # so ask for 4 cores  to get one GPU
#$ -q gpu                # Specify queue
#$ -l gpu_card=1         # This job is just going to use one GPU card
#$ -N encoder            # Specify job name
#$ -t 1-15               # Number of tasks--make sure arglist below 
                         # is at least that long!
#$ -o sgeLogs            # Where to put the output

# Since UGE doesn't have the nice submit file format from HTCondor, we have to define our possible jobs here

set arglist = ( \
    "-o encoder401 -b 1000 -N 5000 -l 50 -l 100" \
    "-o encoder402 -b 1000 -N 5000 -l 50 -l 100" \
    "-o encoder403 -b 1000 -N 5000 -l 50 -l 100" \
    "-o encoder404 -b 1000 -N 5000 -l 50 -l 100" \
    "-o encoder405 -b 1000 -N 5000 -l 50 -l 100" \
    "-o encoder401 -b 1000 -N 5000 -l 100 -l 251" \
    "-o encoder402 -b 1000 -N 5000 -l 100 -l 251" \
    "-o encoder403 -b 1000 -N 5000 -l 100 -l 251" \
    "-o encoder404 -b 1000 -N 5000 -l 100 -l 251" \
    "-o encoder405 -b 1000 -N 5000 -l 100 -l 251" \
    "-o encoder401 -b 1000 -N 5000 -l 50 -l 100 -l 251" \
    "-o encoder402 -b 1000 -N 5000 -l 50 -l 100 -l 251" \
    "-o encoder403 -b 1000 -N 5000 -l 50 -l 100 -l 251" \
    "-o encoder404 -b 1000 -N 5000 -l 50 -l 100 -l 251" \
    "-o encoder405 -b 1000 -N 5000 -l 50 -l 100 -l 251" \
)

echo Starting...
# @ ind = ($SGE_TASK_ID - 1)
# set args = "$arglist[$ind]"
set args = "$arglist[$SGE_TASK_ID]"
set cmd = "../../train.py ../../train_PtEtaPhi.npz $args"

echo Initializing environment
 
if ( -r /opt/crc/Modules/current/init/csh ) then
       source /opt/crc/Modules/current/init/csh
endif
module load python
module load cuda/8.0 
module load cudnn/v5.1

# Can't use ROOT module since that's for RHEL6.  Use one from my local area instead
source /afs/crc.nd.edu/user/k/klannon/local_root_rhel7/root/bin/thisroot.csh

# Set up Keras+Theano to work for GPUs.  Note: using my locally compiled and installed version of libgpuarray.
setenv THEANO_FLAGS "base_compiledir=$TMPDIR/.theano_gpu,floatX=float32,allow_gc=False,device=gpu,lib.cnmem=0.24,mode=FAST_RUN,optimizer_including=cudnn,dnn.include_path=/afs/crc.nd.edu/x86_64_linux/c/cudnn/5.1/cuda/include,dnn.library_path=/afs/crc.nd.edu/x86_64_linux/c/cudnn/5.1/cuda/lib64"
setenv KERAS_BACKEND "theano"

echo '==================================='
pwd
echo '==================================='
ls -alh
echo '==================================='
printenv
echo '==================================='
uname -a
echo '==================================='
cat /proc/cpuinfo
echo '==================================='
echo Will run $cmd
echo '==================================='

# Make a working directory
set wd = workingdir_${JOB_NAME}_${QUEUE}_${JOB_ID}_${SGE_TASK_ID}
mkdir -p results/$wd
pushd results/$wd
$cmd >& train.log

echo '==================================='
ls -alh
echo '==================================='

# Move the log file into the appropriate results directory, in case something fails later.
set model = *.tgz   #There should only be one of these!

# While we're here, let's run validation too!

set cmd2 = "../../validate.py $model ../../val_PtEtaPhi.npz"

echo Will run $cmd2
$cmd2 >& validate.log

echo '==================================='
ls -alh
echo '==================================='

# Rename output directory
popd
mv results/$wd results/${model:r}
rm -rf $TMPDIR/.theano_gpu

echo Done!
