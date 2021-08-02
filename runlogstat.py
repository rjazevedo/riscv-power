#!/usr/bin/python

import argparse
import random
import string
import sys
import csv
import bz2

def DictToCSV(d):
    table = []
    for item in sorted(d.keys()):
        table.append([item, d[item]])
    return table

if __name__ == '__main__':
    random.seed()

    parser = argparse.ArgumentParser(description = 'Read execution log from stdin or file and report number of instructions')

    parser.add_argument('-t', '--trace', required=False, help='Input file containing instruction trace')
    parser.add_argument('-p', '--power', required=False, help='Input file containing power report')
    parser.add_argument('-f', '--frequency', required=False, help='Processor execution frequency (in MHz)')
    parser.add_argument('-o', '--output', required=False, help='Output CSV file containing report')

    args = parser.parse_args()

    executedInstructions = {}

    if (args.trace == None):
        inputFile = sys.stdin
    elif (args.trace[-3:] == 'bz2'):
        inputFile = bz2.BZ2File(args.trace)
    else:
        inputFile = open(args.trace)

    for line in inputFile:
        if (len(line) > 126):
            if (line[0] == 'C' and line[2] == ':'):
                core = int(line[1:2])
                executed = line[16:17]
                instruction = string.split(line[126:])[0]
                if (executed == '1'):
                    executedInstructions[instruction] = executedInstructions.get(instruction, 0) + 1
                else:
                    executedInstructions['stall'] = executedInstructions.get('stall', 0) + 1

    if (args.output != None):
        csv.writer(open(args.output, 'wt')).writerows(DictToCSV(executedInstructions))
    else:
        for instruction in executedInstructions.keys():
            print instruction, executedInstructions[instruction]

    frequency = 0
    if (args.frequency != None):
        frequency = int(args.frequency * 1000000)

    powerConsumption = 0
    if (args.power != None):
        lines = open(args.power).readlines()
        splited = lines[13].split()
        if (splited[0] == 'Rocket'):
            powerConsumption = float(splited[3])

    if (frequency != 0) and (powerConsumption != 0):
        print powerConsumption / frequency