import socket
import pickle
import tkinter
from tkinter import simpledialog
import tkinter.font as tkFont
import threading
from playsound import playsound
import time
import json
import random

#Theme presets
themes = {
    'beach': ['light sea green', 'pale goldenrod'],
    'ocean': ['aquamarine', 'turquoise'],
    'spring': ['spring green', 'lime green'],
    'night': ['gray16', 'slate grey'],
    'sunset': ['dark orange', 'indian red'],
    'alpine': ['snow', 'lavender'],
    'rose': ['peach puff', 'pink'],
    'sweden': ['blue2', 'yellow'],
    'coal': ['grey12', 'grey29']
    #'dark': ['grey10', 'grey16']
}


#Load config.json

with open("resources/client/config.json", 'r') as file:

    data = json.load(file)

    theme = themes[data["theme"]]
    theme_name = data["theme"]
    muted = data["muted"]

def save_config():
    global theme_name
    global muted

    with open("resources/client/config.json", 'w') as file:

        data["theme"] = theme_name
        data["muted"] = muted

        file = json.dump(data, file)


HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "disconnect"
time.sleep(0.4)

server_bound = False

client = ''

def connect(server, port, username):
    global server_bound
    global client

    ADDR = (server, port)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setdefaulttimeout(7)
    try:
        client.connect(ADDR)
    except ConnectionRefusedError:
        tkinter.messagebox.showinfo("Error", "Server is not running.")
        top.destroy()
        exit()
    except socket.gaierror:
        tkinter.messagebox.showinfo("Error", "Host does not exist or is not online.")
        top.destroy()
        exit()
    #except:
        #tkinter.messagebox.showinfo("Error", "An unexpected error occured.")
    
    time.sleep(1)
    server_bound = True
    print("Bound to server")


top = tkinter.Tk()
top.title('PyChat')
top.resizable(False, False)
top.configure(bg=theme[0])

font = tkFont.Font(family="System",size=12)

username = tkinter.simpledialog.askstring("Username", "Choose a username")

space = tkinter.Label(bg=theme[0])
space2 = tkinter.Label(bg=theme[0])
space3 = tkinter.Label(bg=theme[0])

v = tkinter.IntVar()
v.set(1)

def set_official_server():
    server_entry.delete(0, 'end')
    port_entry.delete(0, 'end')
    server_entry.insert(0, '45.80.160.111')
    port_entry.insert(0, '49001')

def set_custom_server():
    server_entry.delete(0, 'end')
    port_entry.delete(0, 'end')



custom_server = tkinter.Radiobutton(text="Custom server", variable=v, value=101, command=set_custom_server)
default_server = tkinter.Radiobutton(text="Official server", variable=v, value=102, command=set_official_server)
server_label = tkinter.Label(text="Server adress")
server_entry = tkinter.Entry()
port_label = tkinter.Label(text="Port number")
port_entry = tkinter.Entry()

def connect_to_current_server(key): connect(server_entry.get(), int(port_entry.get()), username)
port_entry.bind('<Return>', connect_to_current_server)

connect_button = tkinter.Button(text="Connect!",bg=theme[1], command=lambda: connect(server_entry.get(), int(port_entry.get()), username))

custom_server.pack()
default_server.pack()
space2.pack()
server_label.pack()
server_entry.pack()
space.pack()
port_label.pack()
port_entry.pack()
space.pack()
space3.pack()
connect_button.pack()

print("UI initialised")


join_messages = ["is here!", "just joined!", "arived!", "popped in!"]
leave_messages = ["just left...", "exited", "left the chat.", "ran off"]

#handles close window event
def close_window():
    save_config() #Save theme, muted, etc.
    if server_bound:
        send(DISCONNECT_MESSAGE)
    else:
        pass
    time.sleep(0.7)
    running = False
    top.destroy()
    exit()
top.protocol("WM_DELETE_WINDOW", close_window)

