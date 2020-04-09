from subprocess import run, PIPE
import random
import math

if __name__ == "__main__":
    NUM_OF_NODES = 16
    runFileName = "main.py"
    groups = []
    k = int(math.sqrt(NUM_OF_NODES))
    for i in range(k):
        groups.append([])
    i = 0
    j = 0
    end = 0
    while (end < NUM_OF_NODES):
        groups[i].append((i, j))
        i = (i + 1) % k
        if(i == 0):
            j += 1
        end += 1
    for group in groups:
        for node in group:
            cmd = "python {} {} {}".format(runFileName, node[0], node[1])
            p = run(cmd, shell=True, timeout=5*60)
            print("Node ({},{}) is created".format(node[0], node[1]))
