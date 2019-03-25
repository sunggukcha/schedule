r'''
	Author: Sungguk Cha
	eMail : sungguk@unist.ac.kr

	RL realtime-scheduler project.
	This simulator contains gaussian packet generator and machines to process the packets. Given scheduler, it simulates schedulers to check how well a scheduler performs. 

	Overall design
	
	Packet generator(user) gives simulator packets
	simulator gives the packets to scheduler
	scheduler schedules and return it to simulator
	simulator gives the schedule to the machine
	machine returns with readyQ for scheduler
'''

import numpy as np
import time
import csv

class Logger(object):
	def __init__(self):
		self.lines = [['release', 'dead', 'priority', 'required', 'time']]
	def add(self, line):
		self.lines.append(line)
	def load(self, load_dir):
		with open(load_dir, 'r') as readFile:
			reader = csv.reader(readFile)
			lines = list(reader)
	def write(self, save_dir):
		with open(save_dir, 'w') as writeFile:
			writer = csv.writer(writeFile)
			writer.writerows(lines)
		writeFile.close()
	def getLines(self):
		return self.lines[1:]

class Packet(object):
	def __init__(self, req, time, prio, rel, dead=None):
		'''
			release time : int
				release time of a packet
			dead 	: int
				dead line for the packet
			priority : int
				priority 0 ~ 9 (the lower the higher priority)
			required : int
				required amount of resource
			time	 : int
				processing time
		'''
		self.release	= rel
		self.dead	= dead
		self.priority	= prio
		self.required	= req
		self.time	= time
	def process(self, performance, time):
		self.time -= performance
		if self.time == 0:
			return True
		if self.dead != None:
			if self.dead > time:
				return True
		return False
	def getLine(self):
		res = [self.release, self.dead, self.priority, self.required, self.time]
		return res

class Generator(object):
	def __init__(self, rmean, rstd, tmean, tstd, pmean, pstd, delay):
		'''
			delay : int
				generating delay. time_mean * random(1~delay) will be the delay in practice
		'''
		self.req_mean	= rmean
		self.req_std	= rstd
		self.time_mean	= tmean
		self.time_std	= tstd
		self.prio_mean	= pmean
		self.prio_std	= pstd
		self.delay	= delay
		self.time	= 0
	def _gen_r(self):
		res = np.random.normal(self.req_mean, self.req_std)
		res = int(res[0])
		return max(0, res)
	def _gen_t(self):
		res = np.random.normal(self.time_mean, self.time_std)
		res = int(res[0])
		if res > 0:
			return res
		return 0
	def _gen_p(self):
		res = np.random.normal(self.prio_mean, self.prio_std)
		res = int(res[0])
		res = min(9, max(0, res))
		return res
	def generate(self, rel):
		if self.time > rel:
			return None
		req  = self._gen_r()
		time = self._gen_t()
		prio = self._gen_p()
		if time == 0:
			return None
		p = Packet(req, time, prio, rel)
		self.time += int(self.time_mean * np.random.uniform(1, self.delay))
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
			x. CPU utilization(%): utilization / (time * ncores)
			2. Throughput: done / time
			3. Avg. Turnaround time: turnaround / done
				T_finish - T_release
			4. Load average(waiting time): will be reported from simulator
			x. Avg. Response time: respond / done
				T_commence - T_release
			+. Avg. priority: priority / done
			+. Avg. scheduling time: will be reported from simulator
			x. Execution time:
				realtime scheduling is more about throughput rather than execution time. If there are dependencies between packets like order-hierarchy, then execution could matter but this simulator does not contain packet-dependecy.
		'''
		#self.utilization= 0
		self.done	= 0
		self.turnaround	= 0
		#self.respond	= 0
		self.priority	= 0
	def result(self):
		return [self.done, self.turnaround, self.priority]
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
		self.readyQ.append(packet)
	def multi(self, packets, preemptive=False):
		for i in range(self.ncores):
			if packets[i] == None:
				continue
			p = packets[i]
			if preemptive:
				if self.cores[i] == None:
					if self.resources < p.required:
						self.readyQ.append(p)
						continue
						"Not enough resources"
					self.resources -= p.required
					self.cores[i] = p
					self.idle -= 1
					continue
					"Successfully loaded"
				if self.resources + self.cores[i].required < p.required:
					self.readyQ.append(p)
					continue
					"Not enough resources"
				self.resources += self.cores[i].required - p.required
				self.readyQ.append(self.cores[i])
				self.cores[i] = p
			elif self.cores[i] == None:
				if self.resources < p.required:
					self.readyQ.append(p)
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
		if len(packet) == self.ncores:
			self.multi(packet, preemptive)
		else:
			self.single(packet[0], preemptive)

	def process(self, packets, time, preemptive=False):
		self.load(packets, preemptive)
		for i in range(self.ncores):
			if self.cores[i].process(self.performance, time):
				p = self.cores[i]
				'''
					Packet perishes. Check if 
					1. packet is done
					2. packet is discarded due to its deadline
				'''
				if p.dead <= time:
					self.done += 1
					self.priority += p.priority
					self.turnaround += time - p.release
				self.idle += 1
				self.resources += p.required
				self.cores[i] = None
		res = self.readyQ.copy()
		self.readyQ.clear()
		return self.cores, res

class Simulator(object):
	def __init__(self, generators, scheduler, machine, until):
		self.time	= 0
		self.until	= until
		self.generators	= generators
		self.scheduler	= scheduler
		self.machine	= machine
		self.logger	= Logger()
		self.packets	= []
		self.runQ	= machine.cores
		# evaluation
		self.load	= 0
	def run(self):
		if self.time > self.until:
			result = machine.result()
			print("Throughput: ", result[0] / self.time)
			print("Avg. turnaround: ", result[1] / result[0])
			print("Avg. priority: ", result[2] / result[0])
			print("Avg. load: ", self.load / self.time)
			# scheduling time in plan
			return True
			'Simulation done'
		for gen in self.generators:
			p = gen.generate(self.time)
			if p == None:
				continue
			self.logger.add(p.getLine())
			self.packets.append(p)
		self.load += len(self.packets)
		schedule = self.scheduler.run(self.time, self.packets, self.runQ)
		for d, p in schedule:
			if p in self.packets:
				self.packets.remove(p)					
		self.runQ, readyQ = self.machine.process(schedule, self.time, preemptive=self.scheduler.preempt)
		self.packets += readyQ
		self.time += 1
