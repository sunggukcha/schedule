import simulator
from heapq import *


def heapsort(iterable):
	h = []
	for v in iterable:
		heappush(h, value)
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
	def run(self, time, packets, runQ):
		heapQ = []
		for p in packets:
			heapQ.append((p.dead, p))
		for p in runQ:
			headQ.append((p.dead, p))
		heapQ = heapsort(heapQ)
		res = []
		while len(heapQ) > 0:
			d, p = heappop(heapQ)
			# abort
			if time + p.time > d:
				continue
			res.append(p)
			if len(res) == self.n_core:
				return res
		return res
