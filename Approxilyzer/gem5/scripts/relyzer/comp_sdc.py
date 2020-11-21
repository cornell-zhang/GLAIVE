#!/usr/bin/python

# use the gem5-approxilyzer output to construct the bit_graph,reg_graph,inst_graph. 
# This convertor is used to indentify the nodes are approximate(reliable, changing the label rules) or not.
# To collect more attributes, we detail the instruction info for related nodes through importing the instruction database. This part is optional

#AUTHOR: jiajia jiao
#Time: Feb,2020

import os
import sys

#the instruction database is used to add more attributes for each graph node  
from inst_database import instruction
from datetime import datetime as dt
class node(object):
	def __init__(self,name):
		self.name = name
		self.label = True
		self.adjs = []
		self.children = []
		self.dep_list = []
		
	def print_node(self):
		'''
        This function prints the fields
		
		'''
		return '%s  %r' % (app_name+'_'+str(self.name), self.label)
	def is_depend(self,instn):
		'''
        This function identifies the node matches with other node or not
		
		'''
		match = False
		for i in self.dep_list:
			if (instn.pc == i):
				return  True
		return match
		
	def add_child(self,node):
		'''
        if the given node is the adjacent of current node's parent, insert the edges 
			between current node and the reg node's children
		'''
		if(is_match(self,node.pc)):
			self.children.append(node)
	
	def add_adjs(self,node):
		'''
        if the given  node is the adjacent of current node's parent, insert the edges 
			between current node and the reg node's children
        ''' 
		if(node.name != self.name):
			#self.adjs.append(adj)
			self.adjs.append(node)
    
	def print_edges(self):
		'''
        print the edges from the current node
        '''
		for adj in self.adjs:
			if( len(self.adjs) !=0):
				return '%s %s' %(app_name+'_'+str(self.name), app_name+'_'+str(adj.name))

class block_node(node):
	def __init__(self,name):
		self.name = name
		self.pc = name
		# can add more instruction attributes by calling inst_database
		
		self.label = True
		self.adjs = []
		self.children = []
		self.parent = []
		self.dep_list = []

class inst_node(node):
	def __init__(self,name,pc,label):
		self.name = name
		self.pc = pc
        	self.sdc = 0.0
		self.mask = 0.0
		self.crash = 1.0
		self.weight = 0.0
		# can add more instruction attributes by calling inst_database
		
		self.label = label
		self.adjs = []
		self.children = []
		self.parent = []
		self.dep_list = []
	
	def print_node(self):
		'''
        This function prints the fields
		
		'''
		#return '%s %s %r' % (app_name+'_'+str(self.name),self.pc, self.label)
        	return '%s %s %f %f %f %f %r' % (app_name+'_'+str(self.name),self.pc,self.mask, self.sdc, self.crash, self.weight,self.label)
	
	def add_dependence(self,in_string):
		'''
        This function identifies the node matches with other node or not
		
		'''
	#	deps=in_string.split(',')[1:]
		for i in in_string:
			self.dep_list.append(i)
		
	def is_depend(self,node):
		'''
        This function identifies the node matches with other node or not
		
		'''
		match = False
		for i in self.dep_list:
			if (node.pc == i):
				return  True
		return match
        
        
	def add_adjs_ctrl(self):
        	if( len(self.parent) != 0):
            		if(self.parent[0].dep_list[-1] == self.pc):
                		for adj_parent in self.parent[0].adjs:
                    			for child in adj_parent.children:
                        			if(child.pc == adj_parent[0].dep_list[0]):
                            				self.adjs.append(child)
		

	
	def print_node_more_attribs(self,dis_parsed_file):
		'''
        add more attributes for nodes
        '''
		
		db_info = [i for i in open(dis_parsed_file).read().splitlines()[1:]]
		insts = [instruction(None,None,i) for i in db_info]
		
		for i in insts:
			src_regs = i.src_regs
			mem_src_regs = i.mem_src_regs
			if len(src_regs) == 0:
				src_regs = 'None'
			else:
				src_regs = ','.join(src_regs)
			if len(mem_src_regs) == 0:
				mem_src_regs = 'None'
			else:
				mem_src_regs = ','.join(mem_src_regs)
			dest_reg = i.dest_reg
			if dest_reg is None:
				dest_regi = 'None'
			if i.ctrl_flag == True:
                		ctrl_flag = 1
            		else:
                		ctrl_flag = 0
            		if i.is_mem == True:
                		is_mem = 1
            		else:
                		is_mem = 0
			if i.pc == self.pc:		
				#return '%s %s %s %r %s %s %r %s %d %r' % (
					#self.name, self.pc, i.op, i.ctrl_flag, src_regs, mem_src_regs, i.is_mem, dest_reg, i.max_bits,self.label)
				return '%s %s %d %d %d %f %f %f %f ' % (app_name+'_'+str(self.name),i.op,ctrl_flag,i.is_mem,i.max_bits,self.weight,self.mask, self.sdc, self.crash)
     	def print_sdc(self):
            	return '%d %f %f %f ' % (self.name,self.mask, self.sdc, self.crash)

