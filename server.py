import socket 
import threading
import pickle
import time
import traceback

HEADER = 64
PORT = input("Type a port >> ")
if PORT == "":
    PORT = 49001 #Default port
try:
    PORT = int(PORT)
except:
    print("Not a valid port. running on default port...")
SERVER = "0.0.0.0"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "disconnect"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDR)


connections = []
usernames = {}
user_colours = {}
valid_colours = ["green", "orange", "blue", "purple", "red", "turquoise", "red4"]
conn_usernames = {}
online_users = []

message_history = []

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

def send_to_all(msg, user, colour):
    msg = ('m', msg, user, colour)
    message_history.append(msg)
    for conn in connections:
        conn.send(pickle.dumps(msg))

def send_object_to_all(object):
    for conn in connections:
        conn.send(pickle.dumps(object))

def send(user, msg):
    conn = conn_usernames[user] # Get connection object from conn_usernames
    conn.send(pickle.dumps(msg))


def handle_client(conn, addr):
    server.settimeout(6)

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

        if username_set and not join_message_sent:
            time.sleep(0.5)
            send_object_to_all(('j', usernames[addr], user_colours[addr]))
            online_users.append(usernames[addr])
            print(online_users)
            join_message_sent = True


        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)

            if msg_length:
                msg_length = int(msg_length)
            
                try:
                    msg = conn.recv(msg_length)
                except:
                    connected = False

                msg = pickle.loads(msg)

                prefix = msg[0]
                if prefix == 'm':
                    is_command = False
                else:
                    is_command = True

                if msg[1] == DISCONNECT_MESSAGE:
                    connected = False

                if prefix == 'u':
                    username = msg[1].replace(' ', '')

                    if msg[1] in usernames.values():
                        time.sleep(0.5)
                        send(usernames[addr], ('r', "That username is taken. please choose another."))
                        print("username taken")
                    else:
                        usernames[addr] = username #set username
                        user_colours[addr] = msg[2] #set colour
                        print(usernames)
                        conn_usernames[username] = conn
                        send(usernames[addr], ('r', "Username has been set to " + username))
                        username_set = True
                        print("username set to " + username)

                if prefix == 'b': #ban
                    if addr[0] in admins:
                        try:
                            banned.append(addr_from_username(msg[1]))
                            write_config()
                            send(msg[1], ('x')) #x command: disconnects client
                            send(usernames[addr], ('r', 'User banned successfully!'))
                        except:
                            send(usernames[addr], ('r', 'User does not exist'))

                    else:
                        send(usernames[addr], ('r', 'You are not an admin!'))
                        print("Not admin")
                        print(admins)
                        print(addr[0])

                if prefix == 'a': #unban
                    if addr[0] in admins:
                        try:
                            banned.remove(addr_from_username(msg[1]))
                            write_config()
                            send(usernames[addr], ('r', 'User unbanned successfully!'))
                        except:
                            send(usernames[addr], ('r', 'User is not banned!'))
                            send(usernames[addr], ('r', addr_from_username(msg[1])))
                        
                    else:
                        send(usernames[addr], ('r', 'You are not an admin!'))

                if prefix == 'd':
                    try:
                        send(msg[1], ('d', msg[2], usernames[addr], user_colours[addr]))
                        message_history.append(('d', msg[2], usernames[addr], user_colours[addr]))
                    except:
                        conn.send(pickle.dumps(('r', "User does not exist.")))

                if prefix == 'c':
                    if msg[1] in valid_colours:
                        user_colours[addr] = msg[1]
                        send(usernames[addr], ('r', 'Changed username colour to ' + msg[1]))
                    else:
                        send(usernames[addr], ('r', 'That is not a valid colour. type \'/colours\'.'))

                if prefix == 'h': # WORK IN PROGRESS
                    print("Sending history to client...")

                    if len(message_history) < 15:
                        number = len(message_history)
                    else:
                        number = 15
                    
                    history_object = []

                    for i in range(number):
                        if message_history[i][0] == 'm':
                            history_object.append(message_history[i])
                            print(message_history[i])

                    history_object = tuple(history_object)

                    send(usernames[addr], ('h', history_object))
                
                if is_command == False:
                    try:
                        send_to_all(msg[1], usernames[addr], user_colours[addr])
                    except KeyError:
                        usernames[addr] = threading.activeCount() - 1
                        send_to_all(msg[1], usernames[addr], "red")

                if not prefix == 'k':
                    print(f"[{str(addr).strip('(').strip(')')}] {msg}")

            else: #Disconnect client if header is blank
                print("Blank header")
                connected = False
        
        except socket.timeout: #timeout
            connected = False #Disconnect if failed to recive header
            print("Timeout")


    online_users.remove(usernames[addr])
    connections.remove(conn) #Remove from connections list
    try:
        del conn_usernames[usernames[addr]]
    except:
        pass
    send_object_to_all(('l', usernames[addr]))
    try:
        del usernames[addr]
    except:
        pass
    time.sleep(0.5)
    conn.close()
    print("Closed connection.")


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        try:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr)) #Create a new thread for every client that joins
            thread.start()
            connections.append(conn) #Append the connection object for send_to_all() to loop through
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
        except socket.timeout:
            pass


print("[STARTING] server is starting...")
start()
