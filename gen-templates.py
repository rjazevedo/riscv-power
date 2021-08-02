#!/usr/bin/python

import argparse
import random
import string
import os
import numpy


class InstructionBasedTemplate:
    _templateHeader = """
        .text
        .align  2
        .globl _start
_start:
        .globl  main
        .type   main, @function
main:
        li    t0, $iterations

"""

    _templateFooter = """

        addi    t0, t0, -1
        bne     t0, x0, loop
        j       0x1FF0
end:    beq     x0, x0, end
"""

    _aRegisters = ['a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7']
    _tRegisters = ['t0', 't1', 't2', 't3', 't4', 't5', 't6']
    _sRegisters = ['s0', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11']
    _randomRange = range(0, 33)
    # Based on Dynamically Exploiting Narrow Width Operands to Improve Processor Power and Performance,
    # David Brooks and Margaret Martonosi, HPCA 99
    _randomWeight = [0.2222222, 0.1180556, 0.0347222, 0.0486111,  0.0694444,  0.0486111,
                     0.0486111,  0.0486111,  0.0486111,  0.0555556,  0.0277778,  0.0277778,
                     0.0069444,  0.0138889,  0.0208333,  0.0208333,  0.0208333,  0.0138889,
                     0.0138889,  0.0069444,  0,    0.0138889,  0.0138889,  0.0277778,  0,
                     0.0069444,  0,    0,    0.0069444,  0.0069444,  0,    0,    0.0069444 ]

    _randomRegisters = []

    def __init__(self, i, n, instruction):
        """This constructor receives the three basic parameters to create template instructions:
           * i: the number of iterations the loop will execute
           * n: the ammount of instructions to include inside the loop
           * instruction: the instruction to include in the loop
           """
        self.iterations = i
        self.nInstructions = n
        self.instructionName = instruction
        self.program = ''
        self.dir = 'test-programs'
        self.prefix = ''
        self._randomRegisters = self._tRegisters[1:]
        self._randomRegisters.extend(self._aRegisters)
        self._randomRegisters.extend(self._sRegisters)
        self._destRegisters = []

        return

    def SaveProgram(self):
        programName = os.path.join(self.dir,
                                   self.prefix +
                                   self.instructionName +
                                   '_' +
                                   str(self.iterations) +
                                   'x' +
                                   str(self.nInstructions) +
                                   '.s')
        open(programName, 'wt').write(self.program)

    def RandomInitialize16bitRegisters(self, registers):
        for r in registers:
            self.program += "        li %s, %d\n" % (r, random.randint(0, 2 ** 14 - 1) * 4)

    def RandomInitializeRegisters(self, registers, noZero = False, multipleOf4 = False):
        for r in registers:
            value = 2 ** numpy.random.choice(self._randomRange, p=self._randomWeight) - 1
            if noZero:
                value += 1
            if multipleOf4:
                value &= ~3
            self.program += "        li %s, %d\n" % (r, value)

    def ReserveDestinationRegisters(self, number):
        for i in range(0, number):
            register = random.choice(self._randomRegisters)
            self._randomRegisters.remove(register)
            self._destRegisters.append(register)

    def AddHeader(self):
        self.program += string.replace(self._templateHeader, '$iterations', str(self.iterations))

    def AddLoopLabel(self):
        self.program += "\nloop:\n"

    def AddFooter(self):
        self.program += self._templateFooter

    def AddRandomInstruction(self):
        return '# No template given\n'

    def ForceAlignment(self):
        self.program += '        .align 7'

    def GenerateProgram(self, removeZero = False):
        self.AddHeader()
        self.RandomInitializeRegisters(self._randomRegisters, removeZero)
        self.RandomInitializeRegisters(self._destRegisters, removeZero)
        self.ForceAlignment()
        self.AddLoopLabel()
        for i in range(0, self.nInstructions):
            self.program += self.AddRandomInstruction()
        self.AddFooter()
        self.SaveProgram()

    def SetDir(self, newDir):
        self.dir = newDir

    def SetPrefix(self, newPrefix):
        self.prefix = newPrefix


class IBTemplateTypeR(InstructionBasedTemplate):
    def AddRandomInstruction(self):
        return "        %s    %s, %s, %s\n" % (self.instructionName,
                                               random.choice(self._destRegisters),
                                               random.choice(self._randomRegisters),
                                               random.choice(self._randomRegisters))


class IBTemplateTypeI(InstructionBasedTemplate):
    def __init__(self, i, n, instruction, minI, maxI):
        InstructionBasedTemplate.__init__(self, i, n, instruction)
        self.minI = minI
        self.maxI = maxI

    def AddRandomInstruction(self):
        return "        %s    %s, %s, %d\n" % (self.instructionName,
                                                        random.choice(self._randomRegisters),
                                                        random.choice(self._randomRegisters),
                                                        random.randint(self.minI, self.maxI))


class IBTemplateLI(IBTemplateTypeI):
    def AddRandomInstruction(self):
        return "        %s    %s, %d\n" % (self.instructionName,
                                                    random.choice(self._randomRegisters),
                                                    random.randint(self.minI, self.maxI))


class IBTemplateTypeU(InstructionBasedTemplate):
    def AddRandomInstruction(self):
        return "        %s    %s, %d\n" % (self.instructionName,
                                                        random.choice(self._randomRegisters),
                                                        random.randint(0, 2 ** 20 - 1))


class IBTemplate2Registers(InstructionBasedTemplate):
    def AddRandomInstruction(self):
        return "        %s    %s, %s\n" % (self.instructionName,
                                                        random.choice(self._randomRegisters),
                                                        random.choice(self._randomRegisters))


class IBTemplateNOP(InstructionBasedTemplate):
    def AddRandomInstruction(self):
        return "        nop\n"


class IBTemplateMemLoad(InstructionBasedTemplate):
    def __init__(self, i, n, instruction, baseAddress, endAddress):
        InstructionBasedTemplate.__init__(self, i, n, instruction)
        self.baseAddress = baseAddress
        self.endAddress = endAddress
        self.range = int((endAddress - baseAddress) / 4)

    def AddRandomInstruction(self):
        return "        %s    %s, %d(%s)\n" % (self.instructionName,
                                                        random.choice(self._destRegisters),
                                                        self.baseAddress + 4 * random.randint(0, self.range),
                                                        random.choice(self._randomRegisters))


class IBTemplateMemStore(InstructionBasedTemplate):
    def __init__(self, i, n, instruction, baseAddress, endAddress):
        InstructionBasedTemplate.__init__(self, i, n, instruction)
        self.baseAddress = baseAddress
        self.endAddress = endAddress
        self.range = int((endAddress - baseAddress) / 4)

    def RandomInitializeRegisters(self, registers, noZero = False, multipleOf4 = True):
        for r in registers:
            self.program += "        li %s, %d\n" % (r, 1024 + random.randint(0, 2**10) * 4)

    def AddRandomInstruction(self):
        return "        %s    %s, %d(%s)\n" % (self.instructionName,
                                                        random.choice(self._destRegisters),
                                                        self.baseAddress + 4 * random.randint(0, self.range),
                                                        random.choice(self._randomRegisters))


class IBTemplateTypeShift(InstructionBasedTemplate):
    def AddRandomInstruction(self):
        return "        %s    %s, %s, %d\n" % (self.instructionName,
                                                        random.choice(self._destRegisters),
                                                        random.choice(self._randomRegisters),
                                                        random.randint(0, 31))


class IPCTemplate(InstructionBasedTemplate):

    _addrRegisters = []

    def __init__(self, i, n, ratio):
        """This constructor receives the three basic parameters to create template instructions:
            * i: the number of iterations the loop will execute
            * n: the ammount of instructions to include inside the loop
            * instructions: list of pairs (instruction, probability)
            * ratio: ratio of 100*fast/slow instructions
            """
        InstructionBasedTemplate.__init__(self, i, n, 'ipc%02d' % ratio)
        self.range = 511
        self.baseAddress = 0
        self.minI = 0
        self.maxI = 2047
        self.ratio = ratio
        self._addrRegisters = []

    def ReserveAddressRegisters(self, number):
        for i in range(0, number):
            register = random.choice(self._randomRegisters)
            self._randomRegisters.remove(register)
            self._addrRegisters.append(register)

    def AddSlowInstruction(self):
        if (random.random() * 2 < 1):
            instructionName = random.choice(['mul', 'mulw', 'mulh', 'mulhsu', 'mulhu'])
            return "        %s    %s, %s, %s\n" % (instructionName,
                                                   random.choice(self._destRegisters),
                                                   random.choice(self._randomRegisters),
                                                   random.choice(self._randomRegisters))
        else:
            instructionName = random.choice(['lb', 'lh', 'lw', 'lbu', 'lhu'])
            return "        %s    %s, %d(%s)\n" % (instructionName,
                                                   random.choice(self._destRegisters),
                                                   self.baseAddress + 4 * random.randint(0, self.range),
                                                   random.choice(self._addrRegisters))
    def AddFastInstruction(self):
        if (random.random() * 2 < 1):
            instructionName = random.choice(['add', 'addw', 'sub', 'subw', 'sll', 'sllw', 'srl', 'srlw', 'sra', 'sraw',
                                             'xor', 'or', 'and', 'slt', 'sltu'])
            return "        %s    %s, %s, %s\n" % (instructionName,
                                                   random.choice(self._destRegisters),
                                                   random.choice(self._randomRegisters),
                                                   random.choice(self._randomRegisters))
        else:
            instructionName = random.choice(['addi', 'addiw', 'xori', 'ori', 'andi', 'slti', 'sltiu'])
            return "        %s    %s, %s, %d\n" % (instructionName,
                                                   random.choice(self._destRegisters),
                                                   random.choice(self._randomRegisters),
                                                   random.randint(self.minI, self.maxI))

    def AddRandomInstruction(self):
        if random.random() * 100 < self.ratio:
            return self.AddFastInstruction()
        else:
            return self.AddSlowInstruction()

    def GenerateProgram(self, removeZero=False):
        self.AddHeader()
        self.RandomInitializeRegisters(self._randomRegisters, removeZero)
        self.RandomInitializeRegisters(self._destRegisters, removeZero)
        self.RandomInitializeRegisters(self._addrRegisters, removeZero, True)
        self.ForceAlignment()
        self.AddLoopLabel()
        for i in range(0, self.nInstructions):
            self.program += self.AddRandomInstruction()
        self.AddFooter()
        self.SaveProgram()


if __name__ == '__main__':
    random.seed()

    parser = argparse.ArgumentParser(description = 'Generate characterization programs for Instruction Based Power Models')

    parser.add_argument('-i', '--iterations', type=int, required=True, help='Number of loop iterations')
    parser.add_argument('-n', '--number', type=int, required=True, help='Number of instructions to include in the loop body')
    parser.add_argument('-o', '--output', required=False, help='Output directory for template programs')
    parser.add_argument('-v', '--verbose', required=False, action='store_true', help='Show debug information')
    parser.add_argument('-p', '--prefix', required=False, help='Add this prefix to all filenames')
    args = parser.parse_args()

    rTypeInstructions = ['add', 'addw', 'sub', 'subw', 'sll', 'sllw', 'srl', 'srlw', 'sra', 'sraw', 'xor', 'or', 'and',
                         'slt', 'sltu', 'mul', 'mulw', 'mulh', 'mulhsu', 'mulhu']
    divInstructions = ['div', 'divw', 'divu', 'divuw', 'rem', 'remw', 'remu', 'remuw']
    iTypeInstructions = ['addi', 'addiw', 'xori', 'ori', 'andi', 'slti', 'sltiu']
    liInstruction = ['li']
    uTypeInstructions = ['lui', 'auipc']
    r2TypeInstructions = ['mv']
    nopInstruction = ['nop']
    memLoadInstructions = ['lb', 'lh', 'lw', 'lbu', 'lhu']
    memStoreInstructions = ['sb', 'sh', 'sw']
    shiftImmediate = ['slli', 'slliw', 'srli', 'srliw', 'srai', 'sraiw']
    branchInstructions = ['beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu']
    jumpInstructions = ['jal', 'jalr']

    for instruction in rTypeInstructions:
        if (args.verbose):
            print 'Instruction:', instruction
        gen = IBTemplateTypeR(args.iterations, args.number, instruction)
        gen.ReserveDestinationRegisters(6)
        if (args.output is not None):
            gen.SetDir(args.output)
        if (args.prefix is not None):
            gen.SetPrefix(args.prefix)
        gen.GenerateProgram()

    for instruction in divInstructions:
        if (args.verbose):
            print 'Instruction:', instruction
        gen = IBTemplateTypeR(args.iterations, args.number, instruction)
        gen.ReserveDestinationRegisters(6)
        if (args.output is not None):
            gen.SetDir(args.output)
        if (args.prefix is not None):
            gen.SetPrefix(args.prefix)
        gen.GenerateProgram(True)

    for instruction in iTypeInstructions:
        if (args.verbose):
            print 'Instruction:', instruction
        gen = IBTemplateTypeI(args.iterations, args.number, instruction, 0, 2047)
        if (args.output is not None):
            gen.SetDir(args.output)
        if (args.prefix is not None):
            gen.SetPrefix(args.prefix)
        gen.GenerateProgram()

    for instruction in liInstruction:
        if (args.verbose):
            print 'Instruction:', instruction
        gen = IBTemplateLI(args.iterations, args.number, instruction, 0, 2047)
        if (args.output is not None):
            gen.SetDir(args.output)
        if (args.prefix is not None):
            gen.SetPrefix(args.prefix)
        gen.GenerateProgram()

    for instruction in uTypeInstructions:
        if (args.verbose):
            print 'Instruction:', instruction
        gen = IBTemplateTypeU(args.iterations, args.number, instruction)
        if (args.output is not None):
            gen.SetDir(args.output)
        if (args.prefix is not None):
            gen.SetPrefix(args.prefix)
        gen.GenerateProgram()

    for instruction in r2TypeInstructions:
        if (args.verbose):
            print 'Instruction:', instruction
        gen = IBTemplate2Registers(args.iterations, args.number, instruction)
        if (args.output is not None):
            gen.SetDir(args.output)
        if (args.prefix is not None):
            gen.SetPrefix(args.prefix)
        gen.GenerateProgram()

    for instruction in nopInstruction:
        if (args.verbose):
            print 'Instruction:', instruction
        gen = IBTemplateNOP(args.iterations, args.number, instruction)
        if (args.output is not None):
            gen.SetDir(args.output)
        if (args.prefix is not None):
            gen.SetPrefix(args.prefix)
        gen.GenerateProgram()

    for instruction in memLoadInstructions:
        if (args.verbose):
            print 'Instruction:', instruction
        gen = IBTemplateMemLoad(args.iterations, args.number, instruction, 0, 512)
        gen.ReserveDestinationRegisters(6)
        if (args.output is not None):
            gen.SetDir(args.output)
        if (args.prefix is not None):
            gen.SetPrefix(args.prefix)
        gen.GenerateProgram()

    for instruction in memStoreInstructions:
        if (args.verbose):
            print 'Instruction:', instruction
        gen = IBTemplateMemStore(args.iterations, args.number, instruction, 0, 512)
        gen.ReserveDestinationRegisters(6)
        if (args.output is not None):
            gen.SetDir(args.output)
        if (args.prefix is not None):
            gen.SetPrefix(args.prefix)
        gen.GenerateProgram()

    for instruction in shiftImmediate:
        if (args.verbose):
            print 'Instruction:', instruction
        gen = IBTemplateTypeShift(args.iterations, args.number, instruction)
        gen.ReserveDestinationRegisters(6)
        if (args.output is not None):
            gen.SetDir(args.output)
        if (args.prefix is not None):
            gen.SetPrefix(args.prefix)
        gen.GenerateProgram()

    for ratio in range(0, 101):
        if (args.verbose):
            print 'IPC:', ratio
        gen = IPCTemplate(args.iterations, args.number, ratio)
        gen.ReserveDestinationRegisters(6)
        gen.ReserveAddressRegisters(6)
        if (args.output is not None):
            gen.SetDir(args.output)
        if (args.prefix is not None):
            gen.SetPrefix(args.prefix)
        gen.GenerateProgram()