class reg_node(node):
	def __init__(self,name,pc,reg,type,label):
		self.name = name
		self.pc = pc
		self.reg = reg
		self.type = type
		self.label = label
		self.adjs = []
		self.parent = []
		self.children = []
	
	def print_node(self):
		'''
        This function prints the fields
        '''
		return '%s %s %s %s %r' % (app_name+'_'+str(self.name),self.pc, self.reg, self.type, self.label)

	def is_match(self,in_string):
		
		match = False
		if(self.pc == in_string ): 
			match = True
		return match
	
	def add_adjs(self):
		'''
        if the given reg node is the adjacent of current bit node's parent, insert the edges 
			between current node and the reg node's children
        '''
		#adjs between different instructions
		if(len(self.parent) != 0):
			for adj_parent in self.parent[0].adjs:
				for child in adj_parent.children:
					if(child.name != self.name):
						self.adjs.append(child)
		
		#adjs between the same instructions
		if(len(self.parent) != 0):
			for adj in self.parent[0].children:
				if(self.type == 'SRC' or self.type == 'MEM_SRC' and adj.type == 'DEST'):
					if(child.name != self.name):
						self.adjs.append(adj)
	
	def print_node_more_attribs(self,dis_parsed_file):
		'''
        add more attributes for nodes
        '''
		
		db_info = [i for i in open(dis_parsed_file).read().splitlines()[1:]]
		insts = [instruction(None,None,i) for i in db_info]
		
		for i in insts:
			if i.pc == self.pc:
				for j in i.src_regs:
					if self.reg == j:
						self.type = 'SRC'
						break
				for j in i.mem_src_regs:
					if self.reg == j:
						self.type = 'MEM_SRC'
						break
				if self.reg == i.dest_reg:
					self.type = 'DEST'
					
				return '%s %s %s %s %s %r' % (
					self.name, self.pc, self.reg, self.type, i.op, self.label)

			
	
class bit_node(node):
	def __init__(self,name,in_string):
	
		'''
		initializes an bit_node object Args: name - node of name to insert the edges)
              in_string - pc,reg,cycle_num and other fileds from database
              label, outcome as approx or not, reliable or not
		'''
		
		self.name = name
		self.pc = ''
		self.isa = ''
		self.tick = ''
		self.reg = ''
		self.bit = -1
		self.reg_type = ''
		self.src_dest = ''
		self.category = '' # used for fine classification
		self.str_ctl = ''
		self.inj = '' # whether to add the node attributes? or may used for single program self-prediction?
		self.label = False
		self.adjs = [] #  make the edges 
		self.parent = [] # merge multiple bit nodes into a reg_node ????

        # initialize variables from existing output file
		if in_string != '':
			#self.name = in_string.split('::')[0]
			temp = in_string.split('::')[0]
			fields = temp.split(',')
			self.pc = fields[0]
			self.isa = fields[1]
			self.tick = fields[2]
			self.reg = fields[3]
			self.bit = fields[4]
			self.reg_type = fields[5] 
			self.src_dest = fields[6]
			outcome = in_string.split('::')[1]
			sep = ';'
			if(sep in outcome):
				outcome=outcome.split(';')[0]
			self.category = outcome
			if(outcome == 'Masked' or outcome == 'SDC:Tolerable'):
				self.label = True 
			else: 
				self.label = False
				#print('comecome is %s \n' %outcome)
			self.str_ctl = in_string.split('::')[2]
			self.inj = in_string.split('::')[3]

	def print_node(self):
		#print('bit node own \n')
		'''
		This function prints the fields
		'''
		#return '%s %s %s %s %r' % (self.name,self.pc, self.reg, self.bit, self.label)
		#return '%s %s %s %s %s %s %s %s %s %s %s %r' % (self.name, self.pc, self.isa, self.tick, self.reg, self.bit, self.reg_type, self.src_dest,self.str_ctl, self.inj, self.category, self.label)
		#pc = int('0x'+ self.pc,16)
		if self.isa == 'x86':
			isa = 0
		else:
			isa = 1 
		if self.str_ctl== 'store':
			str_ctl = 0 
		else:
			str_ctl = 1 
		if self.inj == 'inj':
			inj = 0 
		else:
			inj = 1
		if self.label == False :
			label = 0 
		else:
			label = 1
		
		return '%s %s %s %s %s %s %s %s %s %s %s' % (app_name+'_'+str(self.name), self.pc,isa,  self.tick, self.reg, self.bit, self.reg_type, self.src_dest, str_ctl, inj,self.category)
		#return '%s %s %s %s %s %s %s %s %s %s %r' % (app_name+'_'+str(self.name), self.pc,isa,  self.tick, self.reg, self.bit, self.reg_type, self.src_dest, str_ctl, inj,self.label)
		#return '%s %s %s %s %s' %(self.name, pc, isa, self.tick, self.category)
	def is_match(self,pc,reg):
		'''
        This function identifies the node matches with other node or not
        '''
		match = False
		if(self.pc == pc and self.reg == reg): 
			match = True
		return match

	def add_adjs(self):
		'''
        if the given reg node is the adjacent of current bit node's parent, insert the edges 
			between current node and the reg node's children
        '''
		if(len(self.parent) != 0):
			for adj_parent in self.parent[0].adjs:
				for child in adj_parent.children:
					self.adjs.append(child)
     
	#ifdef MORE_ATTRIB
	def print_node_more_attribs(self,dis_parsed_file):
		'''
        add more attributes for nodes
        '''
		
		db_info = [i for i in open(dis_parsed_file).read().splitlines()[1:]]
		insts = [instruction(None,None,i) for i in db_info]
		
		for i in insts:
			if i.pc == self.pc:
				return '%s %s %s %s %s %s %s %s %s %s %s %s %r' % (self.name, self.pc, i.op, self.isa, self.tick, self.reg, self.bit, self.reg_type, self.src_dest,self.str_ctl, self.inj, self.category, self.label)
	#endif		

	