def send(msg):  #takes in a string from entry field3.
    
    global username
    global entry_field
    global muted
    global theme_name

    if msg[0] == '/':  #checking if message is command
        is_command = True
        if not muted:
            playsound('resources/client/command.mp3')
    else:
        is_command = False
        if not muted:
            playsound('resources/client/send.mp3')

    

    entry_field.delete(0, 'end')


    if msg[1:7] == 'theme ':
        try:
            theme = themes[msg[7:len(msg)]]
            theme_name = msg[7:len(msg)]
            top.configure(bg=theme[0])
            msg_list.config(bg=theme[1])
            user_list.config(bg=theme[1])
            space3.config(bg=theme[0])
            msg_list.insert(tkinter.END, "[SYSTEM] Theme has been set to " + msg[7:len(msg)])
            msg_list.yview(tkinter.END)
        except KeyError:
            msg_list.insert(tkinter.END, "[SYSTEM] " +  msg[7:len(msg)] + " is not a valid theme.")
            msg_list.yview(tkinter.END)
        return 0

    elif msg[1:7] == 'themes':
        for theme in themes.keys():
            msg_list.insert(tkinter.END, "•" + theme)
            msg_list.yview(tkinter.END)

    elif msg[1:5] == 'mute':
        muted = True
        msg_list.insert(tkinter.END, "[SYSTEM] Muted notifications")
        msg_list.yview(tkinter.END)
    elif msg[1:7] == 'unmute':
        muted = False
        msg_list.insert(tkinter.END, "[SYSTEM] Unuted notifications")
        msg_list.yview(tkinter.END)

    elif msg[1:4] == 'ban':
        member = msg[5:len(msg)]
        msg = ('b', member)
    elif msg[1:6] == 'unban':
        member = msg[7:len(msg)]
        msg = ('a', member)

    elif msg[1:3] == 'dm':
        whole = msg[4:len(msg)]
        print(whole)
        i=0
        for char in whole:
            print(char)
            i+=1
            if char == " ":
                print("Blank!!!")
                from_char = i
                break

        member = whole[0:from_char-1]

        if member == username:
            msg_list.insert(tkinter.END, "[SYSTEM] You can't DM yourself!!")
            return 0

        print("Member: " + member)
        message = whole[from_char:len(whole)]

        msg_list.insert(tkinter.END, "[DM] " + username + ": " + message)
        msg_list.yview(tkinter.END)
        msg = ('d', member, message)

    elif msg[1:5] == 'help':
        msg_list.insert(tkinter.END, "• /disconnect  - Disconnect from the server")
        msg_list.insert(tkinter.END, "• /dm [username] [message]  - Direct message a user")
        msg_list.insert(tkinter.END, "• /theme [theme name]  - Switch colour theme")
        msg_list.insert(tkinter.END, "• /themes  - List theme names")
        msg_list.insert(tkinter.END, "• /mute  - Mute notification sounds")
        msg_list.insert(tkinter.END, "• /unmute  - Unute notification sounds")
        msg_list.insert(tkinter.END, "• /ban [username]  - Ban someone from the server")
        msg_list.yview(tkinter.END)
        return 0
        
    else:
        print(msg)
        is_command = False
        msg = ('m', msg) #  ( message type goes here , args go here )
    

    entry_field.config(textvariable=None)

    message = pickle.dumps(msg)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


