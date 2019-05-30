'''
	Author:	Sungguk Cha
	eMail : sungguk@unist.ac.kr
	Realtime scheduler simulation
'''

from simulator import *
from scheduler import *
import argparse
import json

def gen_packets(self, csv):
    packets = []
    f = open(csv, 'r')
    reader = csv.reader(f)
    for line in reader[1:]:
        cfg = line.split()
        print(line)
        p = Packet(cfg[3], cfg[4], cfg[2], cfg[0], cfg[1])
        packets.append(p)
    return packets


if __name__ == '__main__':
	with open('config.json') as data_file:
		data = json.loads(data_file.read())

	if data["scheduler"] == "edf":
		scheduler = EDF(data["machine"]["ncore"])

	_m	= data["machine"]

	for i in range (100):
		saveas = "./dataset/dataset" + str(i) + ".csv"
		log = "./dataset/dataset.txt"

		gens = []
		for c in data["generators"]:
			gen = Generator(c['rmean'], c['rstd'], c['tmean'], c['tstd'], c['pmean'], c['pstd'], c['delay'])
			gens.append(gen)
		machine = Machine(_m["resources"], _m["performance"], _m["ncore"])
		simulator = Simulator(gens, scheduler, machine, 100000)
		simulator.run(saveas=saveas,log=log)
