import sys
import numpy as np


half_shape = (5000, 333, 217)
total_shape = (20000, 333, 217)
x = np.ones(half_shape, dtype=np.float32)

print("{} arr is {}G, {}B".format(half_shape, float(sys.getsizeof(x)) / (1024.0 ** 3.), sys.getsizeof(x)))

#  this line fails in an interactive session on ppp2
y = np.ones(total_shape, dtype=np.float32)

print(y.shape)
