cd $(dirname $0)/..
REPO_DIR=`pwd`
cd -

CONDA_ENV=py36
LOG_DIR=$REPO_DIR/data/logs/redistribution
mkdir -p $LOG_DIR

for MODULE in adult child neonate; do
for HCE in "" "--hce"; do
for INSTRUMENT in "" "--short"; do

    NAME=m"$MODULE"_h"$HCE"_i"$INSTRUMENT"

    if [[ "$INSTRUMENT" == "--short" ]]; then 
        DATA_DIR=$REPO_DIR/data/smartva_output/phmrc_short-rc7/
    else
        DATA_DIR=$REPO_DIR/data/smartva_output/phmrc_full-rc7/
    fi

    for i in {0..499}; do
    NAME=m"$MODULE"_h"$HCE"_i"$INSTRUMENT"_s"$i"
    LOG=$LOG_DIR/$NAME

    qsub -N $NAME -P proj_va -o $LOG -e $LOG -pe multi_slot 4 -l mem_free=8g \
        $REPO_DIR/scripts/python_w_env.sh $REPO_DIR $CONDA_ENV \
        $REPO_DIR/scripts/undetermined_weights.py phmrc $MODULE $DATA_DIR \
        $HCE $INSTRUMENT --n-splits 500 --subset $i $i

    done

done
done
done
