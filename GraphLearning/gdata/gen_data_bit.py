import os
import pprint as pp
import random
import sys
import numpy as np
import networkx as nx

test_app = sys.argv[1]
def convert(integer, length):
    bool_list = [0] * length
    bool_list[integer] = 1
    return bool_list

def maxminnor(cols):
	temp = []
	for i in range(len(cols)):
		temp.append(int(cols[i],16))
		#print(temp[i])
	temp1 = temp
	temp1.sort()
	max_value = temp1[len(temp)-1]
	min_value = temp1[0]
	for i in range(len(temp)):
		#cols[i] = '0x'+cols[i]
		#temp[i] = int(temp[i],16)
		temp[i] = (temp[i]-min_value)/(max_value-min_value)
	return temp

labels = []
train = []
node_list = []
node_type = []
bit_loc = []
op_type =[]

G = nx.DiGraph()
gl_dir = os.environ.get('GRAPHLEARN')
save_dir = gl_dir + '/gdata/'
temp_file = open( save_dir + 'bugfile', 'w')


SAMPLES = int(sys.argv[2])
TRAIN_SAMPLES = int(SAMPLES * 1)

map_file = open(gl_dir+'/source_data/num_source/nfile_efile_glearn.map', 'r')
l = map_file.readlines()
map_file.close()
sample_list = [l_.split()[0] for l_ in l]
print(len(sample_list))
print(sample_list)

app_map = {}
feats_part =[]
#feats_6=[]
#feats_7=[]
#feats_8=[]
#feats_9=[]
for j in range(0, SAMPLES):
    print(j)
    #if 'TRIT_' not in sample_list[j] and 'RS232_' not in sample_list[j]:
    #    continue
    if os.path.exists((gl_dir+'/source_data/num_source/{}.nodelist').format(j)):
        nodefile = (gl_dir+'/source_data/num_source/{}.nodelist').format(j)
        edgefile = (gl_dir+'/source_data/num_source/{}.edgelist').format(j)
        num_nodes = len(node_list)
        id_map = {}
        with open(nodefile) as ff:
            for i, line in enumerate(ff):
                info = line.split()
                id_map[info[0]] = i
                if i==0 :
                    #app_map[sample_list[j]] = num_nodes
                    app_map[num_nodes] = sample_list[j]
                    #print('%d %s \n' % (i+num_nodes, info[0]))
                #attr = maxminnor(info[1])
                #G.add_node(i+num_nodes, attribute=info[1]) #4:-1
                G.add_node(i+num_nodes, attribute=info[4:-1]) #4:-1
                feats_part.append(info[7:-1])
                #if (info[6] != '0' and info[6] != '1') or (info[7] != '0' and info[7] != '1') or (info[8] != '0' and info[8] != '1') or (info[8] != '0' and info[9] != '1'):
                if ('SDC' not in info[-1]) and ('Masked' not in info[-1]) and ('Detected' not in info[-1]):
                    #temp_file.write(info[0] + '\n')
                    print(info[0])
                if info[-1] == 'Masked':
                    label = 0
                elif(info[-1] == 'SDC:Eggregious' or info[-1] == 'SDC:Eggregious-pixel_mismatch' or info[-1] == 'SDC:Eggregious-line_num_mismatch'  or info[-1] == 'SDC:Tolerable'):
                    label = 1
                else:
                    label = 2
                labels.append(label)
                #if 'blackscholes_1_bit' in sample_list[j] or 'blackscholes_2_bit' in sample_list[j] or 'blackscholes_3_bit' in sample_list[j]  or 'blackscholes_bit' in sample_list[j]  or 'blackscholes_16_bit' in sample_list[j]:
                if test_app in sample_list[j]:
                    train.append(0)
                else:#elif 'lu_cb_bit' in sample_list[j]:
                    train.append(1)
                #id_map[info[0]] = int(info[0])+num_nodes
                node_list.append(i+num_nodes)
                #node_type.append(info[4]) # bit-level graph
                op_type.append(info[4])
                node_type.append(info[5])
                bit_loc.append(info[6])
                temp_file.write(info[-1] + '\n')
        with open(edgefile) as ff:
            for i, line in enumerate(ff):
                info = line.split()
                G.add_edge(id_map[info[0]]+num_nodes, id_map[info[1]]+num_nodes)
        #print('Working on Sample ID: ', j)

#temp_file.write(node_type)

print('Train size: ' + str(len(train)))
print('Labels size: ' + str(len(labels)))

nx.write_edgelist(G, save_dir+test_app+"_all.edgelist")
#nx.write_nodelist(G, save_dir+"all.nodelist")
with open(save_dir+test_app+"_labels.txt", "w") as ff:
    for i in range(len(labels)):
        ff.write(str(i))
        ff.write(" ")
        ff.write(str(labels[i]))
        ff.write(" ")
        ff.write(str(train[i]))
        ff.write("\n")

all_op = {}# reg type in x86
for x in op_type:
    if x not in all_op:
        all_op[x] = len(all_op)
num_ops = len(all_op)
#print(all_op)
print('Size of opcode type vocubulary; ', num_ops)

all_type = {}# reg type in x86
for x in node_type:
    if x not in all_type:
        all_type[x] = len(all_type)
num_types = len(all_type)
#print(all_type)
print('Size of reg type vocubulary; ', num_types)

all_loc = {}# bit localation 
for x in bit_loc:
    if x not in all_loc:
        all_loc[x] = len(all_loc)
num_loc = len(all_loc)
#print('Size of bit loc vocubulary; ', num_loc)
feats0 = []
feats1 = []
feats2 = []
#feats = maxminnor(node_type)
#print(feats)


for x in op_type:
    feats0.append(convert(all_op[x], num_ops))

for x in node_type:
    feats1.append(convert(all_type[x], num_types))
#print(feats)
for x in bit_loc:
    feats2.append(convert(all_loc[x],num_loc))	

#features = np.array(feats)
features0 = np.array([np.array(x) for x in feats0])
features1 = np.array([np.array(x) for x in feats1])
features2 = np.array([np.array(x) for x in feats2])
#features6 = np.array( feats_6)
#features7 = np.array( feats_7)
#features8 = np.array( feats_8)
#features9 = np.array( feats_9)

feats_part_new = []
for x in feats_part:
    feats_part_new.append([int(a) for a in x])
        
features_part = np.array([np.array(x) for x in feats_part_new])
#print(features_part.ndim)
print(features_part.shape)
features1 = np.concatenate((features0,features1),axis=1)
features1 = np.concatenate((features1,features2),axis=1)
features1 = np.concatenate((features1,features_part),axis=1)

np.save(save_dir+test_app+"_feats.npy", features1)

#print(len(node_list))
#print(labels)
#print(node_type)
#print(len(G.edges()))

