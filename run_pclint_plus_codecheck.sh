#!/bin/bash

workspace="${PWD}"
sourcedir="$workspace/../"
pclintdir="$workspace/pclintplus1.2"
pyyamldir="$workspace/PyYAML-3.13/"
regexdir="$workspace/regex-2019.03.09/"
Standard_lnt="$workspace/Standard.lnt"

lintdir="$pclintdir/config"
imposter_log="$lintdir/imposter-log"

logdir="$workspace/log/"
logcsvdir="$workspace/logcsv/"

export PATH=$PATH:$pclintdir:$lintdir
export IMPOSTER_LOG="$imposter_log"

builddir="$sourcedir/build/"

rm -rf $logdir
rm -rf $logcsvdir
rm -rf $builddir

echo "install python module..."
cd $pyyamldir
python setup.py install
cd $regexdir
python setup.py install

cd $lintdir
python pclp_config.py --compiler=gcc \
                      --compiler-bin="${CROSS_COMPILE}gcc" \
                      --config-output-lnt-file=co-gcc.lnt \
                      --config-output-header-file=co-gcc.h \
                      --generate-compiler-config
                      
gcc -o imposter imposter.c

mkdir -p $logdir
mkdir -p $logcsvdir
mkdir -p $builddir

export IMPOSTER_COMPILER=/usr/bin/cc
export CC=imposter

#cd $sourcedir
#make clean is required before every make
#chmod 777 autobuild.sh
#./autobuild.sh

cd $builddir
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

cp $Standard_lnt $lintdir
pclp64_linux co-gcc.lnt Standard.lnt project.lnt > ${logdir}smartantenna_demo.log

cd $workspace
python changelogtocsv_pclint.py --inputlogfile=${logdir}smartantenna_demo.log \
                                 --outputcsvfile=${logcsvdir}smartantenna_demo

cd $logcsvdir
tar -zcvf ../log.csv.tar.gz *
mv ../log.csv.tar.gz log.csv.tar.gz



