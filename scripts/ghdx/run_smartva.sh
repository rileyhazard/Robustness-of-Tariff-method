cd $(dirname $0)/../..
REPO=`pwd`
cd -

SMARTVA_REPO=$(dirname "$REPO")/smartva
if [ ! -d "$SMARTVA_REPO" ]; then
    # TODO: prompt for input
    echo "Cannot find smartva repo"
    exit 1
fi

source activate smartva

INPUT_FILE="$REPO/data/ghdx/odk/ghdx_full.csv"
OUTPUT_DIR="$REPO/data/ghdx/smartva"
mkdir -p "$OUTPUT_DIR"

LOG_FILE="$OUTPUT_DIR/log.txt"
rm -f "$LOG_FILE"
echo "Running SmartVA from source using $INPUT_FILE" >> "$LOG_FILE"
echo "Date: $(/bin/date)" >> "$LOG_FILE"

python "$SMARTVA_REPO/app.py" "$INPUT_FILE" "$OUTPUT_DIR"

cd $SMARTVA_REPO
echo "Git Branch: $(git rev-parse --abbrev-ref HEAD)" >> "$LOG_FILE"
echo "Git Commit: $(git rev-parse HEAD)" >> "$LOG_FILE"
cd -
