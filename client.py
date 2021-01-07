import socket
import pickle
import tkinter
from tkinter import simpledialog
import threading
from playsound import playsound
import time


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
}
theme = themes['beach']
muted = False

top = tkinter.Tk()
top.title('PyChat')
top.geometry('400x360')
top.resizable(False, False)
top.configure(bg=theme[0])

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "disconnect"
time.sleep(0.4)
SERVER = simpledialog.askstring("Server chooser", "Type the hostname or ip of a server: ")
if SERVER == "local" or SERVER == 'l':
    SERVER = socket.gethostname()
ADDR = (SERVER, PORT)

username = tkinter.simpledialog.askstring("Username", "Choose a username")

emojis = ["😀","😃","😄","😁","😆","😂","😊", "😉", "😛", "😎", "😭"]

#Init socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

#Init UI

messages_frame = tkinter.Frame(top)
msg_list = tkinter.Listbox(messages_frame, height=15, width=50)
msg_list.config(bg=theme[1])
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entrymsg = tkinter.StringVar()
entry_field = tkinter.Entry(top, textvariable=entrymsg)


#def send_current_text(key): print(key) #send(entry_field.get()) and 
#entry_field.bind('<Enter>', send_current_text)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=lambda: send(entry_field.get()))
send_button.pack()

variable = tkinter.StringVar(top)
variable.set(emojis[0])
emoji_opt = tkinter.OptionMenu(top, variable, *emojis)
emoji_opt.pack(side=tkinter.LEFT)
print(variable.get())

def send_emoji(): entrymsg.set(entrymsg.get() + variable.get()[0])

emoji_button = tkinter.Button(top, text="➡️", command=send_emoji)
emoji_button.pack(side=tkinter.LEFT)


msg_list.insert(tkinter.END, "[SYSTEM] Welcome to PyChat! Type /help to list commands")

#handles close window event
def close_window():
    send(DISCONNECT_MESSAGE)
    exit()
top.protocol("WM_DELETE_WINDOW", close_window)


def send(msg):
    global muted

    if msg[0] == '/':
        is_command = True
        if not muted:
            playsound('resources/command.mp3')
    else:
        is_command = False
        if not muted:
            playsound('resources/send.mp3')

    

    entry_field.delete(0, 'end')

    if msg[1:9] == 'username':
        username = msg[10:len(msg)]
        msg_list.insert(tkinter.END, "[SYSTEM] Username has been set to " + msg[10:len(msg)])
        msg_list.yview(tkinter.END)
        msg = ('u', msg[10:len(msg)]) #example: ('u', 'A_Person')

    elif msg[1:7] == 'theme ':
        try:
            theme = themes[msg[7:len(msg)]]
            top.configure(bg=theme[0])
            msg_list.config(bg=theme[1])
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
    elif msg[1:7] == 'mute':
        muted = False
        msg_list.insert(tkinter.END, "[SYSTEM] Unuted notifications")
        msg_list.yview(tkinter.END)


    elif msg[1:5] == 'help':
        msg_list.insert(tkinter.END, "• /username [your_username]  - Set a username")
        msg_list.insert(tkinter.END, "• /disconnect  - Disconnect from the server")
        msg_list.insert(tkinter.END, "• /theme [theme name]  - Switch colour theme")
        msg_list.insert(tkinter.END, "• /themes  - List theme names")
        msg_list.insert(tkinter.END, "• /mute  - Mute notification sounds")
        msg_list.insert(tkinter.END, "• /unmute  - Unute notification sounds")
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

    while True:
        #recive messages
        recived_msg = pickle.loads(client.recv(2048))
        print(recived_msg)

        prefix = recived_msg[0]

        if not prefix in ['u']:
            if not recived_msg[2] == username:  #Play message recive sound if the message isnt from the user
                if not muted:
                    if '@' + username in recived_msg:
                        playsound('resources/mention.mp3')
                    else:
                        playsound('resources/recive.mp3')
            
            msg_list.insert(tkinter.END, recived_msg[2] + ': ' + recived_msg[1])
            msg_list.yview(tkinter.END)


send('/username ' + username) #Set username

rcv_thread = threading.Thread(target=recive)
rcv_thread.start()

tkinter.mainloop()