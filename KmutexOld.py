import queue


class KmutexOld():
    def __init__(self, totalNumOfTokens):
        self.totalNumOfTokens = totalNumOfTokens

    def request_CS(self, node):
        node.requested = True
