import simulator
from heapq import *


def heapsort(iterable):
	h = []
	for v in iterable:
		heappush(h, v)
	return [heappop(h) for i in range(len(h))]

class EDF (object):
	def __init__(self, n_core, preempt=True):
		'''
			n_core: int
				number of cores of a machine. it determines the return shape of a packet list
			preempt: boolean
		'''
		self.n_core	= n_core
		self.preempt	= preempt
		'''
		self.packets	= []
	def add_packet(self, packets):
		for p in packets:
			tup	= (p.dead, p)
			self.packets.append(tup)
		heapsort(self.packets)
		'''
	def prios(self, p):
		if p == None:
			print("ERROR: None packet is in Q")
			exit()
		return (p.dead, p.priority, p.release, p.time, p.required, p)
	def run(self, time, packets, runQ):
		heapQ = []
		for p in packets:
			if p == None:
				print("ERROR: None packet gerenated")
				exit()
			heappush(heapQ, self.prios(p))
		for p in runQ:
			if p == None:
				continue
			heappush(heapQ, self.prios(p))
		#heapQ = heapsort(heapQ)
		res = []
		while len(heapQ) > 0:
			_p = heappop(heapQ)
			p = _p[5]
			d = _p[0]
			# abort
			if time + p.time > d:
				continue
			res.append(p)
			if len(res) == self.n_core:
				return res
		while len(res) < self.n_core:
			res.append(None)
		return res

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T
from models import dnn

class ML(object):
    def __init__(self, ncore, preempt=True):
        self.ncore = ncore
        self.preempt = preempt
        self.packets = []
        self.model = dnn.FC10(nn.BatchNorm1d)
    def run(self, time, packets, runQ):
        '''
            Now it supports single core only.
        '''
        art = add = apr = apt = 0.0
        ct = time
        for p in packets:
            art += p.release
            add += p.dead
            apr += p.priority
            apt += p.time
        art /= len(packets)
        add /= len(packets)
        apr /= len(packets)
        apt /= len(packets)
        head = [ct, art, add, apr, apt]
        res = []
        for p in packets:
            _x = head + [p.release, p.dead, p.priority, p.time]
            _x = torch.as_tensor(np.asarray(_x))
            output = self.model(_x)
            res.append(output)
        index = np.asarray(res).argmax()
        return packets[index]