class node_database(object):
	def __init__(self, inputfile):
		self.nodes=[]
		
	def print_nodes_database(self, outfile_nodes):
		'''
		prints the database to a file.
		Args: output_filename - name of location of where to save database to
		'''
		wf = open( outfile_nodes,'w') 
		#wf.write('NAME PC REG BIT OUTCOME\n')
		for node in self.nodes:
			writeln = node.print_node() 
			wf.write("%s\n" % writeln)
		wf.close()
		
	def print_nodes_more_database(self, input_dis, outfile_nodes):
		'''
		prints the database to a file.
		Args: output_filename - name of location of where to save database to
		'''
		wf = open( outfile_nodes,'w') 
		for node in self.nodes:
			writeln = node.print_node_more_attribs(input_dis) 
			wf.write("%s\n" % writeln)
		wf.close()
		
	def print_edges_database(self, outfile_edges):
		'''
		prints the database to a file.
		Args: output_filename - name of location of where to save database to
		'''
		
		wf = open(outfile_edges,'w') 
		#wf.write('SRC DEST\n')
		for node in self.nodes:
			if(len(node.adjs)!=0):
				writeln = node.print_edges() 
				wf.write("%s\n" % writeln)
		wf.close()
			
class bn_database(node_database):
	def __init__(self, inputfile):
		'''
		creates bit node database.
		Args: infile
		'''
		self.nodes=[]
		node_list=open(inputfile).read().splitlines()
		for line in node_list:
			#print('the file read line is \n')
			node = bit_node(len(self.nodes),line)
			self.nodes.append(node)

		
class rn_database(node_database):
	def __init__(self, bn_db):
		'''
		creates bit node database.
		Args: infile
		'''
		self.nodes=[]
		for bn in bn_db.nodes:
			if(len(self.nodes)==0):
				rn = reg_node(len(self.nodes),bn.pc,bn.reg,'',bn.label)
				bn.parent.append(rn) 
				rn.children.append(bn)
				self.nodes.append(rn)
			else:
				flag = False
				for rn in self.nodes:
					if(bn.is_match(rn.pc,rn.reg)):
						rn.label = (rn.label and bn.label)
						bn.parent.append(rn) 
						rn.children.append(bn)
						flag = True
						break
					else:
						continue
				if(flag == False):
					rn = reg_node(len(self.nodes),bn.pc,bn.reg,'',bn.label)
					bn.parent.append(rn) 
					rn.children.append(bn)
					self.nodes.append(rn)						
						
	
