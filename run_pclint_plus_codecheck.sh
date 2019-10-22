#!/bin/bash

projectdir="${PWD}"
workspace="$projectdir/PCLint_Plus/"
pclintdir="$workspace/pclintplus1.2.1"
lintdir="$pclintdir/config"
imposter_log="$lintdir/imposter-log"
logdir="$workspace/log/"
logcsvdir="$workspace/logcsv/"

export PATH=$PATH:$pclintdir:$lintdir
export IMPOSTER_LOG="$imposter_log"

rm -rf $logdir $logcsvdir
mkdir -p $logdir $logcsvdir

codespace=$(find $projectdir -type f -name CHANGELOG.md | head -n 1)
codespace=${codespace%/*}'/'

cd $workspace
cp Standard.lnt au-misra3.lnt $lintdir

#echo "install python module"
#cd ${workspace}/PyYAML-3.13
#python setup.py install

#cd ${workspace}/regex-2019.03.09
#python setup.py install

cd $lintdir
python pclp_config.py --compiler=gcc \
                      --compiler-bin="${CROSS_COMPILE}gcc" \
                      --config-output-lnt-file=co-gcc.lnt \
                      --config-output-header-file=co-gcc.h \
                      --generate-compiler-config
                      
gcc -o imposter imposter.c

cd $codespace
export IMPOSTER_COMPILER=/usr/bin/cc
mkdir -p build
cd ${codespace}build
CC=imposter cmake ..
rm $imposter_log
make clean
make

cd $lintdir
echo "+++++++++++++++++++++ imposter_log print starts +++++++++++++++++++++"
cat $imposter_log
echo "+++++++++++++++++++++  imposter_log print ends  +++++++++++++++++++++"

python pclp_config.py   --compiler=gcc \
                        --imposter-file=$imposter_log \
                        --config-output-lnt-file=project.lnt \
                        --generate-project-config
cp co-gcc.lnt co-gcc.h Standard.lnt project.lnt au-misra3.lnt ${workspace}

cd $workspace
pclp64_linux co-gcc.lnt Standard.lnt project.lnt au-misra3.lnt > ${logdir}user_app.log

python convert_pclintlog_to_csv.py --inputlogfile=${logdir}user_app.log \
                                   --outputcsvfile=${logcsvdir}user_app

python do_pclintcsv_statistics.py --pclintfile=${logcsvdir}user_app.csv \
                                  --outputfile=${logcsvdir}statistics.csv

cd $logcsvdir
tar -zcvf ../log.csv.tar.gz *
mv ../log.csv.tar.gz log.csv.tar.gz
