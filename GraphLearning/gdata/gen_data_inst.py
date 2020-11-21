import numpy as np
import networkx as nx
import os
import sys
import pprint as pp
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
G = nx.DiGraph()
gl_dir = os.environ.get('GRAPHLEARN')
save_dir = gl_dir + '/gdata/'

SAMPLES = int(sys.argv[2])
#TRAIN_SAMPLES = int(SAMPLES * 1.0)

map_file = open(gl_dir+'/source_data/num_source/nfile_efile_glearn.map', 'r')
l = map_file.readlines()
map_file.close()
sample_list = [l_.split()[0] for l_ in l]
print(len(sample_list))
print(sample_list)

weight=[]
app_map = {}
feats_part =[]
for j in range(0, SAMPLES):
    print(j)
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
                G.add_node(i+num_nodes, attribute=info[1:5]) #4:-1
                feats_part.append(info[2:4])
                weight.append(float(info[5]))
                label = info[6:9]	
                labels.append(label)
                #if 'lu_cb_inst' in sample_list[j] or 'swaptions_inst'in sample_list[j]  or 'blackscholes_16_inst'  in sample_list[j]:
                if test_app in sample_list[j] :
                    train.append(0)
                else:#elif 'lu_cb_bit' in sample_list[j]:
                    train.append(1)
                node_list.append(i+num_nodes)
                node_type.append(info[1])
                bit_loc.append(info[4])
        with open(edgefile) as ff:
            for i, line in enumerate(ff):
                info = line.split()
                G.add_edge(id_map[info[0]]+num_nodes, id_map[info[1]]+num_nodes)
        

print('Train size: ' + str(len(train)))
print('Labels size: ' + str(len(labels)))

nx.write_edgelist(G, save_dir+test_app+"_all.edgelist")
#nx.write_nodelist(G, save_dir+"all.nodelist")
with open(save_dir+test_app+"_labels.txt", "w") as ff:
    for i in range(len(labels)):
        ff.write(str(i))
        ff.write(" ")
        ff.write(str(labels[i][0]))
        ff.write(" ")	
        ff.write(str(labels[i][1]))
        ff.write(" ")
        ff.write(str(labels[i][2]))
        ff.write(" ")
        ff.write(str(train[i]))
        ff.write("\n")

all_type = {}# reg type in x86
for x in node_type:
    if x not in all_type:
        all_type[x] = len(all_type)
num_types = len(all_type)
print('Size of reg type vocubulary; ', num_types)

all_loc = {}# bit localation 
for x in bit_loc:
    if x not in all_loc:
	all_loc[x] = len(all_loc)

num_loc = len(all_loc)
	
print('Size of bit loc vocubulary; ', num_loc)

feats = []
#feats = maxminnor(node_type)
#print(feats)
for x in node_type:
    feats.append(convert(all_type[x], num_types))

feats1 = []
for x in bit_loc:
    feats1.append(convert(all_loc[x],num_loc))	


features = np.array([np.array(x) for x in feats])
features1 = np.array([np.array(x) for x in feats1])

feats_part_new = []
for x in feats_part:
    feats_part_new.append(map(eval,x))
         

features_part = np.array([np.array(x) for x in feats_part_new])
features = np.concatenate((features,features1),axis=1)
features = np.concatenate((features,features_part),axis=1)
print(features)

np.save(save_dir+test_app+"_feats.npy", features)

#print(len(node_list))
#print(labels)
#print(node_type)
#print(len(G.edges()))