class instn_database(node_database):
	def __init__(self, rn_db):
		'''
		creates bit node database.
		Args: infile
		'''
		self.nodes=[]
		for rn in rn_db.nodes:
			if(len(self.nodes)==0):
				instn = inst_node(len(self.nodes),rn.pc,rn.label);
				rn.parent.append(instn) 
				instn.children.append(rn)
				self.nodes.append(instn)
			else:
				flag= False
				for instn in self.nodes:
					if(rn.is_match(instn.pc)):
						instn.label = instn.label and rn.label
						rn.parent.append(instn)
						instn.children.append(rn)
						flag = True
						break
					else:		
						continue
				if(flag == False):
					instn = inst_node(len(self.nodes),rn.pc,rn.label);
					rn.parent.append(instn) 
					instn.children.append(rn)
					self.nodes.append(instn)
	
	def load_dep(self,input_dep):
		dep_lines = open(input_dep).read().splitlines()
		
		for line in dep_lines:
			for instn in self.nodes:
				if(len(instn.dep_list) == 0 and instn.pc == line.split(',')[0]):
					instn.add_dependence(line.split(',')[1:])
					break
				else:
					continue
		
	def construct_dep(self):
		for instn in self.nodes:
			i = 0
			for temp in self.nodes:
				if(instn.is_depend(temp)):
					instn.add_adjs(temp)
					i = i+1
					#print ('add adj for instruction graph \n')
				if( i >= len(instn.dep_list)):
					break		
    	def comput_sdc(self,bn_db):
		#overall_num = 0.0
        	for instn in self.nodes:
            		total_num = 0.0 # record all bit faults for each instruction
            		correct_num = 0.0
            		sdc_num = 0.0
            		for rn in instn.children:
                		for bn in rn.children:
                    			total_num = total_num + 1
                    			if( bn.category == 'Masked'):
                        			correct_num = correct_num +1
                    			elif(bn.category == 'SDC:Eggregious' or bn.category == 'SDC:Eggregious-line_num_mismatch'  or bn.category == 'SDC:Tolerable'):
						#print(sdc_num)
                        			sdc_num = sdc_num +1
            		if(total_num !=0):
			#instn.sdc = float(total_num)
				instn.sdc = sdc_num/total_num
				instn.mask = correct_num/total_num
				instn.crash = 1-instn.sdc-instn.mask
				instn.weight = total_num/len(bn_db.nodes)
    	def print_sdc(self,outfile_sdc):
        	wf = open(outfile_sdc,'w') 
		for node in self.nodes:
			writeln = node.print_sdc() 
			wf.write("%s\n" % writeln)
		wf.close()
    
#block level graph based on control flow graph
class block_database(node_database):
	def __init__(self, cfg_node, cfg_edge, inst_db):
		'''
		creates block node database.
		Args: infile
		'''
		self.nodes=[]
		node_list=open(cfg_edge).read().splitlines()
		children_list=open(cfg_node).read().splitlines()

		for line in node_list:
			#print('the file read line is \n')
			node = block_node(line)
			for child in children_list:
				if line == child.split(',')[0]:
					#print(child)
					node.dep_list = child.split(',')
			self.nodes.append(node)
            
        	for i in range(0,len(self.nodes)-1,1):
			self.nodes[i].add_adjs(self.nodes[i+1])
		
        	'''
		for line in node_list:
            		for child in children_list:
                		if line == child.split(',')[0]:
                    			node = block_node(child.split(',')[-1])
                    			node.dep_list = child.split(',')
                    			self.nodes.append(node)
                    
        	for i in range(0,len(self.nodes)-1,1):
			self.nodes[i].add_adjs(self.nodes[i+1])    
       		'''
		
        
		for instn in inst_db.nodes:
			for bbn in self.nodes:
				if instn.pc.strip() == bbn.name.strip():
					bbn.label =  instn.label
				if(instn.pc in bbn.dep_list):
					bbn.label =  instn.label
					bbn.label = bbn.label and instn.label
					instn.parent.append(bbn)
					bbn.children.append(instn)
		
def comput_program_sdc(instn_db):
	total_sdc=0.0
	total_mask=0.0
	total_crash=1.0
	for instn in instn_db.nodes:
		total_sdc = total_sdc + instn.sdc*instn.weight
		total_mask = total_mask + instn.mask*instn.weight
	total_crash = 1- total_sdc - total_mask
	print(total_mask)
	print(total_sdc)
	print(total_crash)
'''
the following part is for input, output and function call
four-level graphs are constructed: bit-level,reg-level,inst-level and block-level
'''		
if len(sys.argv) != 4 :
	print ('Usage: python comp_sdc.py [app_name] [isa] [config_ml]')
	exit()
