import sys
from NodeOld import *

if __name__ == "__main__":
    if(len(sys.argv) == 4):
        node = NodeOld(sys.argv[1], sys.argv[2], sys.argv[3])
        # TODO Run Node
        node.