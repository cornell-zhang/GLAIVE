import numpy as np
import networkx as nx
import os
import sys
import pprint as pp
import random

labels = []
train = []
node_list = []
node_type = []
bit_loc = []
G = nx.DiGraph()
gl_dir = os.environ.get('GRAPHLEARN')
save_dir = gl_dir + '/gdata/'
test_app = sys.argv[1]
SAMPLES =  int(sys.argv[2])
TRAIN_SAMPLES = int(SAMPLES * 1.0)

map_file = open(gl_dir+'/source_data/num_source/nfile_efile_glearn.map', 'r')
l = map_file.readlines()
map_file.close()
sample_list = [l_.split()[0] for l_ in l]
print(len(sample_list))
print(sample_list)

test_list=[]
app_map = {}
feats_part =[]
feats_all = []
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
                feats_part.append(info[6:-1])
                feats_all.append(info[0:-1])
                if info[-1] == 'Masked':
                    label = 0
                elif(info[-1] == 'SDC:Eggregious'  or info[-1] == 'SDC:Eggregious-pixel_mismatch' or info[-1] == 'SDC:Eggregious-line_num_mismatch'  or info[-1] == 'SDC:Tolerable'):
                    label = 1
                else:
                    label = 2
                labels.append(label)
                #if j < TRAIN_SAMPLES:
                #if 'lu_cb_inst' in sample_list[j] or 'swaptions_inst'in sample_list[j]  or 'blackscholes_16_inst'  in sample_list[j]:
                if test_app in sample_list[j] :
                    train.append(0)
                else:#elif 'lu_cb_bit' in sample_list[j]:
                    train.append(1)
                test_list.append(sample_list[j])
                #id_map[info[0]] = int(info[0])+num_nodes
                node_list.append(i+num_nodes)
                #node_type.append(info[4]) # bit-level graph
                node_type.append(info[4])
                bit_loc.append(info[5])
        with open(edgefile) as ff:
            for i, line in enumerate(ff):
                info = line.split()
                G.add_edge(id_map[info[0]]+num_nodes, id_map[info[1]]+num_nodes)
        #print('Working on Sample ID: ', j)


#---------start split app test data-------------------------        
mh = open(gl_dir+'/gdata/app_decode_test.map', 'w')
for i in app_map.keys():
     mh.write( str(i) + '\t' + str(app_map[i]) + '\n')
mh.close()

start_list = app_map.keys()
print(start_list)
sdc_dir = gl_dir + '/sdc_output_ml_bit/'
sdc_file=sdc_dir + test_app+ '_mlpc'

start_flag=False
with open(sdc_file) as ff:
    for line in ff:
        id_test = int(line.split()[0])
        test_value = line.split()[1]
        if id_test in start_list and start_flag == False :
            print('---test--in-\n')
            #start_list.remove(id_test)
            start_flag = True
            sdc_app = sdc_dir + app_map[id_test]
            sdcfile = open(sdc_app, 'a+')
            sdc_post = sdc_dir + app_map[id_test] +'_post_mlpc.txt'
            sdc_postfile = open(sdc_post, 'a+')
            #sdcfile.write(str(id_test) + '\t' + str(test_value) + '\n')
        if (id_test+1) in start_list and start_flag == True:
            start_flag = False
        #if id_test not in start_list and start_flag == True:
        sdcfile.write(str(id_test) + '\t' + str(test_value) + '\n')
        sdc_postfile.write(feats_all[id_test][1].strip()  + ',')
        if(int(feats_all[id_test][2].strip())== 0):
            sdc_postfile.write('x86'  + ',')
        else:
            sdc_postfile.write('isa'  + ',')
	sdc_postfile.write(feats_all[id_test][3].strip()  + ',')
        for i in range(5,8):
            sdc_postfile.write(feats_all[id_test][i].strip()  + ',')
        sdc_postfile.write(feats_all[id_test][8].strip()  + '::')
        if int(test_value) == 0: 
            test_string = 'Masked'
        elif int(test_value) == 1:
            test_string = random.choice(['SDC:Eggregious','SDC:Eggregious-pixel_mismatch','SDC:Eggregious-line_num_mismatch','SDC:Tolerable'])
        else:
            test_string = 'Detected'
        sdc_postfile.write( test_string + '::')
        if(int(feats_all[id_test][9].strip())== 0):
            sdc_postfile.write('store'  + '::')
        else:
            sdc_postfile.write('ctrl'  + '::')
        if(int(feats_all[id_test][10].strip())== 0):
            sdc_postfile.write('inj'  + '\n')
        else:
            sdc_postfile.write('pruned'  + '\n')

        #if id_test in start_list:
            #sdcfile.close()               

sdc_file=sdc_dir + test_app+ '_rf'

start_flag=False
with open(sdc_file) as ff:
    for line in ff:
        id_test = int(line.split()[0])
        test_value = line.split()[1]
        if id_test in start_list and start_flag == False :
            print('---test--in-\n')
            #start_list.remove(id_test)
            start_flag = True
            sdc_app = sdc_dir + app_map[id_test]
            sdcfile = open(sdc_app, 'a+')
            sdc_post = sdc_dir + app_map[id_test] +'_post_rf.txt'
            sdc_postfile = open(sdc_post, 'a+')
            #sdcfile.write(str(id_test) + '\t' + str(test_value) + '\n')
        if (id_test+1) in start_list and start_flag == True:
            start_flag = False
        #if id_test not in start_list and start_flag == True:
        sdcfile.write(str(id_test) + '\t' + str(test_value) + '\n')
        sdc_postfile.write(feats_all[id_test][1].strip()  + ',')
        if(int(feats_all[id_test][2].strip())== 0):
            sdc_postfile.write('x86'  + ',')
        else:
            sdc_postfile.write('isa'  + ',')
        sdc_postfile.write(feats_all[id_test][3].strip()  + ',')
	for i in range(5,8):
            sdc_postfile.write(feats_all[id_test][i].strip()  + ',')
        sdc_postfile.write(feats_all[id_test][8].strip()  + '::')
        if int(test_value) == 0:
            test_string = 'Masked'
        elif int(test_value) == 1:
            test_string = random.choice(['SDC:Eggregious','SDC:Eggregious-pixel_mismatch','SDC:Eggregious-line_num_mismatch','SDC:Tolerable'])
        else:
            test_string = 'Detected'
        sdc_postfile.write( test_string + '::')
        if(int(feats_all[id_test][9].strip())== 0):
            sdc_postfile.write('store'  + '::')
        else:
            sdc_postfile.write('ctrl'  + '::')
        if(int(feats_all[id_test][10].strip())== 0):
            sdc_postfile.write('inj'  + '\n')
        else:
            sdc_postfile.write('pruned'  + '\n')



print(app_map)
#---------end split app test data-------------------------  

