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
                G.add_node(i+num_nodes, attribute=info[1:5]) #4:-1
                feats_part.append(info[2:4])
                weight.append(float(info[5]))
                label = info[6:9]	
                labels.append(label)
                #if j < TRAIN_SAMPLES:
                #if 'lu_cb_inst' in sample_list[j] or 'swaptions_inst'in sample_list[j]  or 'blackscholes_16_inst'  in sample_list[j]:
                if test_app in sample_list[j] :
                    train.append(1)
                else:#elif 'lu_cb_bit' in sample_list[j]:
                    train.append(0)
                #id_map[info[0]] = int(info[0])+num_nodes
                node_list.append(i+num_nodes)
                #node_type.append(info[4]) # bit-level graph
                node_type.append(info[1])
                bit_loc.append(info[4])
        with open(edgefile) as ff:
            for i, line in enumerate(ff):
                info = line.split()
                G.add_edge(id_map[info[0]]+num_nodes, id_map[info[1]]+num_nodes)
        #print('Working on Sample ID: ', j)
        

#---------start split app test data-------------------------  
ml = sys.argv[3]
start_list = app_map.keys()
print(start_list)
sdc_dir = gl_dir+'/sdc_output_classic/'
sdc_file=sdc_dir + test_app +'_' + ml

start_flag=False
with open(sdc_file) as ff:
    for line in ff:
        id_test = int(line.split()[0])
        mask_rate =float( line.split()[1])
        sdc_rate =float( line.split()[2])
        crash_rate =float( line.split()[3])
        if id_test in start_list and start_flag == False :
            print('---test--in-\n')
            #start_list.remove(id_test)
            mask_sum = 0.0
            sdc_sum = 0.0
            crash_sum = 0.0
            start_flag = True
            sdc_app = sdc_dir + app_map[id_test] +'_' +ml+'_overall'
            sdcfile = open(sdc_app, 'w')
            sdc_app_inst = sdc_dir + app_map[id_test] + '_'+ ml + '.sdclist'
            sdcfile_inst = open(sdc_app_inst, 'w')
	    line_num = 0
            #sdcfile.write(str(id_test) + '\t' + str(test_value) + '\n')
        if (id_test+1) in start_list and start_flag == True:
            start_flag = False
        #if id_test not in start_list and start_flag == True:
        mask_sum = mask_sum + mask_rate*weight[id_test]
        sdc_sum = sdc_sum + sdc_rate*weight[id_test]
        crash_sum = crash_sum + crash_rate*weight[id_test]
        #if id_test not in start_list and start_flag == False :
            #sdcfile.write(str(mask_sum) + '\t' + str(sdc_sum) + '\t' +str(crash_sum) +'\n')
        sdcfile_inst.write('%d ' %line_num)
        sdcfile_inst.write('\t'+str(mask_rate) + '\t' + str(sdc_rate) + '\t' +str(crash_rate) +'\n')
	line_num = line_num +1
        #if id_test in start_list:
            #sdcfile.close()  

sdcfile.write(str(mask_sum) + '\t' + str(sdc_sum) + '\t' +str(crash_sum) +'\n')
print(app_map)
#---------end split app test data-------------------------  


