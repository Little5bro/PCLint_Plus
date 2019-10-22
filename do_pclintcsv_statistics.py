import csv
import sys
from argparse import ArgumentParser

def arg_config():
    parser = ArgumentParser(prog = sys.argv[0])

    parser.add_argument('--pclintfile',
                        type = str,
                        required = True,
                        help = 'used for input pclint file')

    parser.add_argument('--outputfile',
                        type = str,
                        required = True,
                        help = 'used for ouput static.csv files')

    args = parser.parse_args()
    arg = vars(args)
    return arg

class StaticCSV:
    def __init__(self):
        self.csvfile = None
        self.csvwriter = None
        self.fieldnames = ['Type', 'WarnType', 'Count', 'Warnspec']

    def BeginCSV(self, inputfile, outputfile):
        self.inputfile = inputfile
        self.csvfile = open(outputfile, 'wb')
        self.csvwriter = csv.DictWriter(self.csvfile, fieldnames = self.fieldnames)
        self.csvwriter.writeheader()

    def CloseCSV(self):
        self.csvfile.close()

    def WriteCSV(self):
        outputRow = {}
        staticDict = {}
        total = 0
        with open(self.inputfile) as f:
            pclintCSV = csv.DictReader(f)
            for row in pclintCSV:
                if row['Type'] not in staticDict:
                    staticDict[row['Type']] = {row['WarnType']: {'Count':1, 'Warnspec': row['Warnspec']}}
                else:
                    if row['WarnType'] not in staticDict[row['Type']]:
                        staticDict[row['Type']][row['WarnType']] = {'Count':1, 'Warnspec': row['Warnspec']}
                    else:
                        staticDict[row['Type']][row['WarnType']]['Count'] += 1
        
        for key_type, value_type in staticDict.items():
            for key_warntype, value_warntype in value_type.items():
                outputRow['Type'] = key_type
                outputRow['WarnType'] = key_warntype
                outputRow['Count'] = value_warntype['Count']
                outputRow['Warnspec'] = value_warntype['Warnspec']
                total += outputRow['Count']
                self.csvwriter.writerow(outputRow)
        outputRow['Type'] = 'Total'
        outputRow['WarnType'] = '-'
        outputRow['Count'] = total
        outputRow['Warnspec'] = '-'
        self.csvwriter.writerow(outputRow)     

if __name__ == '__main__':
    config = arg_config()
    pclintfile = config.get('pclintfile')
    staticfile = config.get('outputfile')

    scsv = StaticCSV()
    scsv.BeginCSV(pclintfile, staticfile)
    scsv.WriteCSV()
    scsv.CloseCSV()

