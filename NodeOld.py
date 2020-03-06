import utils
import enum


class NodeType(enum.Enum):
    NORMAL = 1
    GRC = 2
    LRC = 3


class NodeOld():
    LRQ = []
    GRQ = []

    def __init__(self, i, j):
        self.id = i, j
        self.requested = False
        self.mutex = False
        self.requestSent = False
        if (self.id == (0, 1)):
            self.type = NodeType.GRC
            self.numOfTokens = utils.TOTAL_TOKENS_NUM
        elif (self.id[1] == 1):
            self.type = NodeType.LRC
            self.numOfTokens = 0
        else:
            self.type = NodeType.NORMAL
            self.numOfTokens = 0

    def request_CS(self):
        self.requested = True
        if (self.id[1] != 1):
            # TODO Request, (i, k)i to (i, 1)
            print("hello")
        else:
            self.LRQ.append(self.id)
            if self.numOfTokens > 0:
                # TODO enter CS
                self.numOfTokens -= 1
            elif (self.type != NodeType.GRC and self.type == NodeType.LRC and not self.requestSent):
                # TODO Send hRequest, (i, j) to GRC
                self.requestSent = True

    def recieve_request(self, nodeId):
        if (self.id[1] == 1 and self.id[0] == nodeId[0] and nodeId[1] != 1):
            self.LRQ.append(nodeId)
            if (self.type == NodeType.LRC and not self.requestSent):
                # TODO Send hRequest, (i, j) to GRC
                self.requestSent = True
            if (self.id[1] == 1 and nodeId[0] != self.id[0] and nodeId[1] == 1):
                if(self.type != NodeType.GRC):
                    # TODO Send (Request, (nodeId[0], nodeId[1]) to GRC)
                    self.GRQ.remove(nodeId)
                else:
                    self.GRQ.append(self.id)
                    # self.send_token(nodeId) #TODO uncomment when write this function

    def recieve_token(self, nodeId):
        if (self.id[1] != 1 and self.id == nodeId):
            if self.requested:
                self.mutex = True
                # TODO TokenQ.delete((i, k))
                # TODO Enter CS
            else:
                # self.send_token(nodeId) #TODO uncomment when write this function and remove the print below
                print("To be removed")
            if (self.id[1] == 1):
                self.numOfTokens += 1
                if (self.id[1] == 1 and nodeId[0] == self.id[0]):
                    self.LRQ.append(utils.MARKER)
                    # self.GRQ.put(token.Q) #TODO Doesn't understand what for
                    # LRQ[0] => is front of queue
                    if (self.requested and self.LRQ[0] == self.id):
                        self.mutex = True
                        self.LRQ.remove(self.id)
                        # TODO Enter CS
                    else:
                        # self.send_token(nodeId) #TODO uncomment when write this function and remove the print below
                        print("To be removed")
                else:
                    # self.send_token(nodeId) #TODO uncomment when write this function and remove the print below
                    print("To be removed")
