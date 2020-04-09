import sys
from NodeOld import *

if __name__ == "__main__":
    if(len(sys.argv) == 4):
        node = NodeOld(sys.argv[1], sys.argv[2], sys.argv[3])
        # TODO Run Node
        while(True):
            # thread connections
            node.send_token()
            node.recieve_token((0, 0), Queue())  # TODO TO BE CHANGED
            node.recieve_request((0, 0))  # TODO TO BE CHANGED
            # end of thread connections
            node.request_CS()
