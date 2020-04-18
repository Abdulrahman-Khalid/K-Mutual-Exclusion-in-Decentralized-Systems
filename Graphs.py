# Import our modules that we are using
import matplotlib.pyplot as plt
import numpy as np
import math

M = 10
E = 50
# 32 * 32
q = None
k = None
n = None
n_arr = None
n_largest = None


def time_old_1():
    time = M * (4 + n) + n * E
    return time


def msg_old_1():
    NumOfMsgs = 2 * q * (2 + n)
    return NumOfMsgs


def time_old_2():
    time = M * (4 + n_largest) + n_largest * E
    return time


def msg_old_2():
    NumOfMsgs = (4 * q) + (2 * sum(n_arr))
    return NumOfMsgs


def time_new_1():
    time = (4 * M) + (n * ((q+1)/k)*(M + E))
    return time


def msg_new_1():
    NumOfMsgs = 4*q+sum(n_arr) + n_arr[0]*(q+1)/k + (3/4)*(q+1)*sum(n_arr[1:])
    return NumOfMsgs


def Gf_calc(i):
    if(i < 0):
        return 0
    Gf = (((n_arr[i]*(q+1)*(M+E))/(2*k))+2*M) - Gf_calc(i-1)
    return Gf


def time_new_2():
    n_arr.sort()
    Gf = Gf_calc(len(n_arr)-1)
    time = (4 * M) + Gf
    return time


def msg_new_2():
    NumOfMsgs = q * (4 + n * (2 + ((q+1)/k)))
    return NumOfMsgs


graphIndx = 1


def draw(x, arr_y, labels, title):
    global graphIndx
    caseTitles = ["Case 1", "Case 1", "Case 2", "Case 2"]
    titles = ["Old algorithm", "New algorithm", "Old algorithm", "New algorithm",
              "Old algorithm", "New algorithm", "Old algorithm", "New algorithm"]
    idx = 0
    plt.rcParams.update({'font.size': 22})
    while(idx < len(arr_y) - 1):
        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.set_size_inches(20.5, 10.5)
        fig.suptitle(caseTitles[int(idx/2)]+" " + title, color="#35375A")
        ax1.set_title(titles[idx], color='#FF4500')
        ax2.set_title(titles[idx+1], color='#1F2179')
        ax1.set(xlabel=labels[idx][0], ylabel=labels[idx][1])
        ax2.set(xlabel=labels[idx+1][0], ylabel=labels[idx+1][1])
        ax1.grid()
        ax2.grid()
        ax1.plot(x, arr_y[idx], color='#FF4500')
        ax2.plot(x, arr_y[idx+1], color='#1F2179')
        idx += 2
        plt.savefig('Graphs/{}.png'.format(graphIndx), dpi=50,
                    interpolation='nearest', aspect='auto')
        graphIndx += 1
        # plt.show()


def draw_k_as_variable():
    global k, q, n, n_arr, n_largest
    n = 128
    n_arr = [1, 2, 4, 8, 16, 32, 64, 128]
    q = 8
    n_largest = max(n_arr)
    inputs_k = range(q, 100, 5)
    timeOld1 = []
    timeNew1 = []
    msgOld1 = []
    msgNew1 = []
    timeOld2 = []
    timeNew2 = []
    msgOld2 = []
    msgNew2 = []
    for x in inputs_k:
        k = x
        timeOld1.append(time_old_1())
        timeNew1.append(time_new_1())
        msgOld1.append(msg_old_1())
        msgNew1.append(msg_new_1())
        timeOld2.append(time_old_2())
        timeNew2.append(time_new_2())
        msgOld2.append(msg_old_2())
        msgNew2.append(msg_new_2())
    arr_y = [timeOld1, timeNew1, msgOld1, msgNew1,
             timeOld2, timeNew2, msgOld2, msgNew2]
    labels = [("Number of tokens (k)", "Time in ms"), ("Number of tokens (k)", "Time in ms"), ("Number of tokens (k)", "Num of Messages"),
              ("Number of tokens (k)", "Num of Messages"), ("Number of tokens (k)",
                                                            "Time in ms"), ("Number of tokens (k)", "Time in ms"),
              ("Number of tokens (k)", "Num of Messages"), ("Number of tokens (k)", "Num of Messages")]
    draw(inputs_k, arr_y, labels, "when q = 8 and largest n = 128")


def draw_q_as_variable():  # k > q
    global k, q, n, n_arr, n_largest
    k = 50
    n = 128
    n_arr = [1, 2, 4, 8, 16, 32, 64, 128]
    n_largest = max(n_arr)
    inputs_q = range(1, len(n_arr)+1)
    timeOld1 = []
    timeNew1 = []
    msgOld1 = []
    msgNew1 = []
    timeOld2 = []
    timeNew2 = []
    msgOld2 = []
    msgNew2 = []
    for x in inputs_q:
        q = x
        timeOld1.append(time_old_1())
        timeNew1.append(time_new_1())
        msgOld1.append(msg_old_1())
        msgNew1.append(msg_new_1())
        timeOld2.append(time_old_2())
        timeNew2.append(time_new_2())
        msgOld2.append(msg_old_2())
        msgNew2.append(msg_new_2())
    arr_y = [timeOld1, timeNew1, msgOld1, msgNew1,
             timeOld2, timeNew2, msgOld2, msgNew2]
    labels = [("Number of requested groups (q)", "Time in ms"), ("Number of requested groups (q)", "Time in ms"), ("Number of requested groups (q)", "Num of Messages"),
              ("Number of requested groups (q)", "Num of Messages"), ("Number of requested groups (q)",
                                                                      "Time in ms"), ("Number of requested groups (q)", "Time in ms"),
              ("Number of requested groups (q)", "Num of Messages"), ("Number of requested groups (q)", "Num of Messages")]
    draw(inputs_q, arr_y, labels, "when k = 50 and largest n = 128")


def draw_n_as_variable():  # k > q
    global k, q, n, n_arr, n_largest
    k = 50
    q = 5
    inputs_n = range(1, k+1)
    timeOld1 = []
    timeNew1 = []
    msgOld1 = []
    msgNew1 = []
    timeOld2 = []
    timeNew2 = []
    msgOld2 = []
    msgNew2 = []
    for x in inputs_n:
        n = x
        i = 2
        n_arr = [1]
        while(i < n):
            n_arr.append(i)
            i *= 2
        n_largest = max(n_arr)
        timeOld1.append(time_old_1())
        timeNew1.append(time_new_1())
        msgOld1.append(msg_old_1())
        msgNew1.append(msg_new_1())
        timeOld2.append(time_old_2())
        timeNew2.append(time_new_2())
        msgOld2.append(msg_old_2())
        msgNew2.append(msg_new_2())
    arr_y = [timeOld1, timeNew1, msgOld1, msgNew1,
             timeOld2, timeNew2, msgOld2, msgNew2]
    labels = [("Number of requested nodes (n)", "Time in ms"), ("Number of requested nodes (n)", "Time in ms"), ("Number of requested nodes (n)", "Num of Messages"),
              ("Number of requested nodes (n)", "Num of Messages"), ("Number of requested nodes (n)",
                                                                     "Time in ms"), ("Number of requested nodes (n)", "Time in ms"),
              ("Number of requested nodes (n)", "Num of Messages"), ("Number of requested nodes (n)", "Num of Messages")]
    draw(inputs_n, arr_y, labels, "when k = 50 and q = 5")


if __name__ == "__main__":
    draw_k_as_variable()
    draw_q_as_variable()
    draw_n_as_variable()
