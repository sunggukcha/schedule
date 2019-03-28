# Scheduling simulator

It consists of
1. Packet generators,
2. Schedulers,
3. (Virtual) Machine and
4. Simulator.

### Packet generators

### Schedulers

### Machine
It runs Banker's algorithm which prevents deadlock at all.

### Simulator

Packet generators generate packets accroding to given gauss distribution. Scheduler schedules given packets and machine state. With the schedule, simulator runs the machine and evaluates with following criteria.

1. CPU utilization
2. Throughput
3. Turnaround time
4. Load average(waiting time)
5. Response time
6. Avg. priority
7. Scheduling time
