import torch
import torch.nn as nn
from torch.nn import init
from torch.autograd import Variable
import sys
import numpy as np
import time
import random
from datetime import datetime as dt
import pprint as pp

from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import classification_report

from collections import defaultdict
from collections import OrderedDict as ODict

from graphsage.encoders import Encoder
from graphsage.aggregators import MeanAggregator
from graphsage.plot_confusion_matrix import plot_confusion_matrix

from argparse import ArgumentParser

"""
Simple supervised GraphSAGE model for directed graph as well as examples running the model
on the EDA datasets.
"""
#test_app =  'astar_bit'
class SupervisedGraphSage(nn.Module):

    def __init__(self, num_classes, enc):
        super(SupervisedGraphSage, self).__init__()
        self.enc = enc
        wgts = [1, 1, 1]
        wgts = torch.from_numpy(np.asarray(wgts)).float()
        self.xent = nn.CrossEntropyLoss(weight=wgts)
        #self.xent = nn.CrossEntropyLoss()

        self.weight = nn.Parameter(torch.FloatTensor(num_classes, enc.embed_dim))
        init.xavier_uniform(self.weight)

    def forward(self, nodes):
        embeds = self.enc(nodes)
        scores = self.weight.mm(embeds)
	#print(scores.t()[0])
        return scores.t()

    def loss(self, nodes, labels):
        scores = self.forward(nodes)
        return self.xent(scores, labels.squeeze())

def sdcOutput(test,true_value,pred_value,test_app):
        gl_dir = os.environ.get('GRAPHLEARN')
        output_dir = gl_dir + '/sdc_output/'
        #output_dir = "path..../sdc_output/"
        output_file = output_dir + test_app + '_sdc_output'
        wf = open(output_file,'w')
        for i, line in enumerate(test):
            writeln = str(line) + ' ' + str(true_value[line]) + ' ' + str(pred_value[i])
            wf.write("%s \n" % writeln)
        wf.close()

def load_graph_data(test_app):
    gl_dir = os.environ.get('GRAPHLEARN')
    data_dir = gl_dir + '/gdata'
    feat_data = np.load(("{}/"+test_app+"_feats.npy").format(data_dir))
    num_nodes = feat_data.shape[0]
    labels = np.empty((num_nodes,1), dtype=np.int64)
    train = []
    test  = []
    with open(("{}/"+test_app+"_labels.txt").format(data_dir)) as fp:
        for i,line in enumerate(fp):
            info = line.strip().split()
            labels[int(info[0])] = int(info[1])
            #labels[int(info[0])] = info[1]
            if int(info[2]) == 1:
                train.append(int(info[0]))
            else:
                test.append(int(info[0]))

    adj_lists = defaultdict(lambda: defaultdict(set))
    with open(("{}/"+test_app+"_all.edgelist").format(data_dir)) as fp:
        for i,line in enumerate(fp):
            info = line.strip().split()
            paper1 = int(info[0])
            paper2 = int(info[1])
            adj_lists[paper1]["out"].add(paper2)
            adj_lists[paper2]["in"].add(paper1)
    return feat_data, labels, adj_lists, train, test

def pre_set_search(node,adj_lists):
    pre_set = {}
    pre_set.add(node)
    if(len(adj_list[node]["in"])==0):
        return pre_set
    else:
        for pre in adj_list[node]["in"]:
            pre_set = pre_set + pre_set_search(pre,adj_lists)

def precedent_adj(node, adj_lists):
    pre_adj = {}
    pre_set = pre_set_search(node,adj_lists)
    for i in pre_set:
        pre_adj[i] = adj_lists[i]


def post_set_search(node,adj_lists):
    post_set = {}
    post_set.add(node)
    if(len(adj_list[node]["out"])==0):
        return post_set
    else:
        for post in adj_list[node]["out"]:
            post_set = post_set + post_set_search(post,adj_lists)

def successor_adj(node,adj_lists):
    post_adj = {}
    post_set = post_set_search(node,adj_lists)
    for i in post_set:
        post_adj[i] = adj_lists[i]

