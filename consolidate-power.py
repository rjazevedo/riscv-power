#!/usr/bin/python

import csv
import sys


if __name__ == '__main__':
    if (len(sys.argv) <= 2):
        print 'Usage: %s output.csv power_files.pwr' % sys.argv[0]
        sys.exit(1)

    outputTable = []

    # Read all files adding the instruction counter to allInstructions.
    # Side effect: every instruction used will be in the dictionary
    for fileName in sys.argv[2:]:
        print 'Reading', fileName, '...'

        lines = open(fileName).readlines()
        splited = lines[13].split()
        if (splited[0] == 'Rocket'):
            powerConsumption = float(splited[3])
        else:
            powerConsumption = 0.0
        outputTable.append([fileName, powerConsumption])

    print 'Writing', sys.argv[1], '...'
    csv.writer(open(sys.argv[1], 'wt')).writerows(outputTable)
