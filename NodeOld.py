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
        self.self.myIp = ip
        self.requested = False
        self.mutex = False
        self.requestSent = False
        self.tokenQueue = None  # not sure
        if (self.id[1] == 1):
            self.type = NodeType.LRC
            self.totalTokenSent = 0
            if (self.id == (0, 1)):
                self.type = NodeType.GRC
                self.numOfTokens = TOTAL_TOKENS_NUM
            else:
                self.type = NodeType.NORMAL
                self.numOfTokens = 0

    def ConfigPubSubSockets(self):
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

        if(self.type == NodeType.NOMRAL):
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
            Topic = ("Group({}):RequestCS".format(self.id[0])).encode()
            PubSocket.send_multipart([Topic, pickle.dumps(Msg)])
        else:
            NodeType.LRQ.enqueue(self.id)
            if self.numOfTokens > 0:
                self.numOfTokens -= 1
                # TODO enter CS
                ########################
            elif (self.type == NodeType.LRC):
                Msg = {"MsgID": MsgDetails.LRC_GRC_REQ_CS, "GID": self.id[0]}
                Topic = "LRCRequestCS".encode()
                PubSocket.send_multipart([Topic, pickle.dumps(Msg)])
                self.requestSent = True
            # TODO if GRC wants to enter its CS

    def recieve_request(self, nodeId):
        # setTimeOut(SubSocket, 500)
        if (self.type == NodeType.LRC):
            NodeType.LRQ.enqueue(nodeId)
            if (not self.requestSent):
                # msg to GRC from LRC
                Msg = {"MsgID": MsgDetails.LRC_GRC_REQ_CS, "GID": self.id[0]}
                Topic = "LRCRequestCS".encode()
                PubSocket.send_multipart([Topic, pickle.dumps(Msg)])
                self.requestSent = True
                #####################
        elif(self.type == NodeType.GRC):
            if (nodeId[1] == 1):  # SENT FROM LRC
                NodeOld.GRQ.enqueue(self.id)
                NodeType.LRQ.enqueue(MARKER)
                self.send_token()
            else:
                # TODO Send (Request, (nodeId[0], nodeId[1]) to GRC)
                NodeType.LRQ.enqueue(nodeId)
                # NodeOld.GRQ.remove(nodeId)

    def recieve_token(self, fromNode, tokenQueue):
        if (self.NodeType == NodeType.NORMAL):
            if self.requested:
                self.mutex = True
                tokenQueue.dequeue()
                # TODO Enter CS
                self.release_CS()
            else:
                self.send_token()

        # if (self.id[1] == 1):
        if(self.type == NodeType.LRC or self.type == NodeType.GRC):
            self.numOfTokens += 1
            if (fromNode[0] == self.id[0]):  # same local group
                NodeType.LRQ.enqueue(MARKER)
                # NodeOld.GRQ.put(token.Q) #TODO Doesn't understand what for
                # LRQ[0] => is front of queue
                if (self.requested and NodeType.LRQ.front() == self.id):
                    self.mutex = True
                    NodeType.LRQ.dequeue()
                    # TODO Enter CS

                    # END CS
                    self.release_CS()
                else:
                    self.send_token()
            else:
                # TODO uncomment when write this function and remove the print below
                self.send_token()
                print("To be removed")

    def release_CS(self):
        self.requested = False
        self.mutex = False
        self.send_token()

    # node(i, k) broadcast new requests collector (u, w)
    def broadcast_request_collector(self, newGRCId):
        Msg = {"MsgID": MsgDetails.NEW_GRC, "GRCId": newGRCId}
        Topic = "NewGRC".encode()
        PubSocket.send_multipart([Topic, pickle.dumps(Msg)])

    # not sure he said send token from i,k to u,w and never use u and w in the function

    def send_token(self):
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
                       "FromNode": self.id, "TokenQueue": self.tokenQueue}
                Topic = ("Group({}),Id({}):Token".format(
                    nextNode[0], nextNode[1])).encode()
                PubSocket.send_multipart([Topic, pickle.dumps(Msg)])
        else:
            p = len(NodeOld.LRQ)
            q = len(NodeOld.GRQ)
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
                                   "FromNode": self.id, "TokenQueue": tempTokenQueue}
                            Topic = ("Group({}),Id({}):Token".format(
                                firstNode[0], firstNode[1])).encode()
                            PubSocket.send_multipart(
                                [Topic, pickle.dumps(Msg)])
                            self.numOfTokens -= 1

                    if(p > TOTAL_TOKENS_NUM):  # local nodes wants tokens more than num of tokens
                        queueOfTokenQueue = Queue()
                        for _ in range(TOTAL_TOKENS_NUM):
                            queueOfTokenQueue.enqueue(Queue())

                        m = 0
                        while (not NodeOld.LRQ.is_empty()):
                            queueOfTokenQueue[m].enqueue(
                                NodeOld.LRQ.dequeue())
                            m = (m + 1) % TOTAL_TOKENS_NUM

                        # send tokens to GRC's group's local nodes
                        for i in range(TOTAL_TOKENS_NUM):
                            firstNode = queueOfTokenQueue[i].front()
                            Msg = {"MsgID": MsgDetails.TOKEN_QUEUE,
                                   "FromNode": self.id, "TokenQueue": queueOfTokenQueue[i]}
                            Topic = "Group({}),Id({}):Token".format(
                                firstNode[0], firstNode[1]).encode()
                            PubSocket.send_multipart(
                                [Topic, pickle.dumps(Msg)])
                            self.numOfTokens -= 1

                if (p > 0 and q > 0):
                    # num of LRC's wants tokens from GRC more than (num of tokens - 1)
                    if (q > TOTAL_TOKENS_NUM - 1):
                        queueOfTokenQueue = Queue()
                        for _ in range(TOTAL_TOKENS_NUM - 1):
                            queueOfTokenQueue.enqueue(Queue())

                        m = 0
                        while (not NodeOld.GRQ.is_empty()):
                            queueOfTokenQueue[m].enqueue(
                                NodeOld.GRQ.dequeue())
                            m = (m + 1) % (TOTAL_TOKENS_NUM - 1)

                        # send tokens to GRC's group's local nodes
                        for i in range(TOTAL_TOKENS_NUM - 1):
                            firstLRC = queueOfTokenQueue[i].front()
                            Msg = {"MsgID": MsgDetails.TOKEN_QUEUE,
                                   "FromNode": self.id, "TokenQueue": queueOfTokenQueue[i]}
                            Topic = ("Group({}):TokenQueueGlobal".format(
                                firstLRC[0])).encode()
                            PubSocket.send_multipart(
                                [Topic, pickle.dumps(Msg)])
                            self.numOfTokens -= 1
                            self.totalTokenSent += 1

                        if(self.totalTokenSent == math.sqrt(NODES_NUMBER)):
                            broadcast_request_collector(NodeOld.GRQ.rear())

                    if(q < TOTAL_TOKENS_NUM):
                        for _ in range(q):  # send tokens to LRC's from GRC
                            tempTokenQueue = Queue()
                            tempTokenQueue.enqueue(NodeOld.GRQ.dequeue())
                            firstLRC = self.tempTokenQueue.front()
                            Msg = {"MsgID": MsgDetails.TOKEN_QUEUE,
                                   "FromNode": self.id, "TokenQueue": queueOfTokenQueue[i]}
                            Topic = ("Group({}):TokenQueueGlobal".format(
                                firstLRC[0])).encode()
                            PubSocket.send_multipart(
                                [Topic, pickle.dumps(Msg)])
                            self.numOfTokens -= 1
                            self.totalTokenSent += 1

                        if(self.totalTokenSent == math.sqrt(NODES_NUMBER)):
                            broadcast_request_collector(NodeOld.GRQ.rear())

                        # not sure written LRQ = phi in the paper's pesudo code
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
                                   "FromNode": self.id, "TokenQueue": queueOfTokenQueue[i]}
                            Topic = "Group({}),Id({}):Token".format(
                                firstNode[0], firstNode[1]).encode()
                            PubSocket.send_multipart(
                                [Topic, pickle.dumps(Msg)])
                            self.numOfTokens -= 1

            elif(self.type == NodeType.LRC or self.type == NodeType.GRC):
                if (NodeOld.LRQ.front() != MARKER and NodeOld.LRQ.front() != self.id):  # not sure
                    tempTokenQueue = NodeOld.LRQ.copy()
                    tempTokenQueue.enqueue(MARKER)
                    firstNode = tempTokenQueue.front()
                    Msg = {"MsgID": MsgDetails.TOKEN_QUEUE,
                           "FromNode": self.id, "TokenQueue": queueOfTokenQueue[i]}
                    Topic = "Group({}),Id({}):Token".format(
                        firstNode[0], firstNode[1]).encode()
                    PubSocket.send_multipart([Topic, pickle.dumps(Msg)])

                if (NodeOld.LRQ.front() == MARKER):
                    if(self.type == NodeType.GRC and not NodeOld.GRQ.is_empty()):
                        tempTokenQueue = NodeOld.LRQ.copy()
                        firstNode = tempTokenQueue.front()
                        Msg = {"MsgID": MsgDetails.TOKEN_QUEUE,
                               "FromNode": self.id, "TokenQueue": tempTokenQueue}

                        Topic = "Group({}),Id({}):Token".format(
                            firstNode[0], firstNode[1]).encode()
                        PubSocket.send_multipart([Topic, pickle.dumps(Msg)])
                        NodeOld.LRQ.pop()  # pop marker
                    else:
                        Msg = {"MsgID": MsgDetails.LRC_GRC_Token}
                        Topic = "LRC_GRC_Token".encode()
                        PubSocket.send_multipart([Topic, pickle.dumps(Msg)])
