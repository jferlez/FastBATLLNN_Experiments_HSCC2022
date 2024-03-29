#!/bin/bash

# if [ -d ../FastBATLLNN ]; then
#     cd ../FastBATLLNN
#     SCRIPTS="../scripts"
# else
#     cd ..
#     SCRIPT="scripts"
# fi


SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

SYSTEM_TYPE=$(uname)

EXPERIMENT="${SCRIPT_DIR}/experiments/experiment1/experiment1.p"
LOG_DIR="${SCRIPT_DIR}/../results"
TIMEOUT=300

if [ $SYSTEM_TYPE = "Darwin" ]
then
    CORES=$(( `sysctl -n hw.ncpu` / 2 ))
    PYTHON="python3.10"
else
    CORES_PER_SOCKET=`lscpu | grep "Core(s) per socket:" | sed -e 's/[^0-9]//g'`
    SOCKETS=`lscpu | grep "Socket(s):" | sed -e 's/[^0-9]//g'`
    CORES=$(( $CORES_PER_SOCKET * $SOCKETS ))
    PYTHON=""
fi

echo "Detected ${CORES} physical CPU cores."

for argwhole in "$@"; do
    IFS='=' read -r -a array <<< "$argwhole"
    arg="${array[0]}"
    val=$(printf "=%s" "${array[@]:1}")
    val=${val:1}
    case "$arg" in
        --experiment) EXPERIMENT="${val}";;
        --logdir) LOG_DIR="${val}";;
        --timeout) TIMEOUT="${val}";;
        --cores) CORES="${val}";;
        --python) PYTHON="${val}"
    esac
done

if [ ! $SYSTEM_TYPE = "Darwin" ] && [ ! $PYTHON = "" ]
then
    echo "Setting python interpreter is not supported on Linux. Ignoring --python option."
fi

if [ ! -e "${EXPERIMENT}" ]
then
    echo "Invalid experiment file specified. ${EXPERIMENT}" >&2; exit 1
fi
if [ ! -d "${LOG_DIR}" ]
then
    echo "Invalid log directory specified." >&2; exit 1
fi
re='^[0-9]+$'
if ! [[ $TIMEOUT =~ $re ]] ; then
    echo "Invalid timeout specified" >&2; exit 1
fi
if ! [[ $CORES =~ $re ]] ; then
    echo "Invalid core count specified" >&2; exit 1
fi
BASE_NAME=`echo "${EXPERIMENT}" | sed -E -e 's/^(.*\/)?([^/]*)(\.[^\.]*)$/\2/'`

out_fname="${LOG_DIR}/${BASE_NAME}_${NUM_CORES}_${TIMEOUT}sec.txt"
LOG_FILE="${LOG_DIR}/${BASE_NAME}_${NUM_CORES}_${TIMEOUT}sec_log.txt"
> "${out_fname}"
> "${LOG_FILE}"

printf "Logs are dumped in $LOG_FILE\n"
printf "Results are dumped in $out_fname\n"


printf "Running experiment from file ${EXPERIMENT}\n"
if [ $SYSTEM_TYPE = "Darwin" ]
then
    charmrun +p$CORES "${PYTHON}" ./scripts/TLLReachTester_HSCC_int.py "${EXPERIMENT}" "${out_fname}" $CORES $TIMEOUT >> "${LOG_FILE}" || exit
else
    charmrun +p$CORES ./scripts/TLLReachTester_HSCC_int.py "${EXPERIMENT}" "${out_fname}" $CORES $TIMEOUT >> "${LOG_FILE}" || exit
fi

# 0..29; 0..19
# for net_idx in {0..0}
# do
#     for spec_idx in {1..1}
#     do
#         printf "Verifying problem ${net_idx}_${spec_idx}\n" 
#         charmrun +p$NUM_CORES python3.9 ./TLLReachTester_HSCC_int.py $net_idx $spec_idx $out_fname $DIR $NUM_CORES $TIMEOUT >> $LOG_FILE || exit
#     done
# done

# Check for memory leaks using this code:
# net_idx=0
# spec_idx=0
# printf "Verifying problem ${net_idx}_${spec_idx}\n" 
# charmrun +p$NUM_CORES python3.9 ./TLLReachTester_HSCC_int.py $net_idx $spec_idx $out_fname $DIR $NUM_CORES $TIMEOUT >> $LOG_FILE || exit

# cd "${SCRIPTS}"
# printf "Plotting Box chart.. saving to results/experiment_1.pdf\n"
# python boxchart.py 1
# printf "Done!!\n"
