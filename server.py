import socket 
import threading
import pickle
import time

HEADER = 64
PORT = 8080
SERVER = "0.0.0.0"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "disconnect"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDR)


connections = []
usernames = {}
conn_usernames = {}
online_users = []

admins = []
banned = []

def addr_from_username(user):
    for key, value in usernames.items():
        if value == user:
            return key[0]


with open("resources/server/banned.txt", 'r') as file:
    for line in file:
        line = line.strip()
        banned.append(line)

with open("resources/server/admins.txt", 'r') as file:
    for line in file:
        line = line.strip()
        admins.append(line)

def write_config():
    with open("resources/server/banned.txt", 'w') as file:
        file.truncate(0)
        print(banned)
        for member in banned:
            file.write(member + "\n")

def send_to_all(msg, user):
    msg = ('m', msg, user)
    for conn in connections:
        conn.send(pickle.dumps(msg))

def send_object_to_all(object):
    for conn in connections:
        conn.send(pickle.dumps(object))

def send(user, msg):
    conn = conn_usernames[user] # Get connection object from conn_usernames
    conn.send(pickle.dumps(msg))


def handle_client(conn, addr):
    usernames[addr] = str(threading.activeCount() - 1) #Temp username
    conn_usernames[usernames[addr]] = conn

    if addr[0] in banned:
        conn.send(pickle.dumps(('x')))
        return 0
    else:
        print(f"[NEW CONNECTION] {addr} connected.")
    
    connected = True
    username_set = False
    join_message_sent = False

    conn.send(pickle.dumps(('o', online_users)))

    while connected:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
        except:
            connected = False #Disconnect if failed to recive header

        if username_set == True and join_message_sent == False:
            send_object_to_all(('j', usernames[addr]))
            online_users.append(usernames[addr])
            join_message_sent = True

        
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length)
            msg = pickle.loads(msg)

            prefix = msg[0]
            if prefix == 'm':
                is_command = False
            else:
                is_command = True

            if msg[1] == DISCONNECT_MESSAGE:
                connected = False
            if prefix == 'u':
                if msg[1] in usernames.values():
                    send(usernames[addr], ('r', "That username is taken. please choose another."))
                    print("username taken")
                else:
                    usernames[addr] = msg[1]
                    print(usernames)
                    conn_usernames[msg[1]] = conn
                    send(usernames[addr], ('r', "Username has been set to " + msg[1]))
                    username_set = True
                    print("username set to " + msg[1])

            if prefix == 'b':
                if addr[0] in admins:
                    try:
                        banned.append(addr_from_username(msg[1]))
                        write_config()
                        send(msg[1], ('x')) #x command: disconnects client
                        send(usernames[addr], ('r', 'User banned successfully!'))
                    except:
                        send(usernames[addr], ('r', 'User does not exist'))

                else:
                    send(msg[1], ('r', 'You are not an admin!'))

            if prefix == 'a':
                if addr[0] in admins:
                    try:
                        banned.remove(addr_from_username(msg[1]))
                        write_config()
                        send(usernames[addr], ('r', 'User unbanned successfully!'))
                    except:
                        send(usernames[addr], ('r', 'User is not banned!'))
                        send(usernames[addr], ('r', addr_from_username(msg[1])))
                    
                else:
                    send(msg[1], ('r', 'You are not an admin!'))

            if prefix == 'd':
                try:
                    send(msg[1], ('d', msg[2], usernames[addr]))
                except:
                    conn.send(pickle.dumps(('r', "User does not exist.")))

                

            print(f"[{str(addr).strip('(').strip(')')}] {msg}")
            
            if is_command == False:
                try:
                    send_to_all(msg[1], usernames[addr])
                except KeyError:
                    usernames[addr] = threading.activeCount() - 1
                    send_to_all(msg[1], usernames[addr])

    send_object_to_all(('l', usernames[addr]))
    time.sleep(0.5)
    online_users.remove(usernames[addr])
    connections.remove(conn) #Remove from connections list
    del conn_usernames[usernames[addr]]
    del usernames[addr]
    conn.close()
    print("Closed connection.")


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr)) #Create a new thread for every client that joins
        thread.start()
        connections.append(conn) #Append the connection object for send_to_all() to loop through 
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()

