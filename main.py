import sys
from NodeOld import *
from random import randint
if __name__ == "__main__":
    if(len(sys.argv) == 4):
        node = NodeOld(sys.argv[1], sys.argv[2], sys.argv[3])
        while(True):
            node.receiving()
            rand = randint(1, 1000000)
            if(rand % 10 == 0):  # 1/10 of times request Critical Section
                node.request_CS()
