import random
population = 4_567_893
options = []
for i in range(3):
    x = random.randrange(4)
    if (x == 0):
        x = 5
    elif (x == 1):
        x = 1 / 5
    elif (x == 2):
        x = 8
    elif (x == 3):
        x = 1 / 8
    pop = round((population + population * (random.random() - 0.5)) * x)
    options.append('{:,}'.format(pop).replace(',', '.'))
print(options)
