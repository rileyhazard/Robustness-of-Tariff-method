#$ -S /bin/bash
REPO_DIR=$1
CONDAENV=$2
shift 2;
cd $REPO_DIR

echo "Cluster: $SGE_CLUSTER_NAME"
echo "Architecture: $ARC"
echo "Job ID: $JOB_ID"
echo "Job name: $JOB_NAME"
echo "Job script: $JOB_SCRIPT"
echo "Node: $HOSTNAME"

START_TIME=`/bin/date`
GIT_BRANCH=`git rev-parse --abbrev-ref HEAD`
echo "Running from $REPO_DIR using branch $GIT_BRANCH"
echo "Started at $START_TIME"
echo

echo "Last commit:"
git log -1
echo

source activate $CONDAENV
PYTHONPATH=. python -u "$@"

END_TIME=`/bin/date`
echo "Finished at $END_TIME"
