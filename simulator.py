r'''
	Author: Sungguk Cha
	eMail : sungguk@unist.ac.kr

	RL scheduler project.
	This simulator contains gaussian packet generator and machines to process the packets. Given scheduler, it simulates schedulers to check how well a scheduler performs. 
'''

import numpy as np

class Packet(object):
	def __init__(self, req, time, prio, rel, dead=None):
		'''
			required : int
				required amount of resource
			time	 : int
				processing time
			priority : int
				priority 0 ~ 9 (the lower the higher priority)
			release time : int
				release time of a packet
			dead 	: int
				dead line for the packet
		'''
		self.required	= req
		self.time	= time
		self.priority	= prio
		self.release	= rel
		self.dead	= dead
	def process(self, performance, time):
		self.time -= performance
		if self.time == 0:
			return True
		if self.dead != None:
			if self.dead > time:
				return True
		return False

class Generator(object):
	def __init__(self, rmean, rstd, tmean, tstd, pmean, pstd):
		self.req_mean	= rmean
		self.req_std	= rstd
		self.time_mean	= tmean
		self.time_std	= tstd
		self.prio_mean	= pmean
		self.prio_std	= pstd
	def gen_r(self):
		while True:
			res = np.random.normal(self.req_mean, self.req_std)
			res = int(res[0])
			if 0 <= res:
				return res
	def gen_t(self):
		while True:
			res = np.random.normal(self.time_mean, self.time_std)
			res = int(res[0])
			if res > 0:
				return res
	def gen_p(self):
		while True:
			res = np.random.normal(self.prio_mean, self.prio_std)
			res = int(res[0])
			if 0 <= res and res <= 9:
				return res
	def generate(self, rel):
		req  = self.gen_r()
		time = self.gen_t()
		prio = self.gen_p()
		p = Packet(req, time, prio, rel)
		return p

class Machine(object):
	def __init__(self, resources, performance, cores):
		'''
			resources : int
				number of resources
			performance : int
				performance of each core
			cores : list<Packet>
				cores for Packet load
			ncores : int
				number of cores
			idle : int
				number of idle cores
		'''
		self.resources = resources
		self.performance = performance
		self.cores = [None * i for i in range(cores)]
		self.ncores = cores
		self.idle = cores
		self.readyQ = []
		'''
			Performance evaluator: evaluation metrics
			1. CPU utilization(%): utilization / (time * ncores)
			2. Throughput: done / time
			3. Avg. Turnaround time: turnaround / done
			4. Load average(waiting time): will be reported from simulator
			5. Avg. Response time: respond / done
			+. Avg. priority: priority / done
			+. Avg. scheduling time: will be reported from simulator	
		'''
		self.utilization= 0
		self.done	= 0
		self.turnaround	= 0
		self.respond	= 0
		self.priority	= 0
	def single(self, packet, preemptive=False):
		if preemptive:
			assert False, "preemptive single load is not available.\n	Please use multi load preemtive mode.\n"
		if self.resources < packet.required:
			return
			"Not enough resources"
		for i in range(self.ncores):
			core = self.cores[i]
			if core == None:
				self.cores[i] = packet
				self.resources -= packet.required
				self.idle -= 1
				return
	def multi(self, packets, preemptive=False):
		for i in range(self.ncores):
			if packets[i] == None:
				continue
			if preemptive:
				if self.cores[i] == None:
					if self.resources < packets[i].required:
						continue
						"Not enough resources"
					self.resources -= packets[i].required
					self.cores[i] = packets[i]
					self.idle -= 1
					continue
				if self.resources + self.cores[i].required < packets[i]:
					continue
					"Not enough resources"
				self.resources += self.cores[i].required - packets[i].required
				self.readyQ.append(self.cores[i])
				self.cores[i] = packets[i]
			elif self.cores[i] == None:
				if self.resources < packets[i].required:
					continue
					"Not enough resources"
				self.resources -= packets[i].required
				self.cores[i] = packets[i]
				self.idle -= 1
	def load(self, packet, preemptive=False):
		'''
			packet : Packet list
			len(packet) should be 1 or equal to ncores
			it supports single scheduling and per-core scheduling
		'''
		assert len(packet) == 1 or len(packet) == ncores, \
		"packet should be shape of list<packet> with size 1 or ncores"
		if self.idle == 0:
			return
		if len(packet) == 1:
			self.single(packet[0], preemptive)
		else:
			self.multi(packet, preemptive)

	def process(self, time):
		for i in range(self.ncores):
			if self.cores[i].process(self.performance, time):
				'''
					Packet perishes. Check if 
					1. packet is done
					2. packet is discarded due to its deadline
				'''
				self.idle += 1
				self.resources += self.cores[i].required
				self.cores[i] = None
		

class Simulator(object):
	def __init__(self, generators, scheduler, machine):
		self.time	= 0
		self.generators	= generators
		self.scheduler	= scheduler
		self.machine	= machine
