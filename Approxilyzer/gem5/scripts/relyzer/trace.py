#!/usr/bin/python

class trace_item(object):
    '''
    object used to store individual trace information
    '''
    def __init__(self, items, idx=0):
        self.inst_num = items[0]  # equivalent to gem5's tick
        self.pc = items[1][2:]  # eliminates the '0x' from the PC address
        self.raw_pc = items[1]  # just in case the '0x' is necessary
        self.mem_op = None
        self.mem_addr = None
        self.idx = idx
        if len(items) > 2:
            self.mem_op = items[2]
            self.mem_addr = items[3]

    def __repr__(self):
        return '%s %s %s %s' % \
               (self.inst_num, self.pc, self.mem_op, self.mem_addr)
    
    def is_store(self):
        '''
        determines if pc is a store instruction
        '''
        if self.mem_op is not None:
            return self.mem_op == 'Write'
        return False
                

class trace(object):
    '''
    contains the gem5 trace information (inst_num, pc, (R/W, MemAddr))
    '''
    def __init__(self, filename):
        self.filename = filename
        items = [i.split() for i in open(filename).read().splitlines()]
        self.trace_items = []
        self.trace_idx = 0  # used for iterating through trace
        for i,item in enumerate(items):
            _trace_item = trace_item(item, i)
            self.trace_items.append(_trace_item)

        # also store the index of trace given the inst_num
        self.inst_num_map = {}
        for item in self.trace_items:
            self.inst_num_map[item.inst_num] = item.idx

    def __repr__(self):
        return 'trace from %s of length %d' % \
               (self.filename, len(self.trace_items))

    def __len__(self):
        return len(self.trace_items)
        
    def __getitem__(self, index):
        return self.trace_items[index]
    
    def __iter__(self):
        return self

    def next(self):
        if self.trace_idx == len(self.trace_items):
            self.trace_idx = 0
            raise StopIteration
        else:
            self.trace_idx += 1 
            return self.trace_items[self.trace_idx-1]

    def get_idx(self,inst_num):
        return self.inst_num_map[inst_num]

    def print_trace(self):
        for item in self.trace_items:
            print(item)
    
    def simplify_trace(self):
        '''
        simplifies trace to only include loads/stores
        Returns: simple_trace - simplified trace
        '''
        return [item for item in self.trace_items if item.mem_op is not None]

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('test usage: python trace.py [filename]')
        exit()
    trace_test = trace(sys.argv[1])
    trace_test.print_trace()
