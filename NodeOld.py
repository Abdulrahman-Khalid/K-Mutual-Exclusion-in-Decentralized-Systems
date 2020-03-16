import utils
import enum
import Queue
import math


class NodeType(enum.Enum):
    NORMAL = 1
    GRC = 2
    LRC = 3


class NodeOld():
    LRQ = Queue()
    GRQ = Queue()
    TOKEN_Q = Queue()

    def __init__(self, i, j):
        self.id = i, j
        self.requested = False
        self.mutex = False
        self.requestSent = False
        self.token = Queue()  # not sure
        if (self.id[1] == 1):
            self.type = NodeType.LRC
            self.totalTokenSent = 0
            if (self.id == (0, 1)):
                self.type = NodeType.GRC
                self.numOfTokens = utils.TOTAL_TOKENS_NUM
            else:
                self.type = NodeType.NORMAL
                self.numOfTokens = 0

    def request_CS(self):
        self.requested = True
        if (self.id[1] != 1):
            # TODO Request, (i, k)i to (i, 1)
            print("hello")
        else:
            NodeType.LRQ.push(self.id)
            if self.numOfTokens > 0:
                # TODO enter CS
                self.numOfTokens -= 1
            elif (self.type != NodeType.GRC and self.type == NodeType.LRC and not self.requestSent):
                # TODO Send hRequest, (i, j) to GRC
                self.requestSent = True

    def recieve_request(self, nodeId):
        if (self.type == NodeType.LRC and self.id[0] == nodeId[0] and nodeId[1] != 1):
            NodeType.LRQ.push(nodeId)
            if (self.type == NodeType.LRC and not self.requestSent):
                # TODO Send hRequest, (i, j) to GRC
                self.requestSent = True
            if (self.type == NodeType.LRC and nodeId[0] != self.id[0] and nodeId[1] == 1):
                if(self.type != NodeType.GRC):
                    # TODO Send (Request, (nodeId[0], nodeId[1]) to GRC)
                    NodeOld.GRQ.remove(nodeId)
                else:
                    NodeOld.GRQ.push(self.id)
                    # TODO uncomment when write this function
                    self.send_token(nodeId)

    def recieve_token(self, nodeId):
        if (self.id[1] != 1 and self.id == nodeId):
            if self.requested:
                self.mutex = True
                # TODO TokenQ.delete((i, k))
                # TODO Enter CS
            else:
                # self.send_token(nodeId) #TODO uncomment when write this function and remove the print below
                print("To be removed")
            if(self.type == NodeType.LRC):  # if (self.id[1] == 1):
                self.numOfTokens += 1
                if (nodeId[0] == self.id[0]):  # same local group
                    NodeType.LRQ.push(utils.MARKER)
                    # NodeOld.GRQ.put(token.Q) #TODO Doesn't understand what for
                    # LRQ[0] => is front of queue
                    if (self.requested and NodeType.LRQ.front() == self.id):
                        self.mutex = True
                        NodeType.LRQ.pop()
                        # TODO Enter CS
                    else:
                        # TODO uncomment when write this function and remove the print below
                        self.send_token(nodeId)
                        print("To be removed")
                else:
                    # TODO uncomment when write this function and remove the print below
                    self.send_token(nodeId)
                    print("To be removed")

    def release_CS(self, nodeId):
        self.requested = False
        self.mutex = False
        self.send_token(nodeId)

    # not sure he said send token from i,k to u,w and never use u and w in the function
    def send_token(self, nodeId):
        if(self.type != NodeType.LRC):
            if(self.token.is_empty()):
                idOfLRC = self.id[0], 1
                # TODO Send htoken i to (i, 1)
            else:
                # TODO Send token to tokenQ.front
                print("To be removed")
        else:
            p = len(NodeOld.LRQ)
            q = len(NodeOld.LRQ)
            k = self.id[1]
            # self.numOfTokens == self.id[1]!!!? not sure
            if(self.type == NodeType.GRC and self.numOfTokens == k):
                if(p > 0 and q == 0):
                    if(q <= k):
                        # create p tokens
                        for _ in range(p):  # not sure: most likley wrong
                            NodeOld.TOKEN_Q.push(Queue())
                        for i in range(p):
                            NodeOld.TOKEN_Q[i].push(NodeOld.LRQ.pop())
                            # TODO Send token to tokenQ.front
                            self.numOfTokens -= 1
        if(p > k):
            for _ in range(k):  # not sure: most likley wrong
                NodeOld.TOKEN_Q.push(Queue())
            m = 0
            i = 1
            while (not NodeOld.LRQ.is_empty()):
                NodeOld.TOKEN_Q[i].push(NodeOld.LRQ.pop())
                m = (m+1) % k  # not sure: what is the purpose of this line !!!?
            for i in range(k):
                # TODO send Token[i] to Token[i].front
                self.numOfTokens -= 1
        if (p > 0 and q > 0):
            if (q > k - 1):
                m = 0
                i = 1
                while (not NodeOld.GRQ.is_empty()):
                    NodeOld.TOKEN_Q[i].push(NodeOld.GRQ.pop())
                    # not sure: what is the purpose of this line !!!?
                    m = (m+1) % (k-1)
                for i in range(k-1):  # not sure range(k-1)
                    # TODO send Token[i] to Token[i].front
                    self.numOfTokens -= 1
                    self.totalTokenSent += 1
                    if(self.totalTokenSent == math.sqrt(utils.NODES_NUMBER)):
                        NodeOld.GRQ = NodeOld.TOKEN_Q[i].rear()
                        broadcast_request_collector(NodeOld.GRQ)
                if(q < k):
                    for _ in range(q):  # not sure: most likley wrong
                        NodeOld.TOKEN_Q.push(Queue())
                    for i in range(q):
                        NodeOld.TOKEN_Q[i].push(NodeOld.GRQ.pop())
                        self.numOfTokens -= 1
                        self.totalTokenSent += 1
                        if(self.totalTokenSent == math.sqrt(utils.NODES_NUMBER)):
                            NodeOld.GRQ = NodeOld.TOKEN_Q[i].rear()
                            broadcast_request_collector(NodeOld.GRQ)
                        # TODO Send token to tokenQ.front
                    # send token to local nodes
                    m = 0
                    i = 0
                    # not sure written LRQ = phi in the paper's pesudo code
                    while (not NodeOld.LRQ.is_empty()):
                        NodeOld.TOKEN_Q[i].push(NodeOld.LRQ.pop())
                        # not sure: what is the prpose of this line !!!?
                        m = (m+1) % (k-q)
                    for i in range(k-q):  # not sure range(k-1)
                        # TODO send Token[i] to Token[i].front
                        self.numOfTokens -= 1
                if(self.type == NodeType.LRC):  # not sure if ((i, k) = LRC & id != GRC)
                    if (NodeOld.LRQ.front() != utils.MARKER and NodeOld.LRQ.front() != self.id):  # not sure
                        # TODO Copy(LRQ, tokenQ, Marker)
                        # TODO Send token to tokenQ.front
                        print("To be removed")
                    if (NodeOld.LRQ.front() == utils.MARKER):
                        if(not NodeOld.GRQ.is_empty()):
                            # TODO Copy(LRQ, tokenQ, Ø)
                            # TODO Send token to tokenQ.front
                            NodeOld.LRQ.remove(utils.MARKER)
                        else:
                            # TODO Send token to GRC
                            print("to be removed")

    # node(i, k) broadcast new requests collector (u, w)
    def broadcast_request_collector(self, nodeId):
        for _ in range(math.sqrt(utils.NODES_NUMBER)):
            # TODO send hGRC, (u, w)i to (y, 1)
            print("to be removed")
