import socket 
import threading
import pickle

HEADER = 64
PORT = 5050
SERVER = "0.0.0.0"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "disconnect"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDR)


connections = []
usernames = {}


def send_to_all(msg, user):
    msg = ('m', msg, user)
    for conn in connections:
        conn.send(pickle.dumps(msg))



def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
        except:
            connected = False #Disconnect if failed to recive header
        
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
                usernames[addr] = msg[1]

            print(f"[{str(addr).strip('(').strip(')')}] {msg}")
            
            if is_command == False:
                try:
                    send_to_all(msg[1], usernames[addr])
                except KeyError:
                    send_to_all(msg[1], "Anon")

    conn.close()
    connections.remove(conn) #Remove from connections list


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
