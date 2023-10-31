f = open("information.txt", "r")
test = f.readline()
f.close()

print(test)

f = open("information.txt", "a")
f.write("\nsomethingsomthing")
f.close()

f = open("information.txt", "r")

test = f.read()

print(test)

#testing again