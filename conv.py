import requests
import random
zero = 0
uno = 0
due = 0
for i in range(20000):
    x = random.randrange(3)
    if (x == 0):
        zero += 1
    if (x == 1):
        uno += 1
    if (x == 2):
        due += 1
print(zero, " ", uno, " ", due)
