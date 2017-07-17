#!/bin/csh
#$ -pe smp 6             # 24 cores and 4 GPUs per machine 
                         # so ask for 4 cores  to get one GPU
#$ -q gpu                # Specify queue
#$ -l gpu_card=1         # This job is just going to use one GPU card
#$ -N bcnet_test         # Specify job name
#$ -t 1-45               # Number of tasks--make sure arglist below 
                         # is at least that long!
#$ -o sgeLogs            # Where to put the output

# Since UGE doesn't have the nice submit file format from HTCondor, we have to define our possible jobs here

set arglist = ( \
    "-o fourlayers01 -b 1000 -N 50000 -l 500 -l 500 -l 500 -l 500" \
    "-o fourlayers02 -b 1000 -N 50000 -l 500 -l 500 -l 500 -l 500" \
    "-o fourlayers03 -b 1000 -N 50000 -l 500 -l 500 -l 500 -l 500" \
    "-o fourlayers04 -b 1000 -N 50000 -l 500 -l 500 -l 500 -l 500" \
    "-o fourlayers05 -b 1000 -N 50000 -l 500 -l 500 -l 500 -l 500" \
    "-o fourlayers01 -b 1000 -N 50000 -l 100 -l 100 -l 100 -l 100" \
    "-o fourlayers02 -b 1000 -N 50000 -l 100 -l 100 -l 100 -l 100" \
    "-o fourlayers03 -b 1000 -N 50000 -l 100 -l 100 -l 100 -l 100" \
    "-o fourlayers04 -b 1000 -N 50000 -l 100 -l 100 -l 100 -l 100" \
    "-o fourlayers05 -b 1000 -N 50000 -l 100 -l 100 -l 100 -l 100" \
    "-o fourlayers01 -b 1000 -N 50000 -l 251 -l 251 -l 251 -l 251" \
    "-o fourlayers02 -b 1000 -N 50000 -l 251 -l 251 -l 251 -l 251" \
    "-o fourlayers03 -b 1000 -N 50000 -l 251 -l 251 -l 251 -l 251" \
    "-o fourlayers04 -b 1000 -N 50000 -l 251 -l 251 -l 251 -l 251" \
    "-o fourlayers05 -b 1000 -N 50000 -l 251 -l 251 -l 251 -l 251" \
    "-o fivelayers01 -b 1000 -N 50000 -l 500 -l 500 -l 500 -l 500 -l 500" \
    "-o fivelayers02 -b 1000 -N 50000 -l 500 -l 500 -l 500 -l 500 -l 500" \
    "-o fivelayers03 -b 1000 -N 50000 -l 500 -l 500 -l 500 -l 500 -l 500" \
    "-o fivelayers04 -b 1000 -N 50000 -l 500 -l 500 -l 500 -l 500 -l 500" \
    "-o fivelayers05 -b 1000 -N 50000 -l 500 -l 500 -l 500 -l 500 -l 500" \
    "-o fivelayers01 -b 1000 -N 50000 -l 100 -l 100 -l 100 -l 100 -l 100" \
    "-o fivelayers02 -b 1000 -N 50000 -l 100 -l 100 -l 100 -l 100 -l 100" \
    "-o fivelayers03 -b 1000 -N 50000 -l 100 -l 100 -l 100 -l 100 -l 100" \
    "-o fivelayers04 -b 1000 -N 50000 -l 100 -l 100 -l 100 -l 100 -l 100" \
    "-o fivelayers05 -b 1000 -N 50000 -l 100 -l 100 -l 100 -l 100 -l 100" \
    "-o fivelayers01 -b 1000 -N 50000 -l 251 -l 251 -l 251 -l 251 -l 251" \
    "-o fivelayers02 -b 1000 -N 50000 -l 251 -l 251 -l 251 -l 251 -l 251" \
    "-o fivelayers03 -b 1000 -N 50000 -l 251 -l 251 -l 251 -l 251 -l 251" \
    "-o fivelayers04 -b 1000 -N 50000 -l 251 -l 251 -l 251 -l 251 -l 251" \
    "-o fivelayers05 -b 1000 -N 50000 -l 251 -l 251 -l 251 -l 251 -l 251" \
    "-o sixlayers01 -b 1000 -N 50000 -l 500 -l 500 -l 500 -l 500 -l 500 -l 500" \
    "-o sixlayers02 -b 1000 -N 50000 -l 500 -l 500 -l 500 -l 500 -l 500 -l 500" \
    "-o sixlayers03 -b 1000 -N 50000 -l 500 -l 500 -l 500 -l 500 -l 500 -l 500" \
    "-o sixlayers04 -b 1000 -N 50000 -l 500 -l 500 -l 500 -l 500 -l 500 -l 500" \
    "-o sixlayers05 -b 1000 -N 50000 -l 500 -l 500 -l 500 -l 500 -l 500 -l 500" \
    "-o sixlayers01 -b 1000 -N 50000 -l 100 -l 100 -l 100 -l 100 -l 100 -l 100" \
    "-o sixlayers02 -b 1000 -N 50000 -l 100 -l 100 -l 100 -l 100 -l 100 -l 100" \
    "-o sixlayers03 -b 1000 -N 50000 -l 100 -l 100 -l 100 -l 100 -l 100 -l 100" \
    "-o sixlayers04 -b 1000 -N 50000 -l 100 -l 100 -l 100 -l 100 -l 100 -l 100" \
    "-o sixlayers05 -b 1000 -N 50000 -l 100 -l 100 -l 100 -l 100 -l 100 -l 100" \
    "-o sixlayers01 -b 1000 -N 50000 -l 251 -l 251 -l 251 -l 251 -l 251 -l 251" \
    "-o sixlayers02 -b 1000 -N 50000 -l 251 -l 251 -l 251 -l 251 -l 251 -l 251" \
    "-o sixlayers03 -b 1000 -N 50000 -l 251 -l 251 -l 251 -l 251 -l 251 -l 251" \
    "-o sixlayers04 -b 1000 -N 50000 -l 251 -l 251 -l 251 -l 251 -l 251 -l 251" \
    "-o sixlayers05 -b 1000 -N 50000 -l 251 -l 251 -l 251 -l 251 -l 251 -l 251" \
)

echo Starting...
# @ ind = ($SGE_TASK_ID - 1)
# set args = "$arglist[$ind]"
set args = "$arglist[$SGE_TASK_ID]"
set cmd = "../../train.py ../../train1M_PxPyPzE.npz $args"

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

set cmd2 = "../../validate.py $model ../../validate10k_PxPyPzE.npz"

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
