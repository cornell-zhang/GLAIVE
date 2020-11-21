#!/usr/bin/python

class x86_register(object):
    def __init__(self):
        self.reg_alias_map = {
                'ax':'rax','bx':'rbx','cx':'rcx','dx':'rdx','si':'rsi', \
                'di':'rdi', \
                'sp':'rsp', 'bp':'rbp', 'ip':'rip', \
                'al':'rax','bl':'rbx','cl':'rcx','dl':'rdx', \
                'ah':'rax','bh':'rbx','ch':'rcx','dh':'rdx', \
                'eax':'rax','ebx':'rbx','ecx':'rcx','edx':'rdx', \
                'esi':'rsi','edi':'rsi', 'eip':'rip', \
                'esp':'rsp', 'ebp':'rbp', 'rip':'rip', \
                'rax':'rax','rbx':'rbx','rcx':'rcx','rdx':'rdx', \
                'rsi':'rsi','rdi':'rdi', \
                'rsp':'rsp', 'rbp':'rbp', 'rip':'rip', \
                'r8':'r8','r9':'r9','r10':'r10','r11':'r11',  \
                'r12':'r12','r13':'r13','r14':'r14','r15':'r15', \
                'xmm0':'xmm0','xmm1':'xmm1','xmm2':'xmm2','xmm3':'xmm3', \
                'xmm4':'xmm4','xmm5':'xmm5','xmm6':'xmm6','xmm7':'xmm7', \
                'xmm8':'xmm8','xmm9':'xmm9','xmm10':'xmm10',
                'xmm11':'xmm11','xmm12':'xmm12','xmm13':'xmm13', \
                'xmm14':'xmm14','xmm15':'xmm15', \
                'fpr0':'fpr0','fpr1':'fpr1','fpr2':'fpr2','fpr3':'fpr3', \
                'fpr4':'fpr4','fpr5':'fpr5','fpr6':'fpr6','fpr7':'fpr7'
        }
        self.half_regs = ['ah', 'bh', 'ch', 'dh', 'al', 'bl', 'cl', 'dl']

        self.reg_size_map = {
                'ax':2,'bx':2,'cx':2,'dx':2,'si':2, \
                'di':2, 'sp':2, 'bp':2, 'ip':2, \
                'al':1,'bl':1,'cl':1,'dl':1, \
                'ah':-1,'bh':-1,'ch':-1,'dh':-1, \
                'eax':3,'ebx':3,'ecx':3,'edx':3, \
                'esi':3,'edi':3, 'esp':3, 'ebp':3, 'eip':3, \
                'rax':4,'rbx':4,'rcx':4,'rdx':4, \
                'rsi':4,'rdi':4, 'rsp':4, 'rbp':4, 'rip':4, \
                'r8':4,'r9':4,'r10':4,'r11':4,  \
                'r12':4,'r13':4,'r14':4,'r15':4, \
                'xmm0':4,'xmm1':4,'xmm2':4,'xmm3':4, \
                'xmm4':4,'xmm5':4,'xmm6':4,'xmm7':4, \
                'xmm8':4,'xmm9':4,'xmm10':4,
                'xmm11':4,'xmm12':4,'xmm13':4, \
                'xmm14':4,'xmm15':4, \
                'fpr0':4,'fpr1':4,'fpr2':4,'fpr3':4, \
                'fpr4':4,'fpr5':4,'fpr6':4,'fpr7':4
        }

    def get_raw_reg_size(self, reg):
        '''
        given an x86 register as input, return its size (in bits)
        '''
        reg_size = -1
        if reg in self.reg_size_map:
            curr_size = self.reg_size_map[reg]
            # registers like "ah" are set to -1 in map_size_map[reg]
            if curr_size < 3:
                reg_size = abs(curr_size * 8)
            elif curr_size == 3:
                reg_size = 32
            elif curr_size == 4:
                reg_size = 64
        return reg_size
        

    def is_alias(self, reg_1, reg_2):
        '''
        determines if a register alias results in equivalent names. One example
        is %ax and %rax, which both refer to simply %rax.
        Args: reg_1 - first register to compare against
              reg_2 - second register to compare against
        Returns: True if there is an alias, False otherwise
        '''
        if reg_1 not in self.reg_alias_map:
            raise ValueError('reg_1 %s is not a valid x86 register' % reg_1) 
        if reg_2 not in self.reg_alias_map:
            raise ValueError('reg_2 %s is not a valid x86 register' % reg_2) 
        
        if reg_1 in self.half_regs and reg_2 in self.half_regs:
            return reg_1 == reg_2
        return self.reg_alias_map[reg_1] == self.reg_alias_map[reg_2] 

class x86_def_register(object):
    def __init__(self, reg_name, def_pc):
        self.reg_set = x86_register()
        self.def_pc = def_pc
        self.reg_name = reg_name
        self.def_reg = self.reg_set.reg_alias_map[reg_name]
        self.reg_size = self.reg_set.reg_size_map[reg_name]
        self._64_32 = None
        self._32_16 = None
        self._16_8 = None
        self._8_0 = None
        
        # used to iterate through bit_ranges that are active
        self.bit_ranges = [self._8_0, self._16_8, self._32_16, self._64_32]

        self._update_pc_bit_ranges(self.reg_size, self.def_pc)

    def __repr__(self):
        reg_info = '%s %s' % (self.def_pc, self.reg_name)
        for bit_range_pc in self.bit_ranges:
            if bit_range_pc is not None:
                reg_info += ' %s' % bit_range_pc  # assuming string for now...
            else:
                reg_info += ' %r' % bit_range_pc
        return reg_info
        

    def _update_pc_bit_ranges(self, reg_size, pc, use=False):
        '''
        updates the pc information for either the def or first use of the reg.
        For example: PC 1: mov rax, rcx
                     PC 2: add ecx, edx
        First, rcx is 64 bits, so all the bit ranges will set their PC to 1.
        Next, ecx is 32 bits, so only the bit ranges 0 to 32 will set their PC
        to 2. This function is called each time either a register is created,
        accessed by a first-use, or a new def is updated.
        '''
        if reg_size == -1:  # special case for regs like 'ah'
            self.bit_ranges[1] = pc
        else:
            for i in range(reg_size):
                self.bit_ranges[i] = pc

    def update_def(self, def_reg, def_pc):
        '''
        updates the def when tracking across basic blocks. 
        '''
        def_reg_size = self.reg_set.reg_size_map[def_reg]
        self._update_pc_bit_ranges(def_reg_size, def_pc)

    def update_first_use(self, bit_range_idx, use_pc):
        if self.bit_ranges[bit_range_idx] == self.def_pc:
            self.bit_ranges[bit_range_idx] = use_pc
        



if __name__ == '__main__':

    import sys

    if len(sys.argv) == 2:
        reg = sys.argv[1]
        x86_regs = x86_register()
        print(x86_regs.get_raw_reg_size(reg))
    else:
        x86_regs = x86_register()
        print('%%ax aliases to %%eax? %r' % x86_regs.is_alias('ax','eax'))
        print('%%ax aliases to %%ebx? %r' % x86_regs.is_alias('ax','ebx'))
