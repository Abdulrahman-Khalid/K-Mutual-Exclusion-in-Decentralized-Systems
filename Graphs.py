# Import our modules that we are using
import matplotlib.pyplot as plt
import numpy as np
import math

M = 1
q = 1
k = 1
n = 1
n_largest = 1
E = 1
G = []

TimeOldCaseA = M *(2 + q + n) + n * E
MsgsOldCaseA = q * (4 + n * (1 + (math.sqrt(q)/k)))

TimeNewCaseA = M * (2 + q) + (n * (math.sqrt(q)/k)) * (M + E)
MsgsNewCaseA = q * (3 + n * (1 + (math.sqrt(q)/k)))

TimeOldCaseB = M *(2 + q + n_largest) + n_largest * E

Temp = 0
for i in range (0, q):
    Temp += (n[i] + n[i] * (math.sqrt(q)/k))

MsgsOldCaseB = 4 * q + Temp

Temp2 = 0
for i in range (1, q):
    Temp2 += ((G[i + 1] - G[i] - 2 * M) / 2) + M

TimeNewCaseB = M * (2 + q) + G[0] + Temp2

Temp2 = 0
for i in range (1, q):
    Temp3 +=  3 * n[i] * (math.sqrt(q)/4)

MsgsNewCaseB = q * (3 + n) + n[0] * (math.sqrt(q)/k) + Temp3

# Create the vectors X and Y
x = np.array(range(100))
y = x ** 2

# Create the plot
plt.plot(x,y)

# Show the plot
plt.show()