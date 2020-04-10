import time
import zmq
import enum
import socket
from contextlib import closing


TOTAL_TOKENS_NUM = 5
MARKER = (-1, -1)
NODES_NUMBER = 16
MachinesIPs = ["192.168.1.13", "192.168.1.14", "192.168.1.15", "192.168.1.16",
               "192.168.1.13", "192.168.1.14", "192.168.1.15", "192.168.1.16",
               "192.168.1.13", "192.168.1.14", "192.168.1.15", "192.168.1.16",
               "192.168.1.13", "192.168.1.14", "192.168.1.15", "192.168.1.16"]
# MachinesIPs = [get_ip()]
SubscribePort = "10000"


class MsgDetails(enum.Enum):
    NODE_LRC_REQ_CS = 1
    LRC_GRC_REQ_CS = 2
    EMPTY_TOKEN_QUEUE = 3
    GRC_LRC_TOKEN = 4
    NEW_GRC = 5
    LRC_GRC_Token = 6


def configure_port(ipPort, portType, connectionType, openTimeOut=False,
                   Time=0, subTopic=False, Topics=[]):
    context = zmq.Context()
    socket = context.socket(portType)
    if(portType == zmq.SUB and subTopic == True):
        for topic in Topics:
            socket.setsockopt_string(zmq.SUBSCRIBE, topic)
    elif(portType == zmq.SUB and subTopic == False):
        socket.setsockopt_string(zmq.SUBSCRIBE, "")
    if(openTimeOut):
        socket.setsockopt(zmq.RCVTIMEO, Time)
        socket.setsockopt(zmq.LINGER,      0)
        socket.setsockopt(zmq.AFFINITY,    1)
    if(connectionType == "connect"):
        socket.connect("tcp://" + ipPort)
    else:
        socket.bind("tcp://" + ipPort)
    return socket, context


def setTimeOut(socket, Time):
    socket.setsockopt(zmq.RCVTIMEO, Time)
    socket.setsockopt(zmq.LINGER,      0)
    socket.setsockopt(zmq.AFFINITY,    1)


def configure_multiple_ports(IPs, port, portType, openTimeOut=False,
                             Time=0, subTopic=False, Topics=[]):
    context = zmq.Context()
    socket = context.socket(portType)
    if(portType == zmq.SUB and subTopic == True):
        for topic in Topics:
            socket.setsockopt_string(zmq.SUBSCRIBE, topic)
    elif(portType == zmq.SUB and subTopic == False):
        socket.setsockopt_string(zmq.SUBSCRIBE, "")
    if(openTimeOut):
        socket.setsockopt(zmq.RCVTIMEO, Time)
        socket.setsockopt(zmq.LINGER,      0)
        socket.setsockopt(zmq.AFFINITY,    1)
    for IP in IPs:
        socket.connect("tcp://" + IP + ":" + port)
        time.sleep(1)
    return socket, context


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def get_ip():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
