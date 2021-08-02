#!/usr/bin/python

import argparse
import random
import string
import sys
import yaml
import bz2
import csv


class PowerTable:
    def __init__(self, inputFile):
        inputContent = yaml.load(open(inputFile))

        self.defaultCount = 0
        self.defaultInstructions = []

        self.info = inputContent['info']
        self.stall = float(self.info.get(('stall'), 0.0))
        self.unit = self.info.get('unit', 'unknown')
        self.frequency = float(self.info.get('frequency', 0.0))
        self.library = self.info.get('library', 'unknown')
        self.leakage = self.info.get('leakage', 0.0)
        self.default = self.info.get('default', 0.0)

        if self.frequency == 0:
            print 'Frequency not provided in YAML file, considering energy per instruction'
            frequency = 1
        else:
            frequency = self.frequency

        self.leakage /= frequency * 1000000
        self.stall /= frequency * 1000000
        self.default /= frequency * 1000000

        self.instructions = inputContent['instructions']
        for i in self.instructions.keys():
            self.instructions[i] = float(self.instructions[i]) / (frequency * 1000000)

    def GetPower(self, instruction):
        if instruction in self.instructions:
            return self.instructions[instruction]
        else:
            self.defaultCount += 1
            if instruction not in self.defaultInstructions:
                self.defaultInstructions.append(instruction)
            return self.default

    @property
    def GetStallPower(self):
        return self.stall

    @property
    def GetLeakage(self):
        return self.leakage

    @property
    def GetFrequency(self):
        return self.frequency

if __name__ == '__main__':
    random.seed()

    parser = argparse.ArgumentParser(description = 'Apply the Instruction Based Power Model to a stream of instructions')

    parser.add_argument('-t', '--table', required=True, help='Instruction Based Power Table to use')
    parser.add_argument('-i', '--input', required=False, help='Input file containing instruction trace')
    parser.add_argument('-g', '--graph', required=False, help='Generate a graphic containing power consumption')
    parser.add_argument('-f', '--frequency', required=False, type=float, help='Processor operation frequency')
    parser.add_argument('-q', '--quiet', required=False, action='store_true', help='Show only power results')

    args = parser.parse_args()

    powerTable = PowerTable(args.table)

    if args.input is None:
        inputFile = open(args.input)
    elif args.input[-3:] == 'bz2':
        inputFile = bz2.BZ2File(args.input)
    else:
        inputFile = sys.stdin

    running = 0
    runningPower = 0
    stalled = 0
    stalledPower = 0

    energyThroughTime = []
    cycleCounter = 0
    energyBlock = 0.0

    for line in inputFile.readlines():
        if len(line) > 126:
            if line[0] == 'C' and line[2] == ':':
                core = int(line[1:2])
                executed = line[16:17]
                instruction = string.split(line[126:])[0]
                if executed == '1':
                    power = powerTable.GetPower(instruction)
                    running += 1
                    runningPower += power
                else:
                    power = powerTable.GetStallPower
                    stalled += 1
                    stalledPower += power

                energyBlock += power
                cycleCounter += 1
                if (cycleCounter == 1000):
                    energyThroughTime.append(energyBlock)
                    cycleCounter = 0
                    energyBlock = 0.0
                if not args.quiet:
                    print line[:-1], '\t', power, powerTable.unit
            else:
                if not args.quiet:
                    print line
        else:
            if not args.quiet:
                print line

    print '***** Execution Report *****'
    print 'Executed Instructions: %d' % (running)
    print 'Stalled Cycles       : %d' % (stalled)
    print 'Total Cycles         : %d' % (running + stalled)
    print '***** Energy Consumption *****'
    print 'Executed Instructions: %.2f %s' % (runningPower, powerTable.unit)
    print 'Stalled Cycles       : %.2f %s' % (stalledPower, powerTable.unit)
    print 'Total Cycles         : %.2f %s' % (runningPower + stalledPower, powerTable.unit)
    print 'Leakage              : %.2f %s' % ((running + stalled) * powerTable.GetLeakage, powerTable.unit)
    print '***** Power Report *****'
    print 'Leakage              : %.2f uW' % (powerTable.GetLeakage * powerTable.GetFrequency * 1000000)
    print 'Dynamic Power        : %.2f uW' % (powerTable.GetFrequency * 1000000 / (running + stalled) *
                                              (runningPower + stalledPower))
    print 'Power Total          : %.2f uW' % (powerTable.GetFrequency * 1000000 / (running + stalled) *
                                              (runningPower + stalledPower + powerTable.GetLeakage * (running + stalled)))

    if powerTable.defaultCount != 0:
        print '%d instructions used default power:' % powerTable.defaultCount, powerTable.defaultInstructions

    if (args.graph is not None):
        csv.writer(open(args.graph, 'wt')).writerows([energyThroughTime])

