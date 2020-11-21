#!/usr/bin/python

import re
import sys

from types import NoneType

single_ops = ['push', 'sar', 'sal', 'shl', 'shr']

arithmetic_ops = ['add', 'sub', 'mul', 'div', 'neg', 'adc', 'sbb', 'inc', 'dec']

control_ops = ['jmp', 'je', 'jn', 'jg', 'ja', 'jl', 'jb', 'jo', 'jz',
               'js', 'call', 'loop', 'ret']

segment_regs = ['%ss', '%gs', '%fs', '%ds', '%cs', '%es']

valid_pattern = re.compile('^\s+[0-9a-fA-F]+:\s*[a-zA-Z]+.*')
# we assume stack registers (rbp,rsp) are protected
reg_pattern = ['%ax', '%al', '%ah', '%rax', '%eax',
               '%bx', '%bl', '%bh', '%rbx', '%ebx',
               '%cx', '%cl', '%ch', '%rcx', '%ecx',
               '%dx', '%dl', '%dh', '%rdx', '%edx',
               '%si', '%rsi', '%esi',
               '%di', '%rdi', '%edi',
#                '%sp', '%esp', '%rsp',
#                '%bp', '%ebp', '%rbp',
               '%r8', '%r9', '%r10', '%r11', '%r12', '%r13', '%r14', '%r15',
               '%xmm0', '%xmm1(?![0-5])', '%xmm2', '%xmm3', '%xmm4', '%xmm5', '%xmm6',
               '%xmm13', '%xmm7', '%xmm8', '%xmm9', '%xmm10', '%xmm11', '%xmm12',
               '%xmm14', '%xmm15',
               '%fpr0', '%fpr1', '%fpr2', '%fpr3', '%fpr4', '%fpr5', '%fpr6',
               '%fpr7']



paren_match = re.compile('.*\(.*\).*')

reg_matches = []
for pattern in reg_pattern:
    reg_matches.append(re.compile(pattern))
    
def is_mem_access(search_string):
    '''
    Checks if substring is found within parenthesis, meaning it is a 
    memory access
    Args: search_string - string to search in
    Returns: True - is a memory access, False otherwise
    '''
    return paren_match.match(search_string) is not None
        

class instruction(object):
    def __init__(self, pc, op, in_string=''):
        '''
        initializes an instruction object
        Args: pc - pc of instruction (no '0x' in the front)
              op - instruction op
              (Optional) in_string - string that can be used to create
              instruction from database fields
        '''
        self.pc = pc
        self.op = op
        self.ctrl_flag = False
        self.src_regs = []
        self.mem_src_regs = []
        self.is_mem = False
        self.dest_reg = None
        self.max_bits = 64

        # initialize variables from existing instruction database
        if in_string != '':
            fields = in_string.split()
            self.pc = fields[0]
            self.op = fields[1]
            self.ctrl_flag = True if 'True' in fields[2] else False
            self.src_regs = fields[3].split(',')
            if 'None' in self.src_regs:  # string may have no src_regs
                self.src_regs = []
            self.mem_src_regs = fields[4].split(',')
            if 'None' in self.mem_src_regs:
                self.mem_src_regs = []
            self.is_mem = True if 'True' in fields[5] else False
            self.dest_reg = fields[6] if fields[6] != 'None' else None
            self.max_bits = int(fields[7])
        else: 
            # instructions like addss only affect 32 bits
            if op.endswith('ss'):
                self.max_bits = 32
            
            # push and pop instructions affect stack
            if 'push' in op or 'pop' in op:
                self.is_mem = True

            for control_op in control_ops:
                if self.op in control_op or self.op.startswith(control_op):
                    self.ctrl_flag = True
                    break
        
    def __repr__(self):
        src_regs = self.src_regs
        mem_src_regs = self.mem_src_regs
        if len(src_regs) == 0:
            src_regs = 'None'
        else:
            src_regs = ','.join(src_regs)
        if len(mem_src_regs) == 0:
            mem_src_regs = 'None'
        else:
            mem_src_regs = ','.join(mem_src_regs)
        dest_reg = self.dest_reg
        if dest_reg is None:
            dest_reg = 'None'
        return 'pc:%s op:%s ctrl_flag:%r src_regs:%s mem_src_regs:%s is_mem:%r dest_reg:%s max_bits:%d' % (
            self.pc, self.op, self.ctrl_flag, src_regs, mem_src_regs, \
            self.is_mem, dest_reg, self.max_bits)

    def print_inst(self):
        '''
        This function differs from __repr__ by only printing out the fields
        '''
        src_regs = self.src_regs
        mem_src_regs = self.mem_src_regs
        if len(src_regs) == 0:
            src_regs = 'None'
        else:
            src_regs = ','.join(src_regs)
        if len(mem_src_regs) == 0:
            mem_src_regs = 'None'
        else:
            mem_src_regs = ','.join(mem_src_regs)
        dest_reg = self.dest_reg
        if dest_reg is None:
            dest_reg = 'None'
        return '%s %s %r %s %s %r %s %d' % (
            self.pc, self.op, self.ctrl_flag, src_regs, mem_src_regs, \
            self.is_mem, dest_reg, self.max_bits)

    def _find_reg(self,search_string):
        '''
        Iterates through possible registers, finds possible match
        Args: search_string - string that may contain register
        Returns: regs - string if register(s) found, None otherwise
        '''
        regs = []
        for reg_match in reg_matches:
            match = reg_match.search(search_string)
            if match:
                reg = match.group(0).lstrip('%')
                regs.append(reg)
        if len(regs) > 0:
            regs = ','.join(regs)
        else:
            regs = None
        return regs

    def add_src_reg(self,search_string,is_mem=False):
        '''
        adds appropriate source register to the instruction if it exists
        Args: search_string - string that may contain register
              is_mem - flag that adds to the mem_src_regs field
        '''
        if is_mem_access(search_string):
            is_mem = True
            self.is_mem = True
        reg = self._find_reg(search_string)
        if reg is not None:
            if is_mem:
                if reg not in self.mem_src_regs:
                    self.is_mem = True
                    self.mem_src_regs.append(reg)
            else:
                if reg not in self.src_regs:
                    self.src_regs.append(reg)
    def add_dest_reg(self,search_string):
        '''
        adds appropriate destination register if it exists
        Args: search_string - string that may contain register
        '''
        if not is_mem_access(search_string):
            self.dest_reg = self._find_reg(search_string)
            
            # arithmetic instructions in x86 have both src and dest
            # (ex. add %rax, %rbx; rbx also becomes a src)
            for arithmetic_op in arithmetic_ops:
                if arithmetic_op in self.op:
                    self.add_src_reg(search_string)
                    break
        else:
            self.add_src_reg(search_string,is_mem=True)
    


