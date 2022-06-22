import socket


s = socket.socket()
host = "" #write your ip address here
port = 9999

s.connect((host, port))

while True:
    data = (s.recv(1024).decode("utf-8"))
    try:
        first, *middle, last = data.split()
    except:
        continue
    if data == "Please enter your name:":
        print(data)
        data=input()
        s.send(str.encode(data))
    elif data == "Please offer your first price:":
        print(data)
        data = input()
        s.send(str.encode(data))
    elif last == "offered":
        print(data)
        data2 = input()
        s.send(str.encode(data2))
    else:
        print(data)

