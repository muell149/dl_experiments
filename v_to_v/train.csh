#!/bin/csh -f

echo Starting...
set args = "$*"
set cmd = "./train.py train1M.npz $args"

# Before anything has a chance to fail, let's make the output
# directory HTCondor will look for so that jobs won't go on hold if
# its missing.
mkdir -p results


echo Initializing environment

if ( -r /opt/crc/Modules/current/init/csh ) then
       source /opt/crc/Modules/current/init/csh
endif
module load python
module load root
setenv THEANO_FLAGS "base_compiledir=$_CONDOR_SCRATCH_DIR/.theano"

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

$cmd >& train.log

echo '==================================='
ls -alh
echo '==================================='
ls *.tgz >& /dev/null
if ($? != 0) then
	mkdir -p results/failed/`date +"%Y%m%d%I%M%S"`
	cp *.log results/failed/`date +"%Y%m%d%I%M%S"`/.
endif

# Move the log file into the appropriate results directory, in case something fails later.
set model = *.tgz   #There should only be one of these!
mkdir -p results/${model:r}
mv *.log results/${model:r}

# While we're here, let's run validation too!

set cmd2 = "./validate.py $model validate10k.npz"

echo Will run $cmd2
$cmd2 >& validate.log

echo '==================================='
ls -alh
echo '==================================='

# Put the rest of the outputs in the results directory
mv *.tgz *.root *.log results/${model:r}

rm -rf $_CONDOR_SCRATCH_DIR/.theano

echo Done!
