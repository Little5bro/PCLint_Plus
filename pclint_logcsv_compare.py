import csv
import string
import codecs
import re
import os
import time
import sys
import tarfile
from argparse import ArgumentParser
import shutil


class Filter_Run():
    def __init__(self,input_file_raw,input_file_new,output_file):
        self.output_file = output_file
        self.input_file_raw = input_file_raw
        self.input_file_new = input_file_new
        
        self.FileCheck()


    def FileCheck(self):
        fd1 = codecs.open(self.input_file_new,'rb','utf-8') 
        fd2 = codecs.open(self.input_file_raw,'rb','utf-8')

        lcsv1 = list(csv.reader(fd1))
        lcsv2 = list(csv.reader(fd2))
        del lcsv1[0]
        del lcsv2[0]

        for i, row1 in enumerate(lcsv1):
            fix_flag = 'null'
            for j, row2 in enumerate(lcsv2):
                if row1[:2] == row2[:2]:
                    if row1[2:] == row2[2:]:
                        fix_flag = 'unchanged'
                    else:
                        fix_flag = 'modified'
                    del lcsv2[j]
                    break
            if fix_flag == 'null':
                fix_flag = 'new'
            row1.append(fix_flag)
        
        size = len(lcsv2)

        for i in range(size):
            lcsv2[i].append('fixed')
            lcsv1.append(lcsv2[i])

        savefile = open(self.output_file, 'wb')
        savefile_csv = csv.writer(savefile)
        savefile_csv.writerow(['Path', 'FileName','Line','Type','WarnType','Warnspec', 'status'])

        for row in lcsv1:
            savefile_csv.writerow(row)


        fd1.close()
        fd2.close()
        savefile.close()
    

def arg_config():
    parser = ArgumentParser(prog=sys.argv[0], description='Command Line aguments')

    parser.add_argument('--inputlogfileraw',
                        type=str,
                        required=True,
                        help="used for input raw file")
    parser.add_argument('--inputlogfilenew',
                        type=str,
                        required=True,
                        help="used for input new file")


    args = parser.parse_args()
    arg = vars(args)
    return arg

def untar(fname,dirs):
    t = tarfile.open(fname)
    t.extractall(path = dirs)

def tar(fname):
    t = tarfile.open(fname + ".tar.gz","w:gz")
    for dirpath,dirnames,files in os.walk(fname):
        for file in files:
            fullpath = os.path.join(dirpath,file)
            t.add(fullpath)
    t.close()

if __name__ == "__main__":
    
    config = arg_config()

    inputfileraw = config.get("inputlogfileraw")
    inputfilenew = config.get("inputlogfilenew") 

    new_folder = "Log/SCM_"+re.match('\w+_([0-9a-z]+)\.', inputfilenew).group(1)
    last_folder = "Log/SCM_"+re.match('\w+_([0-9a-z]+)\.', inputfileraw).group(1)
    diff_folder = "Log/Diff_"+re.match('\w+_([0-9a-z]+)\.', inputfilenew).group(1)+'_'+re.match('\w+_([0-9a-z]+)\.', inputfileraw).group(1)

    untar(inputfileraw, last_folder)
    untar(inputfilenew, new_folder)
    if os.path.exists(diff_folder) == False:
        os.mkdir(diff_folder)

    for dirpath,dirnames,files in os.walk(last_folder):
        filesraw = [file for file in files]

    for dirpath,dirnames,files in os.walk(new_folder):
        for filenew in files:
            if filenew in filesraw:
                rawfile = last_folder+'/'+filenew
                newfile = new_folder+'/'+filenew     
                outfile = diff_folder+'/'+filenew
                Filter_Run(rawfile, newfile, outfile)

    tar("Log")
    shutil.rmtree("Log",True)
