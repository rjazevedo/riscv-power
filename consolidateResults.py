#!/usr/bin/python

import csv
import sys
import os
import string


def ReadPower(fileName):
    fileName = string.replace(fileName, '.instr.csv', '.pwr')
    if not os.path.isfile(fileName):
        filName = string.replace(fileName, '.csv', '.pwr')
        if not os.path.isfile(fileName):
            return 0.0

    lines = open(fileName).readlines()
    for l in lines:
        splited = l.split()
        if len(splited) > 0:
            if splited[0] == 'Rocket':
                return float(splited[3])

    return 0.0


if __name__ == '__main__':
    if (len(sys.argv) <= 2):
        print 'Usage: %s output.csv csv_files.csv' % sys.argv[0]
        print 'If a .pwr file is found under the same csv_file name, its power is read and added to the output table.'
        sys.exit(1)

    allInstructions = {}
    allFiles = {}
    powerInfo = {}
    # Read all files adding the instruction counter to allInstructions.
    # Side effect: every instruction used will be in the dictionary
    for fileName in sys.argv[2:]:
        print 'Reading', fileName, '...'
        inputTable = list(csv.reader(open(fileName)))
        inputDict = {}
        for mnemonic, count in inputTable:
            allInstructions[mnemonic] = allInstructions.get(mnemonic, 0) + int(count)
            inputDict[mnemonic] = int(count)
        allFiles[fileName] = inputDict
        powerInfo[fileName] = ReadPower(fileName)

    print 'Joining files...'

    # Create output table header, first 3 columns empty per instruction, followed by all instructions
    instructionNames = sorted(allInstructions.keys())
    outputTable = [['', '', '']]
    outputTable[0].extend(sorted(instructionNames))

    # Add content
    for inputName in sorted(allFiles.keys()):
        outputLine = [inputName, inputName.split('_')[1], powerInfo[inputName]]
        inputContent = allFiles[inputName]
        for mnemonic in instructionNames:
            outputLine.append(inputContent.get(mnemonic, 0))

        outputTable.append(outputLine)

    outputLine = ['Total', '', '']
    for mnemonic in instructionNames:
        outputLine.append(allInstructions.get(mnemonic))
    outputTable.append(outputLine)

    print 'Writing', sys.argv[1], '...'
    csv.writer(open(sys.argv[1], 'wt')).writerows(outputTable)
