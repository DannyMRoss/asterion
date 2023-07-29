
dict = {'a': 10, 'b':12}

for k, v in dict.items():
    print(k)
    print(v)

import pandas as pd
import numpy as np

path = pd.DataFrame({'x' : np.concatenate(([0], np.repeat(np.arange(1, 4), 2))), 'y' : np.concatenate((np.repeat(np.arange(0, 3),2), [3]))})

x = 0 
y = 0
i = 0
for i, row in path[::-1].iterrows():
    while x != row['x']:
        if x < row['x']:
            x += 1
        else:
            x -= 1
    while y != row['y']:
        if y < row['y']:
            y += 1
        else:
            y -= 1
    print(x, y)
path = path[::-1]

