from subprocess import run, PIPE
import random
from NodeOld import *
from random import randint
import threading
import math
from utils import MachinesIPs, NODES_NUMBER


def run_node(node, ip):
    node = NodeOld(node[1], node[2], ip)
    while(True):
        node.receiving()
        rand = randint(1, 1000000)
        if(rand % 10 == 0):  # 1/10 of times request Critical Section
            node.request_CS()


if __name__ == "__main__":
    runFileName = "main.py"
    groups = []
    k = int(math.sqrt(NODES_NUMBER))
    for i in range(k):
        groups.append([])
    i = 0
    j = 0
    end = 0
    while (end < NODES_NUMBER):
        groups[i].append((i, j))
        i = (i + 1) % k
        if(i == 0):
            j += 1
        end += 1
    i = 0
    z = []
    for group in groups:
        for node in group:
            t = threading.Thread(target=run_node, args=(node, MachinesIPs[i],))
            t.start()
            z.append(t)
            # p = run(cmd, shell=True, timeout= 5*60)
            print("Node ({},{}) is created with ip address = {}".format(
                node[0], node[1], MachinesIPs[i]))
            i += 1
    for t in z:
        t.join()


###

# start all threads


# wait for all threads to finish
for t in z:
    t.join()
