#!/usr/bin/python


import csv
import sys


if __name__ == '__main__':
    if (len(sys.argv) <= 2):
        print 'Usage: %s output.csv csv_files.csv' % sys.argv[0]
        sys.exit(1)

    allInstructions = {}
    allFiles = {}
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

    print 'Joining files...'

    # Create output table header, first column empty and one extra column per instruction
    instructionNames = sorted(allInstructions.keys())
    outputTable = [['']]
    outputTable[0].extend(sorted(instructionNames))

    # Add content
    for inputName in sorted(allFiles.keys()):
        outputLine = [inputName]
        inputContent = allFiles[inputName]
        for mnemonic in instructionNames:
            outputLine.append(inputContent.get(mnemonic, 0))

        outputTable.append(outputLine)

    outputLine = ['Total']
    for mnemonic in instructionNames:
        outputLine.append(allInstructions.get(mnemonic))
    outputTable.append(outputLine)

    print 'Writing', sys.argv[1], '...'
    csv.writer(open(sys.argv[1], 'wt')).writerows(outputTable)
