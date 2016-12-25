#!/usr/bin/python

import sys
import time


class Program:
    def __init__(self, code):
        self.c = [l.split() for l in code]

    def printCode(self):
        c = self.c
        j = 0
        while j < len(c):
            print '%02d %s' % (j, ' '.join(c[j]))
            j += 1

    def optimize(self):
        def instr(i):
            if i < len(c):
                return c[i]
            else:
                return []

        modified = True
        optPass = 1
        c = self.c
        while modified:
            print 'Optimizing, pass %d...' % (optPass,)
            new = []
            modified = False
            i = 0
            while i < len(c):
                parts = instr(i)
                if parts[0] == 'inc':
                    reg = parts[1]
                    p2 = instr(i + 1)
                    p3 = instr(i + 2)
                    p4 = instr(i + 3)
                    p5 = instr(i + 4)
                    if p2[0] == 'dec' and p3[0] == 'jnz' and \
                       p3[1] == p2[1] and \
                       p4[0] == 'dec' and p5[0] == 'jnz' \
                       and p4[1] == p5[1]:
                        reg2 = p2[1]
                        reg3 = p4[1]
                        new = new + [['mul',reg2, reg3, reg],['nop'],['nop'],['nop'],['nop'],]
                        modified = True
                        print 'Optimizing line %d-%d into %s' % (i, i + 4, c[i])
                        i += 5
                        continue

                new.append(parts)
                i += 1
            optPass += 1
            c = new

        print new

        newP = Program([])
        newP.c = new
        return newP

    def execute(self, regs):
        def val(v):
            if v in regs:
                return regs[v]
            else:
                return int(v)

        def isReg(reg):
            return reg in ['a', 'b', 'c', 'd']

        def assign(reg, v):
            if isReg(reg):
                regs[reg] = val(v)

        def instr(i):
            if i < len(c):
                return c[i]
            else:
                return []

        i = 0
        c = self.c
        while i < len(c):
        #    print i, ' ', c[i], ' ', regs
            parts = c[i]
            if parts[0] == 'cpy':
                assign(parts[2], parts[1])
            elif parts[0] == 'inc':
                if isReg(parts[1]):
                    regs[parts[1]] += 1
            elif parts[0] == 'dec':
                if isReg(parts[1]):
                    regs[parts[1]] -= 1
            elif parts[0] == 'mul':
                regs[parts[3]] = val(parts[3]) + val(parts[1]) * val(parts[2])
                regs[parts[2]] = 0
                regs[parts[1]] = 0
                print '%s = %s + %s * %s' % (parts[1], parts[1], parts[2], parts[3]), regs
            elif parts[0] == 'jnz':
                r = parts[1]
                v = val(r)
                if v != 0:
                    o = val(parts[2])
        #            print c[i]
        #            print i, 'jnz ', r, ' (=', v, '); offset=', o
                    if i + o >= 0:
                        i += o
                        continue
            elif parts[0] == 'tgl':
                index = i + val(parts[1])
                if index < 0 or index >= len(c):
                    print 'Ignoring toggle on line %i, index is %d' % (i, index)
                    i += 1
                    continue
                instr = c[index]
                if len(instr) == 2:
                    instr[0] = 'dec' if instr[0] == 'inc' else 'inc'
                else:
                    instr[0] = 'cpy' if instr[0] == 'jnz' else 'jnz'
                print 'Toggle %d: %s -> %s' % (index, c[index], ' '.join(instr))
                c[index] = instr
            elif parts[0] == 'out':
                yield val(parts[1])
            elif parts[0] == 'nop':
                pass
            else:
                raise Exception('Unknown instruction "' + c[i][0] + '" at ' + str(i))

            # if i >= 19:
            # print i, ' ', c[i], ' ', regs

            i += 1
            # time.sleep(.2)

f = open(sys.argv[1], 'r')
p = Program(f.readlines())
p.printCode()
p = p.optimize()
p.printCode()

print 'Running...'

done = False
a = 0
expected = [f % 2 for f in xrange(0, 100)]
while not done:
    print 'Testing', a
    regs = {
        'a': a,
        'b': 0,
        'c': 1,
        'd': 0
    }

    comp = zip(p.execute(regs), expected)
    if len([o for (o, x) in comp if o == x]) == len(expected):
        print comp
        break
    
    a += 1

print a
