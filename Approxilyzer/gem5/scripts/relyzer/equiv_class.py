#!/usr/bin/python

# equivalence class data structure (currently used in store_equivalence.py
# and postprocessing.py, TODO: use in control_equivalence.py)
import random


class equiv_class(object):
    def __init__(self,pc,in_string=None,simple=True):
        '''
        initializes equivalence class data structure (use in_string to read
        existing data from file)
        '''
        if in_string is None:
            self.pc = pc
            self.members = []
            self.pop = 0
            self.pilot = None
        else:
            temp = in_string.split(':')
            self.pc = temp[0]
            self.pop = int(temp[1])
            self.pilot = temp[2]
            if not simple:
                self.members = temp[3].lstrip().split()

    def add_member(self,inst_num):
        '''
        adds a member to the equivalence class
        Args: isnt_num - instruction number of dynamic PC to add
        '''
        self.members.append(inst_num)
        self.pop += 1
    
    def remove_member(self,inst_num):
        '''
        removes a member from the equivalence class (to save space).
        Args: inst_num - instruction number of dynamic PC to remove
        '''
        if inst_num in self.members:
            self.members.remove(inst_num)
            self.pop -= 1

    def select_pilot(self,seed_val=1):
        '''
        selects a pilot from the list of members at random.
        Args: (Optional) seed_val - used for making sure pilot selection
        is deterministic
        '''
        random.seed(seed_val)
        if len(self.members) > 0:
            rand_pilot_idx = random.randint(0,len(self.members)-1)
            self.pilot = self.members[rand_pilot_idx]
    
    def set_pilot(self,pilot):
        '''
        sets the pilot if known beforehand.
        Args: pilot - the predetermined pilot.
        '''
        self.pilot = pilot

    def print_equiv_class(self):
        '''
        prints the given equivalence class.
        Returns: output - string of all contents of the equivalence class
        '''
        output = '%s:%d:%s:%s' % (self.pc, self.pop, self.pilot, \
                 ' '.join(self.members))
        return output

class equiv_class_database(object):
    def __init__(self, filename, get_members=False, simple=True):
        '''
        creates a database depending on equiv class file (ctrl or store)
        '''
        # equiv_class_list = open(filename).read().splitlines()[1:]
        self.equiv_class_map = {}
        self.pop_map = {}  # gets population given the equiv id (pilot atm)
        equiv_classes = []
        self.equiv_members_map = {}

        with open(filename) as f:
            f.readline()  # ignore first field
            for item in f:
                equiv_classes.append(equiv_class(None,in_string=item,simple=simple))
        for _equiv_class in equiv_classes:
            # members = _equiv_class.members
            pilot = _equiv_class.pilot
            pop = _equiv_class.pop
            if get_members:
                self.equiv_members_map[pilot] = members
            # for member in members:
            #     self.equiv_class_map[member] = pilot
            self.pop_map[pilot] = pop
    
    def __contains__(self, equiv_id):
        '''
        check if equiv_id exists in db
        '''
        return equiv_id in self.equiv_class_map

    def get_pilot(self, inst_num):
        '''
        gets the pilot of the appropriate equiv class (if it exists)
        '''
        return self.equiv_class_map.get(inst_num, None)

    def get_pop(self, equiv_id):
        '''
        gets the population of the equivalence class
        '''
        return self.pop_map[equiv_id]
    def get_top_pops(self, cutoff):
        '''
        returns the equivalence classes with the largest pop (set by cutoff)
        '''
        total_pop = 0
        pop_equiv_map = {}
        for equiv_id in self.pop_map:
            if self.pop_map[equiv_id] not in pop_equiv_map:
                pop_equiv_map[self.pop_map[equiv_id]] = []
            pop_equiv_map[self.pop_map[equiv_id]].append(equiv_id)
        top_pop = sorted(pop_equiv_map.keys())
        top_pop.reverse()
        top_equiv_ids = []
        for pop in top_pop:
            for equiv_id in pop_equiv_map[pop]:
                total_pop += pop
        cutoff_val = cutoff * total_pop
        curr_pop = 0

        for pop in top_pop:
            for equiv_id in pop_equiv_map[pop]: 
                if curr_pop > cutoff_val:
                    break
                top_equiv_ids.append(equiv_id)
                curr_pop += pop
        return top_equiv_ids
    def get_above_average_pops(self):
        '''
        calculates the average population and returns equiv ids
        that have a population greater than or equal to the average
        '''
        pops = []
        for equiv_id in self.pop_map:
            pops.append(self.pop_map[equiv_id])
        av_pop = sum(pops) / float(len(pops)) 
        equiv_ids = []
        for equiv_id in self.pop_map:
            pop = self.pop_map[equiv_id]
            if pop >= av_pop:
                equiv_ids.append(equiv_id)
        return equiv_ids
        
    def get_members(self, equiv_id):
        '''
        returns members of equiv class (if db was created to do so)
        '''
        return self.equiv_members_map.get(equiv_id, [])