def recive():
    global muted
    global msg_list
    global user_list
    running = True

    while running:
        #recive messages
        recived_msg = pickle.loads(client.recv(2048))
        print(recived_msg)

        prefix = recived_msg[0]

        
        if prefix == 'x':
            msg_list.insert(tkinter.END, "[SYSTEM] You have been banned from the server.")
            msg_list.yview(tkinter.END)
            running = False
            time.sleep(2)
            top.destroy()

        if prefix == 'r':
            msg_list.insert(tkinter.END, "[SYSTEM] " + str(recived_msg[1]))
            msg_list.yview(tkinter.END)

        if prefix == 'd': #A DM was recived
            msg_list.insert(tkinter.END, "[DM] " + recived_msg[2] + ": " + recived_msg[1])
            msg_list.yview(tkinter.END)
            if not muted:
                playsound("resources/client/mention.mp3")
        
        if prefix == 'j':  #Someone joined
            msg_list.insert(tkinter.END, "> " + recived_msg[1] + " " + join_messages[random.randint(0, len(join_messages) - 1)])
            msg_list.yview(tkinter.END)
            user_list.insert(tkinter.END, recived_msg[1])

        if prefix == 'l':  #Someone joined
            msg_list.insert(tkinter.END, "< " + recived_msg[1] + " " + leave_messages[random.randint(0, len(leave_messages) - 1)])
            msg_list.yview(tkinter.END)
            idx = user_list.get(0, tkinter.END).index(recived_msg[1])
            user_list.delete(idx)

        if prefix == 'o':  #List of online members
            for user in recived_msg[1]:
                user_list.insert(tkinter.END, user)
        
        try:
            if prefix in ['m'] and not recived_msg[2] == "disconnect":
                msg_list.insert(tkinter.END, recived_msg[2] + ': ' + recived_msg[1])
                msg_list.yview(tkinter.END)

                if not recived_msg[2] == username:  #Play message recive sound if the message isn't from the user
                    if not muted:
                        if '@' + username in recived_msg:
                            playsound('resources/client/mention.mp3')
                        else:
                            playsound('resources/client/recive.mp3')
        except IndexError:
            pass

def clock():
    while True:
        time.sleep(4)
        msg = ('k', '') #Send keepalive
        message = pickle.dumps(msg)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(message)


msg_list = None
user_list = None
entry_field = None

def on_start():
    global client
    global msg_list
    global user_list
    global entry_field

    while True:
        if server_bound == True: #Only start once the user has entered a server and port
            
            custom_server.destroy()
            default_server.destroy()
            space2.destroy()
            server_label.destroy()
            server_entry.destroy()
            space.destroy()
            port_label.destroy()
            port_entry.destroy()
            connect_button.destroy()
            server_entry.destroy()
            port_entry.destroy()


            try:
                emojis = ["😀","😃","😄","😁","😆","😂","😊", "😉", "😛", "😎", "😭"]
            except:
                emojis = [" Not supported"]


            #Init UI
            top.geometry('710x430')

            messages_frame = tkinter.Frame(top)
            msg_list = tkinter.Listbox(messages_frame, height=16, width=60)
            msg_list.config(bg=theme[1], font=font)
            msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
            msg_list.pack()
            messages_frame.pack()

            users_frame = tkinter.Frame(top)
            user_list = tkinter.Listbox(messages_frame, height=15, width=15)
            user_list.config(bg=theme[1])
            user_list.pack(side=tkinter.RIGHT, fill=tkinter.BOTH)
            user_list.pack()
            users_frame.pack()
            user_list.insert(tkinter.END, "ONLINE USERS:")
            entrymsg = tkinter.StringVar()
            entry_field = tkinter.Entry(top, textvariable=entrymsg)

            def send_current_text(key): send(entry_field.get()) #Its working now but I need to pass in params
            entry_field.bind('<Return>', send_current_text)

            entry_field.pack()
            send_button = tkinter.Button(top, text="Send", command=lambda: send(entry_field.get())) 
            send_button.pack()

            variable = tkinter.StringVar(top)
            variable.set(emojis[0])
            emoji_opt = tkinter.OptionMenu(top, variable, *emojis)
            emoji_opt.pack(side=tkinter.LEFT)

            def send_emoji(): entrymsg.set(entrymsg.get() + variable.get()[0])

            emoji_button = tkinter.Button(top, text="➡️", command=send_emoji)
            emoji_button.pack(side=tkinter.LEFT)

            msg_list.insert(tkinter.END, "[SYSTEM] Welcome to PyChat! Type /help to list commands")



            msg = ('u', username) #Send username

            message = pickle.dumps(msg)
            msg_length = len(message)
            send_length = str(msg_length).encode(FORMAT)
            send_length += b' ' * (HEADER - len(send_length))
            client.send(send_length)
            client.send(message)

            rcv_thread = threading.Thread(target=recive)
            rcv_thread.start()
            clock_thread = threading.Thread(target=clock)
            clock_thread.start()

            break


on_start_thread = threading.Thread(target=on_start) 
on_start_thread.start()

tkinter.mainloop()