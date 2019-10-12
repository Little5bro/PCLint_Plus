#!/bin/bash

workspace="${PWD}"
pclintdir="$workspace/pclintplus1.2.1"
lintdir="$pclintdir/config"
imposter_log="$lintdir/imposter-log"
logdir="$workspace/log/"
logcsvdir="$workspace/logcsv/"

export PATH=$PATH:$pclintdir:$lintdir
export IMPOSTER_LOG="$imposter_log"

rm -rf $logdir
rm -rf $logcsvdir

cp Standard.lnt $lintdir

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

cd $workspace
mkdir -p $logdir
mkdir -p $logcsvdir

SRC_DIR=$(find $workspace -type f -name CHANGELOG.md | head -n 1)
SRC_DIR=${SRC_DIR%/*}'/'

cd $SRC_DIR
mkdir build

export IMPOSTER_COMPILER=/usr/bin/cc
command -v cmake >/dev/null || { curl -O http://10.25.15.53:1080/tools/cmake/cmake-3.14.1.tar.gz;  tar -xf cmake-3.14.1.tar.gz; cd cmake-3.14.1; ./bootstrap && make > /dev/null && make install > /dev/null; }

cd ${SRC_DIR}build
cmake -version
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
cp co-gcc.lnt co-gcc.h Standard.lnt project.lnt ${workspace}

cd $workspace
pclp64_linux co-gcc.lnt Standard.lnt project.lnt > ${logdir}cv2x_app.log

python changelogtocsv_pclint.py --inputlogfile=${logdir}cv2x_app.log \
                                --outputcsvfile=${logcsvdir}cv2x_app

cd $logcsvdir
tar -zcvf ../log.csv.tar.gz *
mv ../log.csv.tar.gz log.csv.tar.gz

