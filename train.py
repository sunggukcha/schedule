import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T

from models import dnn

### env. configs
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

### model config
model = dnn.FC10(nn.BatchNorm1d)

### training config
epoch = 1000
learning_rate = 0.01
criterion = nn.CrossEntropyLoss()
#loss = criterion(output, target)

import csv
def get_packets(csv):
    packets = []
    f = open(csv, 'r')
    reader = csv.reader(f)
    for line in reader[1:]:
        cfg = line.split()
        print(line)
        p = Packet(cfg[3], cfg[4], cfg[2], cfg[0], cfg[1])
        packets.append(p)
    return packets

from simulator import *
from scheduler import *
import argparse, json
from tqdm import tqdm
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default=None, help="model parameters")
    return parser.parse_args()

if __name__ == '__main__':
	args = get_args()
    # load model
	
	with open('config.json') as data_file:
		data = json.loads(data_file.read())
	scheduler = ML(1)
	_m = data["machine"]

	lr = learning_rate
	tbar = tqdm(range(epoch))
	for i in tbar:
		optimizer = torch.optim.Adam(scheduler.model.parameters(), lr=lr)
		f = open('./dataset/dataset.txt', 'r')
		lines = f.readlines()
		loss = 0.0
		for line in lines:
			load, thru, prio = line.split()
			load = str(load); thru = int(thru); prio = float(prio)
			gens = []
			machine = Machine(_m["resources"], _m["performance"], _m["ncore"])
			simulator = Simulator(gens, scheduler, machine, 100000, packets=get_pacekts(load))
			out_t, out_p = simulator.run()
			loss = criterion(out_t, thru) + criterion(out_p, prio)
			optimizer.zero_grad()
			loss.backward()
			optimizer.step()
			tbar.set_description('Train loss: %.3f' % loss)
		if i > 0:
			if ploss <= loss:
				lr = lr/2
		ploss = loss