app_name=sys.argv[1]
isa = sys.argv[2]
ml = sys.argv[3]
# more from instruction database

'''
more_attrib = False  #default configuration
#sys.argv[3] = 'fewer'
if(len(sys.argv) ==4 ):
	if(sys.argv[3] == 'more'):
		more_attrib = True
	elif(sys.argv[3] == 'fewer'):
		more_attrib = False
	else:
		print ('configure the nodes attributes by two options: more or fewer')
'''
approx = os.environ.get('APPROXGEM5')
approx_dir = approx + '/Approxilyzer'
apps_dir = approx_dir + '/workloads/' + isa + '/apps/' + app_name
app_prefix = apps_dir + '/' + app_name

if ml == 'gl':
	infile = app_prefix + '_bit_post.txt'
	outfile_inst_sdc = app_prefix + '_inst_gl.sdclist'
elif ml == 'rf':
	infile = app_prefix + '_bit_post_rf.txt'
	outfile_inst_sdc = app_prefix + '_bit_rf.sdclist'
#elif ml == 'mlpc':
else:
	infile = app_prefix + '_bit_post_mlpc.txt'
	outfile_inst_sdc = app_prefix + '_bit_mlpc.sdclist'
#infile = app_prefix + '_postprocess.txt'
#infile = app_prefix + '_bit_post.txt'
#infile = app_prefix + '_bit_post_rf.txt'
input_dep = app_prefix + '_dep.txt'
dis_infile = app_prefix + '_parsed.txt'

outfile_bit_nodes =  app_prefix + '_bit.nodelist'
outfile_bit_edges = app_prefix + '_bit.edgelist'

outfile_reg_nodes =  app_prefix + '_reg.nodelist'
outfile_reg_edges = app_prefix + '_reg.edgelist'

outfile_inst_nodes = app_prefix + '_inst.nodelist'
outfile_inst_edges = app_prefix + '_inst.edgelist'
#outfile_inst_sdc = app_prefix + '_bit_rf.sdclist'
#outfile_inst_sdc = app_prefix + '_inst_gl.sdclist'
#outfile_inst_sdc = app_prefix + '_inst_fi.sdclist'

cfg_node = app_prefix + '_cfg_node.txt'
cfg_edge = app_prefix + '_cfg_edge.txt'

outfile_bb_nodes = app_prefix + '_bb.nodelist'
outfile_bb_edges = app_prefix + '_bb.edgelist'

print('start-time', dt.now().strftime("%m/%d/%Y %H:%M:%S"))
#construct nodes and build the relation between different levels
bn_db = bn_database(infile)
#bn_db.print_nodes_database(outfile_bit_nodes)
rn_db = rn_database(bn_db)
instn_db = instn_database(rn_db)

bbn_db = block_database(cfg_node, cfg_edge,instn_db)
#bbn_db.print_nodes_database(outfile_bb_nodes)
#bbn_db.print_edges_database(outfile_bb_edges)

#print the nodes for different levels

#instn_db.load_dep(input_dep)
#instn_db.construct_dep()
instn_db.comput_sdc(bn_db)

comput_program_sdc(instn_db)
instn_db.print_sdc(outfile_inst_sdc)
print('end-time', dt.now().strftime("%m/%d/%Y %H:%M:%S"))
 
'''
if more_attrib == True:
	bn_db.print_nodes_more_database(dis_infile,outfile_bit_nodes)
	rn_db.print_nodes_more_database(dis_infile,outfile_reg_nodes)
	instn_db.print_nodes_more_database(dis_infile,outfile_inst_nodes)
else:
	bn_db.print_nodes_database(outfile_bit_nodes)
	rn_db.print_nodes_database(outfile_reg_nodes)
	instn_db.print_nodes_more_database(dis_infile,outfile_inst_nodes)
	#instn_db.print_nodes_database(outfile_inst_nodes)


# add the edges via determing the adjs between different PCs/instructions
#instn_db.load_dep(input_dep)
#instn_db.construct_dep()
#instn_db.comput_sdc()

#print the edges for different levels

for instn in instn_db.nodes:
	instn.add_adjs_ctrl();
instn_db.print_edges_database(outfile_inst_edges)

for rn in rn_db.nodes:
	rn.add_adjs()
rn_db.print_edges_database(outfile_reg_edges)

for bn in bn_db.nodes:
	bn.add_adjs()
bn_db.print_edges_database(outfile_bit_edges)
'''
