import socket
import time
import threading

v = 1
all_connections = []
all_address = []
client_names = []
client_offers = []
products = []
prices = []
previous_winner = 100 #it should be big number, as much as client number index can't reach
previous_winner2 = 200 #in order to check second round , if the winner is same, so we need 2 variable

#we create our lock at the beginning and receive data related client number,and product number and related data
def main():
    global lock
    global cln
    prn = int(input("How many products will be in Auction?"))
    cln = int(input("How many clients will be in Auction?"))
    global v
    while v <= prn:
        products.append(input("Please enter " + str(v) + ". product name:"))
        prices.append(input("Please enter " + str(v) + ". product price:"))
        v += 1
    v = 1
    lock = threading.Lock()
    create_socket()
    bind_socket()
    welcomers()

#With pycharm IDE, to run server on windows we need to write ip number for host data to create local server
def create_socket():
    try:
        global host
        global port
        global s
        host = "" #write your ip address here
        port = 9999
        s = socket.socket()
    except socket.error as msg:
        print("Socket creation error: " + str(msg))

#Binding the socket
def bind_socket():
    global cln
    try:
        global host
        global port
        global s
        print("Binding the Port: " + str(port))
        s.bind((host, port))
        s.listen(5)
    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()

#We create threads here as many as clients numbers and target is accepting connection
def welcomers():
    global cln
    for _ in range(cln):
        t = threading.Thread(target=accepting_connections)
        t.daemon = True
        t.start()
        t.join()

#We accepts connections for clients in the order and when we have all clients , we start auction
def accepting_connections():
    i=0
    global cln
    while True:
        try:
            conn, address = s.accept()
            s.setblocking(1)  # prevents timeout
            all_connections.append(conn)
            all_address.append(address)
            cl=all_connections[i]
            cl.send(str.encode("Please enter your name:"))
            client_names.append(str(conn.recv(1024).decode("utf-8")))
            print("Connection has been established with: " + client_names[i] + " on port number: " + str(address[1]))
            conn.send(str.encode("Welcome! " + client_names[i]))
            i += 1
            if i == cln:
                start_auction()
        except:
            print("Error accepting connections")

#We receive first offers for the products
def start_auction():
    global p
    global previous_winner, previous_winner2
    for a in range(len(products)):
        p = a
        for x in range(len(all_connections)):
            c = all_connections[x]
            c.send(str.encode("Auction will start 5 seconds later,minimum price for the "
                              + str(products[a]) + " is " + str(prices[p])))
        time.sleep(5)
        for x in range(len(all_connections)):
            c = all_connections[x]
            c.send(str.encode("Please offer your first price:"))
            data = str(c.recv(1024).decode("utf-8"))
            client_offers.append(int(data))
        #for the next product we clear the winner data(setting default)
        previous_winner = 100
        previous_winner2 = 200
        #after receiving first prices we find max(winner)
        find_max()

#we calculate maximum offer here
def find_max():
    max = 0
    global previous_winner, previous_winner2
    for i in range(len(client_offers)):
        if client_offers[i] > max:
            max = client_offers[i]
            index = i
    previous_winner2 = previous_winner
    previous_winner = index
    #after we find the winner, we ask for new offer
    get_new_offer(index)

#we send message to winner but not receiving, when loser acquire the lock , it puts the new offer and release the lock for other loser
def get_new_offer(winner):
    lock.acquire()
    for x in range(len(all_connections)):
        cl = all_connections[x]
        if x == winner:
            cl.send(str.encode("You have offered maximum price, please wait for other people"))
    for x in range(len(all_connections)):
        cl = all_connections[x]
        if x == winner:
            continue
        else:
            cl.send(str.encode(client_names[winner] + " has offered " + str(client_offers[winner]) +
                               " dollars, please offer bigger price for next turn, if you would like to give up, please"+
                               " enter the last price you have offered"))
            data = cl.recv(1024).decode("utf-8")
            client_offers[x] = int(data)
    lock.release()


    result = check_winner(winner)
    #We check if winner is changed or not
    if result == True:
        find_max()

#here if the winner remained same for 2 turn, it return false so the next product auction starts over in the for loop from start(auction)
def check_winner(winner):
    global previous_winner, previous_winner2
    if winner == previous_winner2:
        for x in range(len(all_connections)):
            cl = all_connections[x]
            if x == winner:
                cl.send(str.encode("You have bought the" + products[p] + " for " +
                                  str(client_offers[winner]) + " dollars"))
                print(client_names[x] + " has bought the product " + products[p] +" for " +
                                  str(client_offers[winner]) + " dollars")
            else:
                cl.send(str.encode(client_names[winner] + " has bought " + products[p] +
                       " for " + str(client_offers[winner]) + " dollars"))
        del client_offers[:]
        return False
    else:
        return True






main()