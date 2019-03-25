'''
	Author:	Sungguk Cha
	eMail : sungguk@unist.ac.kr
	Realtime scheduler simulation
'''

from simulator import *
from scheduler import *
import argparse
import json

if __name__ == '__main__':
	with open('config.json') as data_file:
		data = json.loads(data_file.read())

	if data["scheduler"] == "edf":
		scheduler = EDF(data["machine"]["ncore"])

	gens = []
	for c in data["generators"]:
		gen = Generator(c['rmean'], c['rstd'], c['tmean'], c['tstd'], c['pmean'], c['pstd'], c['delay'])
		gens.append(gen)

	_m	= data["machine"]
	machine = Machine(_m["resources"], _m["performance"], _m["ncore"])

	simulator = Simulator(gens, scheduler, machine, 1000)
	simulator.run()