class inst_database(object):
    def __init__(self, dis_filename):
        '''
        creates instruction database.
        Args: dis_filename - filename of disassembly
        '''
        self.insts = []
        
        f = open(dis_filename, 'rb')
        for line in f:
            line = line[:9] + line[31:]
            # make sure line actually contains contents to parse
            if valid_pattern.match(line) and '(bad)' not in line:
                data = line[2:].rstrip('\r\n').split(':	')
                pc = data[0]
                op = data[1].split(' ', 1)[0]
                reg = []
                # many corner cases in x86, one being a '.' in the op
                if '.' in op:
                    try:
                        op = data[1].split(' ', 1)[1].split(' ')[0]
                        reg_info = data[1].split(' ', 1)[1].split(' ')[1]
                    except:
                        continue
                elif len(data[1].split(' ', 1)) > 1:
                    reg_info = data[1].split(' ', 1)[1]

                inst = instruction(pc,op)
                if 'nop' in op:  # ignore nops
                    self.insts.append(inst)
                    continue
                comma_split = reg_info.lstrip().split(',')
                if 'mov' in op:
                    for comma_sv in comma_split:
                        for segment_reg in segment_regs:
                            if segment_reg in comma_sv:
                                inst.is_mem = True
                                break
                        
                # in x86, the number of src/dest operands varies
                if len(comma_split) == 1:
                    is_src_op = False
                    # src register may be just single register
                    for single_op in single_ops:  # check for insts like push
                        if op in single_op:
                            is_src_op = True
                            src_info = comma_split[0]
                            inst.add_src_reg(src_info)
                            break
                    if not is_src_op:
                        if len(comma_split[0]) > 0:
                            dest_info = comma_split[0]
                            inst.add_dest_reg(dest_info)
                        
                elif len(comma_split) == 2:
                    if 'cmp' in op:
                        inst.add_src_reg(comma_split[0])
                        inst.add_src_reg(comma_split[1])
                    else:
                        src_info = comma_split[0]
                        dest_info = comma_split[-1]
                        inst.add_src_reg(src_info)
                        inst.add_dest_reg(dest_info)

                elif len(comma_split) == 3:
                    src_info = comma_split[1]
                    dest_info = comma_split[-1]
                    inst.add_src_reg(src_info)
                    inst.add_dest_reg(dest_info)
                # usually referring to memory (ex. imul (%rcx,%r8,1),%edx)
                elif len(comma_split) == 4:
                    if comma_split[0].startswith('('):
                        src_info = ','.join(comma_split[0:2])
                        dest_info = comma_split[-1]
                        inst.add_src_reg(src_info,is_mem=True)
                        inst.add_dest_reg(dest_info)
                    elif comma_split[1].startswith('('):
                        src_info = comma_split[0]
                        inst.add_src_reg(src_info)
                        src_info = ','.join(comma_split[1:3])
                        inst.add_src_reg(src_info,is_mem=True)
                    
                self.insts.append(inst)
        f.close()


    def print_database(self, output_filename):
        '''
        prints the database to a file.
        Args: output_filename - name of location of where to save database to
        '''
        wf = open(output_filename,'w') 
        wf.write('PC OP CONTROL_FLAG SRC_REGS SRC_MEM_REGS IS_MEM DEST_REG MAX_BITS\n')
        for inst in self.insts:
            writeln = inst.print_inst() 
            wf.write("%s\n" % writeln)
        wf.close()

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Test Usage: python inst_database.py [dis_file] [out_file]")
        exit()

    f = sys.argv[1]
    wf = sys.argv[2]
    database = inst_database(f)
    database.print_database(wf)
