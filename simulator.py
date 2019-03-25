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

def print_core(core):
	pp = []
	for p in core:
		if p == None:
			pp.append(p)
		else:
			pp.append(p.release)
	return pp

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
			writer.writerows(self.lines)
		writeFile.close()
	def getLines(self):
		return self.lines[1:]
	def getLen(self):
		return len(self.lines)-1

class Packet(object):
	def __init__(self, req, time, prio, rel, dead):
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
		if self.time <= 0:
			return True
		if self.dead != None:
			if self.dead <= time:
				return True
		return False
	def getLine(self):
		res = [self.release, self.dead, self.priority, self.required, self.time]
		return res
	def __lt__(self, other):
		return self.time < other.time

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
		return max(0, int(res))
	def _gen_t(self):
		res = np.random.normal(self.time_mean, self.time_std)
		res = int(res)
		if res > 0:
			return res
		return 0
	def _gen_p(self):
		res = np.random.normal(self.prio_mean, self.prio_std)
		res = int(res)
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
		p = Packet(req, time, prio, rel, int(rel + time * np.random.uniform(1, self.delay)))
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
		self.cores = [None for i in range(cores)]
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
		self.dead	= 0
		self.util	= 0
		self.done	= 0
		self.turnaround	= 0
		#self.respond	= 0
		self.priority	= 0
	def result(self):
		return [self.done, self.turnaround, self.priority, self.util]
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
		loaded=0
		npacket=0
		for p in self.cores:
			if p != None:
				loaded += 1
		for p in packets:
			if p != None:
				npacket += 1
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
		if loaded + npacket != (self.ncores-self.idle) + len(self.readyQ):
			print("ERROR in multi loading")
			print("loaded: ", loaded)
			print("npacket: ", npacket)
			print("working: ", self.ncores-self.idle)
			print("readyQ: ", len(self.readyQ))
			exit()
	def load(self, packet, preemptive=False):
		'''
			packet : Packet list
			len(packet) should be 1 or equal to ncores
			it supports single scheduling and per-core scheduling
		'''
		assert len(packet) == 1 or len(packet) == self.ncores, \
		"packet should be shape of list<packet> with size 1 or ncores. %d is given." % len(packet)
		if self.idle == 0:
			return
		if len(packet) == self.ncores:
			self.multi(packet, preemptive)
		else:
			self.single(packet[0], preemptive)

	def process(self, packets, time, preemptive=False):
		self.load(packets, preemptive)
		print(time, print_core(self.cores))
		for i in range(self.ncores):
			p = self.cores[i]
			if p == None:
				continue
			if self.cores[i].process(self.performance, time):
				p = self.cores[i]
				'''
					Packet perishes. Check if 
					1. packet is done
					2. packet is discarded due to its deadline
				'''
				if p.dead > time:
					self.done += 1
					self.priority += p.priority
					self.turnaround += time - p.release
				else:
					self.dead += 1
				self.idle += 1
				self.resources += p.required
				self.cores[i] = None
		res = self.readyQ.copy()
		self.readyQ.clear()
		self.util += self.ncores - self.idle
		'''
		cc = 0
		for p in self.cores:
			if p == None:
				cc += 1
		if self.idle < 0 or self.idle > self.ncores or cc != self.idle:
			print("ERROR: BUG IN IDLE COUNT")
			exit()
		'''
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
		while self.time < self.until:
			for gen in self.generators:
				p = gen.generate(self.time)
				if p == None:
					continue
				self.logger.add(p.getLine())
				self.packets.append(p)
			self.load += len(self.packets)
			schedule = self.scheduler.run(self.time, self.packets, self.runQ)
#			'''
			for p in schedule:
				if p in self.packets:
					self.packets.remove(p)
#			'''

			self.runQ, readyQ = self.machine.process(schedule, self.time, preemptive=self.scheduler.preempt)
			for p in readyQ:
				if p in self.packets:
					self.packets.remove(p)
					#print("ERROR: packet replicated")
					#exit()
			self.packets += readyQ
			for p in self.runQ:
				if p in self.packets:
					self.packets.remove(p)
					#print("ERROR: packet replicated!")
					#exit()
			self.time += 1
			_r = 0
			for c in self.runQ:
				if c != None:
					_r += 1
			if self.logger.getLen() != self.machine.done + len(self.packets) + _r:
				print("ERROR in packet delivery")
				print("%d packets generated" % self.logger.getLen())
				print("%d packets done" % self.machine.done)
				print("%d packets in Q" % len(self.packets))
				print("%d pacekts in runQ" % _r)
				exit()
			'''
			ppp = []
			for p in self.runQ:
				if p == None:
					ppp.append(p)
				else:
					ppp.append(p.release)
			print(self.time, " : ", ppp)
			'''
			#print("%d packets and %d inQ" % (len(self.packets), len(self.runQ)))
		self.logger.write("log.csv")
		print(self.logger.getLen(), "packets generated")
		print(self.machine.done, "packets are done")
		print(self.machine.dead, "packets are dead")
		#self.logger.write(log.csv)
		result = self.machine.result()
		if result[0] == 0:
			print("NOTHING PROCESSED")
			return False
		print("CPU utilization: ", round(result[3] / (self.machine.ncores * self.until) * 100, 2))
		print("Throughput: ", result[0] / self.until)
		print("Avg. turnaround: ", result[1] / result[0])
		print("Avg. priority: ", result[2] / result[0])
		print("Avg. load: ", self.load / self.until)
		# scheduling time in plan
		return True
		'Simulation done'
