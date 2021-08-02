#!/usr/bin/python

import argparse
import random
import string
import sys
import os

class IPCTemplate:
    _templateHeader = """
        .text
        .align  2
        .globl _start
_start:
        .globl  main
        .type   main, @function
main:
        addi    t0, x0, $iterations

"""

    _templateFooter = """

        addi    t0, t0, -1
        bne     t0, x0, loop

        .align 6
end:    beq     x0, x0, end
"""

    _aRegisters = ['a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7']
    _tRegisters = ['t0', 't1', 't2', 't3', 't4', 't5', 't6']
    _sRegisters = ['s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11']

    def __init__(self, i, n, distance):
        """This constructor receives the three basic parameters to create template instructions:
           * i: the number of iterations the loop will execute
           * n: the ammount of instructions to include inside the loop
           * distance: the distance between register reuse
           """
        self.iterations = i
        self.nInstructions = n
        self.distance = distance
        self.program = ''
        self.prefixDir = 'test-programs'
        self.availableSources = {}
        self.availableTargets = {}
        self._randomRegisters = self._tRegisters[1:]
        self._randomRegisters.extend(self._aRegisters)
        self._randomRegisters.extend(self._sRegisters)
        self._randomRegisters = self._tRegisters[1:]
        self._randomRegisters.extend(self._aRegisters)
        self._randomRegisters.extend(self._sRegisters)

        return

    def SaveProgram(self):
        programName = os.path.join(self.prefixDir,
                                   'distance_' +
                                   str(self.distance) +
                                   '_' +
                                   str(self.iterations) +
                                   'x' +
                                   str(self.nInstructions) +
                                   '.s')
        open(programName, 'wt').write(self.program)

    def RandomInitializeRegisters(self, registers):
        for r in registers:
            self.program += "        li %s, %d\n" % (r, random.randint(0, 2**30 - 1) * 4)

    def AddHeader(self):
        self.program += string.replace(self._templateHeader, '$iterations', str(self.iterations))

    def AddLoopLabel(self):
        self.program += "\nloop:\n"

    def AddFooter(self):
        self.program += self._templateFooter

    def AddRandomInstruction(self):
        self.program += '# No template given\n'

    def GenerateProgram(self):
        self.AddHeader()
        self.RandomInitializeRegisters(self._randomRegisters)
        self.AddLoopLabel()
        for i in range(0, self.nInstructions):
            self.AddRandomInstruction()
        self.AddFooter()
        self.SaveProgram()

    def SetPrefix(self, newPrefix):
        self.prefixDir = newPrefix


if __name__ == '__main__':
    random.seed()

    parser = argparse.ArgumentParser(description = 'Generate characterization programs for Instruction Per Cycle Models')

    parser.add_argument('-i', '--iterations', type=int, required=True, help='Number of loop iterations')
    parser.add_argument('-n', '--number', type=int, required=True, help='Number of instructions to include in the loop body')
    parser.add_argument('-o', '--output', required=False, help='Output directory for template programs')
    parser.add_argument('-v', '--verbose', required=False, action='store_true', help='Show debug information')
    args = parser.parse_args()

    rTypeInstructions = ['add', 'sub', 'sll', 'srl', 'sra', 'xor', 'or', 'and', 'slt', 'sltu', 'mul', 'mulh', 'mulhsu', 'mulhu', 'div', 'divu', 'rem', 'remu']
    memLoadInstructions = ['lb', 'lh', 'lw', 'lbu', 'lhu']
    iTypeInstructions = ['addi', 'xori', 'ori', 'andi', 'slti', 'sltiu']
    shiftImmediate = ['slli', 'srli', 'srai']
    branchInstructions = ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu']
    jumpInstructions = ['jal', 'jalr']
    storeInstructions = ['sb', 'sh', 'sw']
    luiInstruction = ['lui']
    auipcInstruction = ['auipc']

    for instruction in rTypeInstructions:
        if (args.verbose):
            print 'Instruction:', instruction
        gen = IBTemplateTypeR(args.iterations, args.number, instruction)
        if (args.output != None):
            gen.SetPrefix(args.output)
        gen.GenerateProgram()


    for instruction in iTypeInstructions:
        if (args.verbose):
            print 'Instruction:', instruction
        gen = IBTemplateTypeI(args.iterations, args.number, instruction, 0, 2047)
        if (args.output != None):
            gen.SetPrefix(args.output)
        gen.GenerateProgram()

    for instruction in memLoadInstructions:
        if (args.verbose):
            print 'Instruction:', instruction
        gen = IBTemplateMem(args.iterations, args.number, instruction, 0, 512)
        if (args.output != None):
            gen.SetPrefix(args.output)
        gen.GenerateProgram()

