#!/bin/csh
#$ -pe smp 6             # 24 cores and 4 GPUs per machine 
                         # so ask for 4 cores  to get one GPU
#$ -q gpu                # Specify queue
#$ -l gpu_card=1         # This job is just going to use one GPU card
#$ -N twotest               # Specify job name
#$ -t 1-10               # Number of tasks--make sure arglist below 
                         # is at least that long!
#$ -o sgeLogs            # Where to put the output

# Since UGE doesn't have the nice submit file format from HTCondor, we have to define our possible jobs here

set arglist = ( \
	"-o nodes01 -b 1000 -N 50000" \
	"-o nodes02 -b 1000 -N 50000" \
	"-o nodes03 -b 1000 -N 50000" \
	"-o nodes04 -b 1000 -N 50000" \
	"-o nodes05 -b 1000 -N 50000" \
	"-o param06 -b 1000 -N 5000" \
	"-o param07 -b 1000 -N 5000" \
	"-o param08 -b 1000 -N 5000" \
	"-o param09 -b 1000 -N 5000" \
	"-o param10 -b 1000 -N 5000" \
)

echo Starting...
# @ ind = ($SGE_TASK_ID - 1)
# set args = "$arglist[$ind]"
set args = "$arglist[$SGE_TASK_ID]"
set cmd = "../../train.py ../../train1M.npz $args"

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

set cmd2 = "../../validate.py $model ../../validate10k.npz"

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
