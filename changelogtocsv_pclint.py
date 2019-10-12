import csv
import string
import codecs
import re
import os
import time
import sys
from argparse import ArgumentParser

#import pandas as pd
#import numpy as np
pathFilter=['dot2_asn1']


Warning_match = re.compile("(?P<path>.*)warning (?P<Warncode>[0-9]+):(?P<content>.*)")
Info_match = re.compile("(?P<path>.*)info (?P<Warncode>[0-9]+):(?P<content>.*)")
Error_match = re.compile("(?P<path>.*)error (?P<Warncode>[0-9]+):(?P<content>.*)")

baseline_match = re.compile("(?P<basename>.*)\((?P<line>[0-9]+)\)")


def checkIsFiltered(path):
    for x in pathFilter:
        if x in path:
            print("++++++++++ checkIsFiltered returns 1 ++++++++++")
            return 1
    return 0


class Filter_warning():
    def __init__(self,Type_name):
        self.path = ''
        self.basename = ''
        self.line = ''
        self.Warning_type = ''
        self.content = ''
        self.Type_name = Type_name

class Filter_Run():
    def __init__(self,input_file,output_file):
        self.mask = 0
        self.output_file = output_file
        self.input_file = input_file
        self.splitlinenum = 600000
        self.Title = ['Path','FileName','Line','Type','WarnType','Warnspec']
        
        self.FileCheck()

    def FileCheck(self):
        self.CreateCsvFile()
        f = codecs.open(self.input_file,'rb','utf-8')
        for index,line in enumerate(f.xreadlines()):
            '''
            if index / self.splitlinenum != self.mask:
                self.mask = index / self.splitlinenum
                self.ChangeHandle()
            '''    
            self.CheckCompile(line,Warning_match,"Warning")
            self.CheckCompile(line,Info_match,"Info")
            self.CheckCompile(line,Error_match,"Error")

        else:
            f.close()

    def ChangeHandle(self):
        self.FileHandle.close()
        self.FileHandle = open(self.output_file + '%s'%self.mask+'.csv','wb')
        self.csvHandle = csv.writer(self.FileHandle)
        self.csvHandle.writerow(self.Title)
    
    def CreateCsvFile(self):
        self.FileHandle = open(self.output_file+'.csv', 'wb')
        self.csvHandle = csv.writer(self.FileHandle)
        self.csvHandle.writerow(self.Title)

    def WriteCsvFile(self,tmplog):
        if isinstance(tmplog,Filter_warning):
            if checkIsFiltered(tmplog.path)==0:
                self.csvHandle.writerow([tmplog.path,tmplog.basename,tmplog.line,tmplog.Type_name,tmplog.Warning_type,tmplog.content])

    def CheckCompile(self,logline,Type_match,Type_name):
        result = re.match(Type_match,logline)
        if result:
            tmp_warning = Filter_warning(Type_name)
            if result.group('path') != '':
                baseline_result = re.search(baseline_match,result.group('path'))
                if baseline_result:
                    basename = baseline_result.group('basename').split('/')[-1]
                    tmp_warning.basename = basename
                    tmp_warning.path = baseline_result.group('basename')[:-len(basename)]
                    tmp_warning.line = baseline_result.group('line')
            tmp_warning.Warning_type = result.group('Warncode')
            tmp_warning.content = result.group('content').strip()
            self.WriteCsvFile(tmp_warning)
        else:
            return None

def arg_config():
    parser = ArgumentParser(prog=sys.argv[0], description='Command Line aguments')

    parser.add_argument('--inputlogfile',
                        type=str,
                        required=True,
                        help="used for chang input file")

    parser.add_argument('--outputcsvfile',
                        type=str,
                        required=True,
                        help='path for output file')

    args = parser.parse_args()
    arg = vars(args)
    return arg

if __name__ == "__main__":
    config = arg_config()
    inputfile = config.get("inputlogfile")
    outputfile = config.get("outputcsvfile")

    Filter_Run(inputfile, outputfile)
    
            
