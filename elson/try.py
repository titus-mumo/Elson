import os

current = os.getcwd()

nn = os.path.join(os.getcwd(), "audio")
n = os.path.normpath(nn)
print(n)