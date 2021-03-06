from utils import *
from Queue import *
import enum
import math
import zmq
import pickle

# import sys

PubSocket = None
PubContext = None
SubSocket = None
SubContext = None


class NodeType(enum.Enum):
    NORMAL = 1
    GRC = 2
    LRC = 3


class NodeOld():
    LRQ = Queue()
    GRQ = Queue()
    # TOKEN_Q = Queue()

    def __init__(self, i, j, ip):
        self.id = i, j
        self.myIp = ip
        self.requested = False
        self.mutex = False
        self.requestSent = False
        self.tokenQueue = None 
        self.tokens = []
        self.type = None
        if (self.id[1] == 1):
            self.type = NodeType.LRC
            self.totalTokenSent = 0
            if (self.id == (0, 1)):
                self.type = NodeType.GRC
                self.numOfTokens = TOTAL_TOKENS_NUM
        else:
            self.type = NodeType.NORMAL
            self.numOfTokens = 0
        self.ConfigPubSubSockets()

    def ConfigPubSubSockets(self):
        global SubSocket, SubContext, PubSocket, PubContext
        # Setup Subscriber Port
        ipPort = self.myIp + ":" + SubscribePort
        Topics = self.MsgsTopics()
        SubSocket, SubContext = configure_port(ipPort, zmq.SUB, 'bind',
                                               True, -1, True, Topics)
        # Connect to all other Subscribers
        MachinesIPsTemp = MachinesIPs.copy()
        MachinesIPsTemp.remove(self.myIp)
        PubSocket, PubContext = configure_multiple_ports(
            MachinesIPsTemp, SubscribePort, zmq.PUB)

    def MsgsTopics(self):
        Topics = []

        if (self.type == NodeType.LRC):
            Topics.append("Group({}):RequestCS".format(self.id[0]))
            Topics.append("Group({}):EmptyTokenQueueLocal".format(self.id[0]))
            Topics.append("Group({}):TokenQueueGlobal".format(self.id[0]))
            Topics.append("NewGRC")

        if (self.type == NodeType.GRC):
            Topics.append("Group({}):RequestCS".format(self.id[0]))
            Topics.append("Group({}):EmptyTokenQueueLocal".format(self.id[0]))
            Topics.append("LRCRequestCS")
            Topics.append("LRC_GRC_Token")

        if(self.type == NodeType.NORMAL):
            Topics.append("Group({}),Id({}):Token".format(
                self.id[0], self.id[1]))

        # The Kind of Messages that I want only to receive
        Topics.append("Broadcast")

        return Topics

    def request_CS(self):
        self.requested = True
        if (self.type == NodeType.NORMAL):
            Msg = {"MsgID": MsgDetails.NODE_LRC_REQ_CS,
                   "ID": self.id[1]}
            Topic = ("Group({}):RequestCS"
                     .format(self.id[0])).encode()
            PubSocket.send_multipart([Topic, pickle.dumps(Msg)])
        else:
            NodeOld.LRQ.enqueue(self.id)
            if self.numOfTokens > 0:
                self.numOfTokens -= 1
                # TODO enter CS
                self.run_CS()
                self.release_CS()
                ########################
                self.numOfTokens += 1
            elif (self.type == NodeType.LRC):
                Msg = {"MsgID": MsgDetails.LRC_GRC_REQ_CS, "GID": self.id[0]}
                Topic = "LRCRequestCS".encode()
                PubSocket.send_multipart([Topic, pickle.dumps(Msg)])
                self.requestSent = True

    def recieve_request(self, fromNode):
        if (self.type == NodeType.LRC):
            NodeOld.LRQ.enqueue(fromNode)
            if (not self.requestSent):
                # msg to GRC from LRC
                Msg = {"MsgID": MsgDetails.LRC_GRC_REQ_CS, "GID": self.id[0]}
                Topic = "LRCRequestCS".encode()
                PubSocket.send_multipart([Topic, pickle.dumps(Msg)])
                self.requestSent = True
                #####################
        elif(self.type == NodeType.GRC):
            if (fromNode[1] == 1):  # SENT FROM LRC
                NodeOld.GRQ.enqueue(self.id)
                # NodeType.LRQ.enqueue(MARKER)
            else:
                # TODO Send (Request, (fromNode[0], fromNode[1]) to GRC)
                NodeOld.LRQ.enqueue(fromNode)
                # NodeOld.GRQ.remove(fromNode)
            self.send_token()

    def receiving(self):
        setTimeOut(SubSocket, 5000)
        Topic, receivedMessage = SubSocket.recv_multipart()
        receivedMessage = pickle.loads(receivedMessage)
        if(self.type == NodeType.NORMAL):
            if(Topic == "Group({}),Id({}):Token".format(self.id[0], self.id[1])):
                self.recieve_token(True, receivedMessage["TokenQueue"])

        elif(self.type == NodeType.LRC):
            if(Topic == "Group({}):RequestCS".format(self.id[0])):
                self.recieve_request((self.id[0], receivedMessage["ID"]))
            elif(Topic == "Group({}):EmptyTokenQueueLocal".format(self.id[0])):
                self.recieve_token(True, Queue())
            elif(Topic == "Group({}):TokenQueueGlobal".format(self.id[0])):
                self.recieve_token(False, receivedMessage["TokenQueue"])
            elif(Topic == "NewGRC"):
                if(self.id == receivedMessage["GRCId"]):
                    self.type = NodeType.GRC
                    NodeOld.GRQ = receivedMessage["GRQ"]

        elif(self.type == NodeType.GRC):
            if(Topic == "Group({}):RequestCS".format(self.id[0])):
                self.recieve_request((self.id[0], receivedMessage["ID"]))
            elif(Topic == "Group({}):EmptyTokenQueueLocal".format(self.id[0])):
                self.recieve_token(True, Queue())
            elif(Topic == "LRCRequestCS"):
                self.recieve_request((receivedMessage["GID"], 1))
            elif(Topic == "LRC_GRC_Token"):
                self.recieve_token(False, receivedMessage["TokenQueue"])

    def recieve_token(self, sameLocalGroup, tokenQueue):
        # TODO Added Need TO BE REVIEWED
        self.tokenQueue = tokenQueue.copy()
        ################################
        if (self.type == NodeType.NORMAL):
            if self.requested:
                self.mutex = True
                self.tokenQueue.dequeue()
                # TODO Enter CS
                self.run_CS()
                self.release_CS()
            else:
                self.send_token()
        # if (self.id[1] == 1):
        if(self.type == NodeType.LRC):
            self.numOfTokens += 1
            if (not sameLocalGroup):  # same local group
                # NodeOld.GRQ.put(token.Q) #TODO Doesn't understand what for
                # LRQ[0] => is front of queue
                self.requestSent = False
                if (self.requested and NodeOld.LRQ.front() == self.id):
                    self.mutex = True
                    NodeOld.LRQ.dequeue()
                    # TODO Enter CS
                    self.run_CS()
                    self.release_CS()
                    # END CStokenQueuetokenQueue
                else:
                    self.send_token()
            else:
                # TODO uncomment when write this function and remove the print below
                self.send_token()
                # print("To be removed")
        else:
            self.numOfTokens += 1
            self.totalTokenSent -= 1
            self.send_token(tokenQueue)

    def release_CS(self):
        self.requested = False
        self.mutex = False
        self.send_token()

    def run_CS(self):
        time.sleep(100)
    # node(i, k) broadcast new requests collector (u, w)

    def broadcast_request_collector(self, newGRCId):
        Msg = {"MsgID": MsgDetails.NEW_GRC,
               "GRCId": newGRCId, "GRQ": NodeOld.GRQ}
        Topic = "NewGRC".encode()
        PubSocket.send_multipart([Topic, pickle.dumps(Msg)])
       
        if(self.type == NodeType.GRC):
            self.type = NodeType.LRC
            NodeOld.GRQ = Queue()

    # not sure he said send token from i,k to u,w and never use u and w in the function

    def send_token(self, token=None):
        if(token != None and (not token.is_empty())):
            firstLRC = token.front()
            Msg = {"MsgID": MsgDetails.TOKEN_QUEUE,
                   "TokenQueue": token}
            Topic = ("Group({}):TokenQueueGlobal".format(
                firstLRC[0])).encode()
            PubSocket.send_multipart(
                [Topic, pickle.dumps(Msg)])
            self.numOfTokens -= 1
            self.totalTokenSent += 1

        if(self.type == NodeType.NORMAL and self.tokenQueue != None):  # token from local node to LRC
            if(self.tokenQueue.is_empty()):
                # idOfLRC = self.id[0], 1
                Msg = {"MsgID": MsgDetails.EMPTY_TOKEN_QUEUE}
                Topic = ("Group({}):EmptyTokenQueueLocal".format(
                    self.id[0]).encode())
                PubSocket.send_multipart([Topic, pickle.dumps(Msg)])
            else:  # token from local node to another local node
                nextNode = self.tokenQueue.front()
                Msg = {"MsgID": MsgDetails.TOKEN_QUEUE,
                       "TokenQueue": self.tokenQueue}
                Topic = ("Group({}),Id({}):Token".format(
                    nextNode[0], nextNode[1])).encode()
                PubSocket.send_multipart([Topic, pickle.dumps(Msg)])
            self.tokenQueue = None  
        else:
            p = NodeOld.LRQ.size()
            q = NodeOld.GRQ.size()
            if(self.type == NodeType.GRC and self.numOfTokens == TOTAL_TOKENS_NUM):
                if(p > 0 and q == 0):  # local nodes wants tokens and another groups doesn't
                    # localsend_to nodes wants tokens less than or equals num of tokens
                    if(p <= TOTAL_TOKENS_NUM):
                        # create p tokens
                        for _ in range(p):  # send tokens to GRC's group's local nodes
                            tempTokenQueue = Queue()
                            tempTokenQueue.enqueue(NodeOld.LRQ.dequeue())
                            firstNode = self.tokenQueue.front()
                            Msg = {"MsgID": MsgDetails.TOKEN_QUEUE,
                                   "TokenQueue": tempTokenQueue}
                            Topic = ("Group({}),Id({}):Token".format(
                                firstNode[0], firstNode[1])).encode()
                            PubSocket.send_multipart(
                                [Topic, pickle.dumps(Msg)])
                            self.numOfTokens -= 1

                    if(p > TOTAL_TOKENS_NUM):  # local nodes wants tokens more than num of tokens
                        queueOfTokenQueue = []
                        for _ in range(TOTAL_TOKENS_NUM):
                            queueOfTokenQueue.append(Queue())

                        m = 0
                        while (not NodeOld.LRQ.is_empty()):
                            queueOfTokenQueue[m].enqueue(
                                NodeOld.LRQ.dequeue())
                            m = (m + 1) % TOTAL_TOKENS_NUM

                        # send tokens to GRC's group's local nodes
                        for i in range(TOTAL_TOKENS_NUM):
                            firstNode = queueOfTokenQueue[i].front()
                            Msg = {"MsgID": MsgDetails.TOKEN_QUEUE,
                                   "TokenQueue": queueOfTokenQueue[i]}
                            Topic = "Group({}),Id({}):Token".format(
                                firstNode[0], firstNode[1]).encode()
                            PubSocket.send_multipart(
                                [Topic, pickle.dumps(Msg)])
                            self.numOfTokens -= 1

                if (p >= 0 and q > 0):
                    # num of LRC's wants tokens from GRC more than (num of tokens - 1)
                    if (q >= TOTAL_TOKENS_NUM - 1):
                        queueOfTokenQueue = []
                        for _ in range(TOTAL_TOKENS_NUM - 1):
                            queueOfTokenQueue.append(Queue())

                        m = 0
                        while (not NodeOld.GRQ.is_empty()):
                            queueOfTokenQueue[m].enqueue(
                                NodeOld.GRQ.dequeue())
                            m = (m + 1) % (TOTAL_TOKENS_NUM - 1)

                        # send tokens to GRC's group's local nodes
                        for i in range(TOTAL_TOKENS_NUM - 1):
                            firstLRC = queueOfTokenQueue[i].front()
                            Msg = {"MsgID": MsgDetails.TOKEN_QUEUE,
                                   "TokenQueue": queueOfTokenQueue[i]}
                            Topic = ("Group({}):TokenQueueGlobal".format(
                                firstLRC[0])).encode()
                            PubSocket.send_multipart(
                                [Topic, pickle.dumps(Msg)])
                            self.numOfTokens -= 1
                            self.totalTokenSent += 1

                        if(self.totalTokenSent == math.sqrt(NODES_NUMBER)):
                            self.broadcast_request_collector(
                                NodeOld.GRQ.rear())

                    if(q < TOTAL_TOKENS_NUM):
                        for _ in range(q):  # send tokens to LRC's from GRC
                            tempTokenQueue = Queue()
                            tempTokenQueue.enqueue(NodeOld.GRQ.dequeue())
                            firstLRC = tempTokenQueue.front()
                            Msg = {"MsgID": MsgDetails.TOKEN_QUEUE,
                                   "TokenQueue": queueOfTokenQueue[i]}
                            Topic = ("Group({}):TokenQueueGlobal".format(
                                firstLRC[0])).encode()
                            PubSocket.send_multipart(
                                [Topic, pickle.dumps(Msg)])
                            self.numOfTokens -= 1
                            self.totalTokenSent += 1

                        if(self.totalTokenSent == math.sqrt(NODES_NUMBER)):
                            self.broadcast_request_collector(
                                NodeOld.GRQ.rear())

                        remainingNumTokens = TOTAL_TOKENS_NUM - q
                        queueOfTokenQueue = Queue()
                        for _ in range(remainingNumTokens):
                            queueOfTokenQueue.enqueue(Queue())

                        m = 0
                        while (not NodeOld.LRQ.is_empty()):
                            queueOfTokenQueue[m].enqueue(
                                NodeOld.LRQ.dequeue())
                            m = (m + 1) % remainingNumTokens

                        for i in range(remainingNumTokens):
                            firstNode = queueOfTokenQueue[i].front()
                            Msg = {"MsgID": MsgDetails.TOKEN_QUEUE,
                                   "TokenQueue": queueOfTokenQueue[i]}
                            Topic = "Group({}),Id({}):Token".format(
                                firstNode[0], firstNode[1]).encode()
                            PubSocket.send_multipart(
                                [Topic, pickle.dumps(Msg)])
                            self.numOfTokens -= 1

            elif(self.type == NodeType.LRC or self.type == NodeType.GRC):
                if (NodeOld.LRQ.front() != MARKER and NodeOld.LRQ.front() != self.id):  
                    tempTokenQueue = NodeOld.LRQ.copy()
                    # tempTokenQueue.enqueue(MARKER)
                    firstNode = tempTokenQueue.front()
                    Msg = {"MsgID": MsgDetails.TOKEN_QUEUE,
                           "TokenQueue": queueOfTokenQueue[i]}
                    Topic = "Group({}),Id({}):Token".format(
                        firstNode[0], firstNode[1]).encode()
                    PubSocket.send_multipart([Topic, pickle.dumps(Msg)])

                if (NodeOld.LRQ.front() == MARKER):
                    if(self.type == NodeType.GRC and not NodeOld.GRQ.is_empty()):
                        NodeOld.LRQ.dequeue()  # pop marker
                        self.tokenQueue = NodeOld.LRQ.copy()
                        NodeOld.LRQ.enqueue(MARKER)
                        firstNode = tempTokenQueue.front()
                        Msg = {"MsgID": MsgDetails.TOKEN_QUEUE,
                               "TokenQueue": tempTokenQueue}
                        Topic = "Group({}),Id({}):Token".format(
                            firstNode[0], firstNode[1]).encode()
                        PubSocket.send_multipart([Topic, pickle.dumps(Msg)])
# --------------------------------------------------------------------------------------------
                    else:
                        self.tokenQueue.dequeue()
                        Msg = {"MsgID": MsgDetails.LRC_GRC_Token,
                               "TokenQueue": self.tokenQueue}
                        self.tokenQueue = None
                        Topic = "LRC_GRC_Token".encode()
                        PubSocket.send_multipart([Topic, pickle.dumps(Msg)])

## Queue (LRC1, LRC2, LRC3)
# LRC1 -> serve all in LRQ
# LRC1 -> Queue (LRC2, LRC3)
# Queue (LRC2, LRC3) -> to GRC
