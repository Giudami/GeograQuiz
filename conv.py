from functools import reduce

l = [(2291715, 2), (324709314, 1), (426899305, 0)]

text = ""
for x in l:
    text += str(x[0]) + ': ' + str(x[1]) + '\n'

print(text)