def train_graph(epoch, num_batch, batch_size, labels, train, optimizer, graphsage):
    times = []
    LOSS = 0.0

    for e in range(epoch):
        for i in range(num_batch):
            if i < num_batch-1:
                batch_nodes = train[i*batch_size: i*batch_size + batch_size]
            else:
                batch_nodes = train[i*batch_size: len(train)]
            start_time = time.time()
            optimizer.zero_grad()
            loss = graphsage.loss(batch_nodes,\
                Variable(torch.LongTensor(labels[np.array(batch_nodes)])))
            loss.backward()
            optimizer.step()
            end_time = time.time()
            times.append(end_time-start_time)
            if i % 100 == 0:
                print("The {}-th epoch ".format(e), "{}-th batch".format(i), \
                        "Loss: ", loss.item())
            LOSS = loss.item()
    #print('this is graphsage.model for its scores')
    #print(graphsage.forward(train))
    #print(graphsage.forward(test))

    if len(train) < 100000:
        train_output = graphsage.forward(train)

        precision = precision_score(labels[train], train_output.data.numpy().argmax(axis=1), \
                average="macro")#, labels=[1])
                #average="weighted")
        recall = recall_score(labels[train], train_output.data.numpy().argmax(axis=1), \
                average="macro")# labels=[1])
                #average="weighted")
        accuracy = accuracy_score(labels[train], train_output.data.numpy().argmax(axis=1), \
                )
        f1 = f1_score(labels[train], train_output.data.numpy().argmax(axis=1), \
                average="macro")#, labels=[1])
                #average="weighted")
        print("train Precision: ", precision)
        print("train Recall: ", recall)
        print("train Accuracy: ", accuracy)
        print("train macro F1: ", f1)

        print(classification_report(labels[train], train_output.data.numpy().argmax(axis=1), digits=3))

        cm = plot_confusion_matrix(labels[train], train_output.data.numpy().argmax(axis=1), \
                np.array([0, 1, 2]), title='Confusion matrix, without normalization')

        print(cm)

    ### Inference on large graph, avoid out of memory
    else:
        pred = []
	chunk_size = 8
        for j in range(len(train)//chunk_size):
            if j < (len(train)//chunk_size-1):
                train_output = graphsage.forward(train[j*chunk_size:(j+1)*chunk_size])
            else:
                train_output = graphsage.forward(train[j*chunk_size:len(train)])
            pred += (train_output.data.numpy().argmax(axis=1)).tolist()

        precision = precision_score(labels[train], np.asarray(pred), \
                average="macro")#, labels=[1])
                #average="weighted")
        recall = recall_score(labels[train], np.asarray(pred), \
                average="macro")#, labels=[1])
                #average="weighted")
        accuracy = accuracy_score(labels[train], np.asarray(pred), \
                )
        f1 = f1_score(labels[train], np.asarray(pred), \
                average="macro")# labels=[1])
                #average="weighted")

        cm = plot_confusion_matrix(labels[train], np.asarray(pred), \
                np.array([0,1,2]), title='Confusion matrix, without normalization')

        print("train Precision: ", precision)
        print("train Recall: ", recall)
        print("train Accuracy: ", accuracy)
        print("train F1: ", f1)


        print(classification_report(labels[train], np.asarray(pred), digits=3))

    return graphsage, times, LOSS


def infer_graph(test, graphsage, labels, chunk_size,test_app):

    if len(test) < 100000:
        test_output = graphsage.forward(test)

        precision = precision_score(labels[test], test_output.data.numpy().argmax(axis=1), \
                average="macro")#, labels=[1])
                #average="weighted")
        recall = recall_score(labels[test], test_output.data.numpy().argmax(axis=1), \
                average="macro")#, labels=[1])
                #average="weighted")
        accuracy = accuracy_score(labels[test], test_output.data.numpy().argmax(axis=1), \
                )
        f1 = f1_score(labels[test], test_output.data.numpy().argmax(axis=1), \
                average="macro")#, labels=[1])
                #average="weighted")
        sdcOutput(test,labels, test_output.data.numpy(),test_app)
        print("Test Precision: ", precision)
        print("Test Recall: ", recall)
        print("Test Accuracy: ", accuracy)
        print("Test F1: ", f1)

        print(classification_report(labels[test], test_output.data.numpy().argmax(axis=1), digits=3))

        cm = plot_confusion_matrix(labels[test], test_output.data.numpy().argmax(axis=1), \
                np.array([0, 1]), title='Confusion matrix, without normalization')

        print(cm)

    ### Inference on large graph, avoid out of memory
    else:
        pred = []
        for j in range(len(test)//chunk_size):
            if j < (len(test)//chunk_size-1):
                test_output = graphsage.forward(test[j*chunk_size:(j+1)*chunk_size])
            else:
                test_output = graphsage.forward(test[j*chunk_size:len(test)])
            pred += (test_output.data.numpy().argmax(axis=1)).tolist()

        precision = precision_score(labels[test], np.asarray(pred), \
                average="macro")#, labels=[1])
                #average="weighted")
        recall = recall_score(labels[test], np.asarray(pred), \
                average="macro")#, labels=[1])
                #average="weighted")
        accuracy = accuracy_score(labels[test], np.asarray(pred), \
                )
        f1 = f1_score(labels[test], np.asarray(pred), \
                average="macro")#, labels=[1])
                #average="weighted")

        sdcOutput(test,labels,np.asarray(pred),test_app)
        cm = plot_confusion_matrix(labels[test], np.asarray(pred), \
                np.array([0, 1,2]), title='Confusion matrix, without normalization')

        print("Test Precision: ", precision)
        print("Test Recall: ", recall)
        print("Test Accuracy: ", accuracy)
        print("Test F1: ", f1)

        print(classification_report(labels[test], np.asarray(pred), digits=3))

    return precision, recall, accuracy, f1, cm

def printTable1(myDict, colList=None):
    if not colList:
        colList = list(myDict[0].keys() if myDict else [])
    myList = [colList]

    for key in myDict.keys():
        if type(myDict[key]) is list:
            list_ = [str(x) for x in myDict[key]]
            myList.append([key] + list_)
        else:
            myList.append([key, str(myDict[key])])

    colSize = [max(map(len, col)) for col in zip(*myList)]
    formatStr = '^  ' + '  |  '.join(["{{:^{}}}".format(i) for i in colSize])  + '  |'
    #myList.insert(1, ['-' * i for i in colSize])

    content = ''

    for item in myList:
        content = content + formatStr.format(*item) + '\n'

    return content


def main():

    parser = ArgumentParser()
    parser.add_argument('-e', '--epoch', help='Number of epochs for training', \
            dest='epoch', type=int, required=True)
    parser.add_argument('-b', '--batchsize', help='Training batch size', \
            dest='batch_size', type=int, required=True)
    parser.add_argument('-c', '--chunksize', help='Inference chunk size', \
            dest='chunk_size', type=int, required=True)
    parser.add_argument('-r', '--random_shuffle', action='store_true', \
            help='Shuffle training data set', dest='shuffle', default=False)
    parser.add_argument('-a', '--app for test', help='application name for test', \
            dest='testapp', required=True)

    options = parser.parse_args()
    gl_dir = os.environ.get('GRAPHLEARN')
    #log_dir = 'path..../glog/'
    log_dir = gl_dir + '/glog/'

    #Commented out as per Chenhui's suggestion to introduce randomness
    #in training data via random permutation
    if not options.shuffle:
        np.random.seed(1)
        random.seed(1)
    test_app=options.testapp
    print("before-load-time stamp:", dt.now().strftime("%m/%d/%Y %H:%M:%S"))
    feat_data, labels, adj_lists, train, test = load_graph_data(test_app)
    num_nodes = feat_data.shape[0]
    feat_dim = feat_data.shape[1]
    #hidden_dim = 64
    hidden_dim = 128
    features = nn.Embedding(num_nodes, feat_dim)
    features.weight = nn.Parameter(torch.FloatTensor(feat_data), requires_grad=False)
    #features.cuda()

    agg1 = MeanAggregator(features, cuda=True)
    enc1 = Encoder(features, feat_dim, hidden_dim, adj_lists, agg1, gcn=False, cuda=False)
    agg2 = MeanAggregator(lambda nodes : enc1(nodes).t(), cuda=False)
    enc2 = Encoder(lambda nodes : enc1(nodes).t(), enc1.embed_dim, hidden_dim, adj_lists, agg2,
            base_model=enc1, gcn=False, cuda=False)
    agg3 = MeanAggregator(lambda nodes : enc2(nodes).t(), cuda=False)
    enc3 = Encoder(lambda nodes : enc2(nodes).t(), enc2.embed_dim, hidden_dim, adj_lists, agg3,base_model=enc2, gcn=False, cuda=False)
    enc1.num_samples = 5
    enc2.num_samples = 5
    enc3.num_samples = 5

    graphsage = SupervisedGraphSage(3, enc3)

    optimizer = torch.optim.Adam(filter(lambda p : p.requires_grad, graphsage.parameters()), \
            lr=0.001)#,weight_decay=5e-4)

    epoch = options.epoch
    batch_size = options.batch_size
    chunk_size = options.chunk_size
    num_batch = len(train)//batch_size

    if not options.shuffle:
        #NOTE: Train
	print("before-train-time stamp:", dt.now().strftime("%m/%d/%Y %H:%M:%S"))
        graphsage, times, LOSS = train_graph(epoch, num_batch, batch_size, labels, \
                train, optimizer, graphsage)

        #NOTE: Infer
        print("after-train-time and before-infer-time stamp:", dt.now().strftime("%m/%d/%Y %H:%M:%S"))
        precision, recall, accuracy, f1, cm = infer_graph(test, graphsage, labels, chunk_size,test_app)

	print("after-infer-time stamp:", dt.now().strftime("%m/%d/%Y %H:%M:%S"))

        #NOTE: Summarize

        now_time = dt.now().strftime("%m/%d/%Y %H:%M:%S")
        mean_batch_time = np.mean(times)

        print("Average batch time for training:", mean_batch_time)
        print('Final loss at the end of the training: ' + str(LOSS) + '\n\n')
        print("Test Precision: ", precision)
        print("Test Recall: ", recall)
        print("Test Accuracy: ", accuracy)
        print("Test F1: ", f1)

        fh = open(log_dir + '/' + str(epoch) + '_' + str(batch_size) + \
                '_' + str(chunk_size) + '.txt', 'w')

        fh.write('Timestamp: ' + now_time + '\n\n')
        fh.write('Final loss at the end of the training: ' + str(LOSS) + '\n\n')
        fh.write('Average batch time for training: ' + str(mean_batch_time) + '\n\n')
        fh.write("Test Precision: " + str(precision) + '\n')
        fh.write("Test Recall: " + str(recall) + '\n')
        fh.write("Test Accuracy: " + str(accuracy) + '\n')
        fh.write("Test F1: " + str(f1) + '\n')
        fh.write(str(cm))

        fh.close()
    else:
        #NOTE: Introducing randomness
        stability_stat_ = {}
        for i in range(0, 5):
            random.shuffle(train)
            print("Training on the {}-th random shuffled data ".format(i))

            #NOTE: Train
	    print("before-train-time stamp:", dt.now().strftime("%m/%d/%Y %H:%M:%S"))
            graphsage, times, LOSS = train_graph(epoch, num_batch, batch_size, labels, \
                    train, optimizer, graphsage)

            #NOTE: Infer
	    print("after-train-time and before-infer-time stamp:", dt.now().strftime("%m/%d/%Y %H:%M:%S"))
            precision, recall, accuracy, f1, cm = infer_graph(test, graphsage, labels, chunk_size,test_app)
            print("after -infer-time stamp:", dt.now().strftime("%m/%d/%Y %H:%M:%S"))

            #NOTE: Store stat
            stability_stat_[str(i)] = [precision, recall, accuracy, f1]
            print('\n\n')

        stability_stat = ODict(sorted(stability_stat_.items(), key=lambda t: t[1][1], reverse=True))
        del stability_stat_

        pp.pprint(stability_stat)

        sh = open(log_dir + '/' + 'stability_stat.table', 'w')
        scontent = printTable1(stability_stat, \
                ['Shuffle No', 'Precision', 'Recall', 'Accuracy', 'F1']
                )
        sh.write(scontent)
        sh.close()

        del stability_stat

    return


if __name__ == "__main__":
    main()
