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
import textwrap
import webbrowser #For /discord command
import hashlib
import difflib

HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "disconnect"
running = True

#Theme presets
themes = {
    'beach': ['light sea green', 'pale goldenrod'],
    'sky': ['SkyBlue1', 'powder blue'],
    'night': ['gray16', 'slate grey'],
    'alpine': ['snow', 'lavender'],
    'rose': ['peach puff', 'pink'],
    'sweden': ['blue2', 'gold'],
    'coal': ['grey12', 'grey29'],
    'spring': ['PaleGreen1', 'turquoise']
}

colour_set = False
user_colours = ["green", "orange", "blue", "purple", "red", "turquoise", "red4"]

#Load config.json

with open("resources/client/config.json", 'r') as file:

    data = json.load(file)

    theme = themes[data["theme"]]
    theme_name = data["theme"]
    muted = data["muted"]
    try:
        user_colour = data["user_colour"]
        colour_set = True
    except:
        user_colour = user_colours[random.randint(0, len(user_colours) - 1)]
        colour_set = False
    try: username = data["username"]
    except: username = ""

#Save config

def save_config():
    global theme_name
    global muted
    global colour_set
    global user_colour
    global username
    global plaintext_password

    with open("resources/client/config.json", 'w') as file:

        data["theme"] = theme_name
        data["muted"] = muted
        data["username"] = username
        #data["password"] = str(plaintext_password.encode(FORMAT))
        if colour_set: data["user_colour"] = user_colour
        file = json.dump(data, file)


join_messages = ["is here!", "just joined!", "arived!", "popped in!"]
leave_messages = ["just left...", "exited", "left the chat.", "ran off"]

commands = ['help', 'mute', 'unmute', 'dm', 'ban', 'unban', 'themes', 'theme', 'colours', 'colour', 'inbox', 'discord']

server_bound = False

client = None

def connect(server, port):
    global server_bound
    global client

    ADDR = (server, port)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setdefaulttimeout(7)
    try:
        client.connect(ADDR)
    except ConnectionRefusedError:
        popupwin("Error", "Server is not running.", False)
        return 0
    except socket.gaierror:
        popupwin("Error", "Host does not exist or is not online.", False)
        return 0
    except:
        popupwin("Error", "An unexpected error occured.", False)
        return 0
    
    time.sleep(1)
    server_bound = True
    print("Bound to server")


top = tkinter.Tk()
top.title('PyChat login')
top.resizable(False, False)
top.configure(bg=theme[0])

font = tkFont.Font(family="Courier New",size=11)


def choosefunc(choice, tl, fatal):
    global running

    if choice == 'ok':
        tl.destroy()
        if fatal:
            print("Exiting...")
            top.destroy()
            running = False
            exit()

def popupwin(title, message, fatal):

    tl = tkinter.Toplevel(top, bg=theme[0])
    tl.title(title)


    msgbody1 = tkinter.Label(tl, text=message, font=("Courier New", 15, "bold"), bg=theme[0], activebackground=theme[0])
    msgbody1.pack()

    okbttn = tkinter.Button(tl, text="OK", command=lambda: choosefunc("ok", tl, fatal), width=10, bg=theme[1])
    okbttn.pack()

#username = tkinter.simpledialog.askstring("Username", "Choose a username")
#password = tkinter.simpledialog.askstring("Password", "Type your password")

password = None
#plaintext_password = None


login_title = tkinter.Label(text="Login or register", bg=theme[1], font=("Helvetica", 11, 'bold'))
login_space = tkinter.Label(text=" ", bg=theme[0])
login_title.pack()
login_space.pack()

def login(*key):
    global username
    global password
    global plaintext_password

    username = username_entry.get()
    password = password_entry.get()
    #plaintext_password = password
    password = hashlib.md5(password.encode(FORMAT)).hexdigest()

    var.set(1)

var = tkinter.IntVar()
username_label = tkinter.Label(text="Username", bg=theme[0])
password_label = tkinter.Label(text="Password", bg=theme[0])
username_entry = tkinter.Entry(bg=theme[0], fg='black', highlightthickness=1, justify='center')
username_entry.focus_set()
username_entry.insert(0, username) #insert saved username


password_entry = tkinter.Entry(bg=theme[0], fg='black', highlightthickness=1, justify='center', show='•')
ok_button = tkinter.Button(text="Ok", command=login, bg=theme[1], activebackground=theme[1])
username_entry.bind('<Return>', login)
password_entry.bind('<Return>', login)
if len(username) > 0:
    password_entry.focus_set() #Set focus on password field if username has been saved

username_label.pack()
username_entry.pack()
password_label.pack()
password_entry.pack()
ok_button.pack(pady=4)


ok_button.wait_variable(var) #Wait for ok button to be pressed

login_title.destroy()
login_space.destroy()
username_label.destroy()
username_entry.destroy()
password_label.destroy()
password_entry.destroy()
ok_button.destroy()


space = tkinter.Label(bg=theme[0])
space2 = tkinter.Label(bg=theme[0])
space3 = tkinter.Label(bg=theme[0])

def set_official_server():
    server_entry.delete(0, 'end')
    port_entry.delete(0, 'end')
    server_entry.insert(0, '45.80.160.111')
    port_entry.insert(0, '49001')

def set_custom_server():
    server_entry.delete(0, 'end')
    port_entry.delete(0, 'end')

top.title('Server selector')
v = tkinter.IntVar(); v.set(1)
custom_server = tkinter.Radiobutton(text="Custom server", variable=v, value=2, command=set_custom_server, bg=theme[0], highlightthickness=0)
default_server = tkinter.Radiobutton(text="Official server ", variable=v, value=1, command=set_official_server, bg=theme[0], highlightthickness=0)
server_label = tkinter.Label(text="Server adress", bg=theme[0])
server_entry = tkinter.Entry(bg=theme[0], fg='black', highlightthickness=1, justify='center')
port_label = tkinter.Label(text="Port number", bg=theme[0])
port_entry = tkinter.Entry(bg=theme[0], fg='black', highlightthickness=1, justify='center')

set_official_server() # Default server is selected by default

def connect_to_current_server(key): connect(server_entry.get(), int(port_entry.get()))
port_entry.bind('<Return>', connect_to_current_server)
server_entry.bind('<Return>', connect_to_current_server)

connect_button = tkinter.Button(text="Connect!", bg=theme[1], activebackground=theme[1], command=lambda: connect(server_entry.get(), int(port_entry.get())))
connect_button.bind('<Return>', connect_to_current_server)
connect_button.focus_set()

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


#handles close window event
def close_window():
    global running

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
    global user_colour
    global entry_field
    global muted
    global theme_name
    global theme
    global running

    global inbox_window
    global inbox_list
    global refresh_button

    if msg == '': #Don't send if message is blank
        return 0

    if msg[0] == '/':  #checking if message is command
        is_command = True
        if not muted:
            playsound('resources/client/command.mp3')

    else:
        is_command = False
        if not muted:
            playsound('resources/client/send.mp3')

    

    entry_field.delete(0, 'end')

    if is_command: # Don't send if message is command

        if msg[1:11] == 'disconnect':
            msg_list.insert(tkinter.END, "[SYSTEM] Disconnecting... " + '\n')
            current_line = str(int(msg_list.index('end').split('.')[0]) - 2)
            msg_list.tag_add("hilight_system", current_line + ".0", current_line + "." + "8") #Hilight [SYSTEM]
            msg_list.tag_config("hilight_system", foreground="blue")
            top.update()
            msg_list.yview(tkinter.END)

            save_config() #Save theme, muted, etc.
            if server_bound:
                send(DISCONNECT_MESSAGE)
            else:
                pass
            time.sleep(1)
            running = False
            top.destroy()
            exit()

        elif msg[1:7] == 'theme ':
            try:
                theme = themes[msg[7:len(msg)]]
                theme_name = msg[7:len(msg)]
                
                #Update UI
                top.configure(bg=theme[0])
                msg_list.config(bg=theme[1])
                user_list.config(bg=theme[1])
                space3.config(bg=theme[0])
                entry_field.config(bg=theme[0], highlightthickness=1)
                msg_list.config(bg=theme[1], font=font, selectbackground=theme[0], highlightcolor=theme[0])
                send_button.config(bg=theme[1], highlightthickness=0, activebackground=theme[1])
                emoji_opt.config(bg=theme[1], highlightthickness=0, activebackground=theme[1])
                emoji_button.config(bg=theme[1], highlightthickness=0, activebackground=theme[1])

                #Update inbox UI
                try:
                    inbox_window.configure(bg=theme[0])
                    inbox_list.config(bg=theme[1], font=font, selectbackground=theme[0], highlightcolor=theme[0])
                    refresh_button.config(bg=theme[1], highlightthickness=0, activebackground=theme[1])
                except: pass  #If window is not open

                msg_list.insert(tkinter.END, "[SYSTEM] Theme has been set to " + msg[7:len(msg)] + '\n')

                current_line = str(int(msg_list.index('end').split('.')[0]) - 2)

                msg_list.tag_add("hilight_system", current_line + ".0", current_line + "." + "8") #Hilight [SYSTEM]
                msg_list.tag_config("hilight_system", foreground="blue")
                top.update()

                msg_list.yview(tkinter.END)

            except KeyError:
                msg_list.insert(tkinter.END, "[SYSTEM] " +  msg[7:len(msg)] + " is not a valid theme." + '\n')

                current_line = str(int(msg_list.index('end').split('.')[0]) - 2)
                msg_list.tag_add("hilight_system", current_line + ".0", current_line + "." + "8") #Hilight [SYSTEM]
                msg_list.tag_config("hilight_system", foreground="blue")
                top.update()

                msg_list.yview(tkinter.END)
            return 0

        elif msg[1:7] == 'themes':
            for theme in themes.keys():
                msg_list.insert(tkinter.END, "•" + theme + '\n')
                msg_list.yview(tkinter.END)

        elif msg[1:5] == 'mute':
            muted = True
            msg_list.insert(tkinter.END, "[SYSTEM] Muted notifications" + '\n')

            current_line = str(int(msg_list.index('end').split('.')[0]) - 2)
            msg_list.tag_add("hilight_system", current_line + ".0", current_line + "." + "8") #Hilight [SYSTEM]
            msg_list.tag_config("hilight_system", foreground="blue")
            top.update()
            msg_list.yview(tkinter.END)

        elif msg[1:8] == 'colour ': # English spelling
            user_colour = msg[8:len(msg)]
            msg = ('c', msg[8:len(msg)])

        elif msg[1:7] == 'color ': # American spelling
            user_colour = msg[7:len(msg)]
            msg = ('c', msg[7:len(msg)])

        elif msg[1:8] == 'colours' or msg[1:7] == 'colors':
            for colour in user_colours:
                msg_list.insert(tkinter.END, "•" + colour + '\n')
                msg_list.yview(tkinter.END)

        elif msg[1:7] == 'unmute':
            muted = False
            msg_list.insert(tkinter.END, "[SYSTEM] Unuted notifications" + '\n')

            current_line = str(int(msg_list.index('end').split('.')[0]) - 2)
            msg_list.tag_add("hilight_system", current_line + ".0", current_line + "." + "8") #Hilight [SYSTEM]
            msg_list.tag_config("hilight_system", foreground="blue")
            top.update()

            msg_list.yview(tkinter.END)

        elif msg[1:8] == 'sendobj':
            obj = msg[9:len(msg)]
            msg = eval(obj)

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
                msg_list.insert(tkinter.END, "[SYSTEM] You can't DM yourself!!" + '\n')
                
                current_line = str(int(msg_list.index('end').split('.')[0]) - 2)
                msg_list.tag_add("hilight_system", current_line + ".0", current_line + "." + "8") #Hilight [SYSTEM]
                msg_list.tag_config("hilight_system", foreground="blue")
                top.update()

                return 0
            else:
                message = whole[from_char:len(whole)]

                msg_list.insert(tkinter.END, "[DM] You --> " + member + ": " + message + '\n')
                
                current_line = str(int(msg_list.index('end').split('.')[0]) - 2)
                msg_list.tag_add("hilight-" + username, current_line + ".5", current_line + "." + str(3 + 5)) #Hilight the username
                msg_list.tag_config("hilight-" + username, foreground=user_colour)
                top.update()

                msg_list.yview(tkinter.END)
                msg = ('d', member, message)

        elif msg[1:6] == 'inbox':
            msg = ('i')

        elif msg[1:8] == 'discord':
            webbrowser.open("https://discord.gg/nmza5KPfQb")

        elif msg[1:5] == 'help':
            msg_list.insert(tkinter.END, "• /disconnect  - Disconnect from the server" + '\n')
            msg_list.insert(tkinter.END, "• /dm [username] [message]  - Direct message a user" + '\n')
            msg_list.insert(tkinter.END, "• /inbox - View your inbox" + '\n')
            msg_list.insert(tkinter.END, "• /theme [theme name]  - Switch colour theme" + '\n')
            msg_list.insert(tkinter.END, "• /themes  - List theme names" + '\n')
            msg_list.insert(tkinter.END, "• /mute  - Mute notification sounds" + '\n')
            msg_list.insert(tkinter.END, "• /unmute  - Unute notification sounds" + '\n')
            msg_list.insert(tkinter.END, "• /ban [username]  - Ban someone from the server" + '\n')
            msg_list.insert(tkinter.END, "• /colour [colour name]  - Set your username to a colour" + '\n')
            msg_list.insert(tkinter.END, "• /colours - List all username colours" + '\n')
            msg_list.insert(tkinter.END, "• /discord - Join the official discord server!" + '\n')
            msg_list.yview(tkinter.END)
            return 0

        else: # Not valid command
            matches = difflib.get_close_matches(msg[1:len(msg)], commands)

            if len(matches) > 0:
                msg_list.insert(tkinter.END, '[SYSTEM] That is not a command. Did you mean "/' + matches[0] + '\"?' + '\n')
            else:
                msg_list.insert(tkinter.END, '[SYSTEM] That is not a command. Type /help' + '\n')
            
            current_line = str(int(msg_list.index('end').split('.')[0]) - 2)
            msg_list.tag_add("hilight_system", current_line + ".0", current_line + "." + "8") #Hilight [SYSTEM]
            msg_list.tag_config("hilight_system", foreground="blue")
            top.update()

            msg_list.yview(tkinter.END)

    if not is_command:
        msg = ('m', msg) #  ( message/command type goes here , args go here )
        print(msg)
    

    entry_field.config(textvariable=None)

    message = pickle.dumps(msg)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    
    try:
        client.send(send_length)
        client.send(message)
    except ConnectionResetError:
        return 0
    except BrokenPipeError:
        popupwin("Info", "Lost connection with server.", True)
        print("Exited send")
        return 0

#Make inbox UI global
inbox_window = None
inbox_list = None
refresh_button = None

def recive():
    global muted
    global msg_list
    global user_list
    global running
    global colour_set

    global inbox_list
    global inbox_window
    global refresh_button

    timeout = False
    history_recived = False

    while running:

        #recive messages
        try:
            msg_length = client.recv(HEADER).decode(FORMAT)

            if msg_length:
                msg_length = int(msg_length)
            
                try:
                    msg = client.recv(msg_length)
                except:
                    connected = False

                recived_msg = pickle.loads(msg)
                print(recived_msg)
                timeout = False
            else:
                timeout = True
                connected = False
    
        except EOFError: #If server is not responding
            if running:
                popupwin("Info","Server closed.", True)
            else:
                print("exited recive")
                return 0
        except socket.timeout:
            print("Timeout")
            timeout = True
            pass

        if not timeout:

            prefix = recived_msg[0]

            
            if prefix == 'm':
                if recived_msg[1] == "disconnect":
                    return 0

            if prefix == 'x':
                msg_list.insert(tkinter.END, "[SYSTEM] You have been banned from the server." + '\n')

                current_line = str(int(msg_list.index('end').split('.')[0]) - 2)
                msg_list.tag_add("hilight_system", current_line + ".0", current_line + "." + "8") #Hilight [SYSTEM]
                msg_list.tag_config("hilight_system", foreground="blue")
                top.update()

                msg_list.yview(tkinter.END)
                running = False
                time.sleep(2)
                top.destroy()

            if prefix == 'r':
                msg_list.insert(tkinter.END, "[SYSTEM] " + str(recived_msg[1]) + '\n')

                current_line = str(int(msg_list.index('end').split('.')[0]) - 2)
                msg_list.tag_add("hilight_system", current_line + ".0", current_line + "." + "8") #Hilight [SYSTEM]
                msg_list.tag_config("hilight_system", foreground="blue")
                top.update()
                msg_list.yview(tkinter.END)

                if str(recived_msg[1][0:26]) == "Changed username colour to":
                    print("colour cmd")
                    colour_set = True
                    save_config()

            if prefix == 'd': #A DM was recived
                msg_list.insert(tkinter.END, "[DM] " + recived_msg[2] + ": " + recived_msg[1] + '\n')

                current_line = str(int(msg_list.index('end').split('.')[0]) - 2)
                msg_list.tag_add("hilight-" + recived_msg[2], current_line + ".5", current_line + "." + str(len(recived_msg[2]) + 5)) #Hilight the username
                msg_list.tag_config("hilight-" + recived_msg[2], foreground=recived_msg[3])
                top.update()

                msg_list.yview(tkinter.END)
                if not muted:
                    playsound("resources/client/mention.mp3")
            
            if prefix == 'j':  #Someone joined
                msg_list.insert(tkinter.END, "> " + recived_msg[1] + " " + join_messages[random.randint(0, len(join_messages) - 1)] + '\n')
                
                current_line = str(int(msg_list.index('end').split('.')[0]) - 2)
                msg_list.tag_add("hilight-" + recived_msg[2], current_line + ".2", current_line + "." + str(len(recived_msg[1]) + 2)) #Hilight the username
                msg_list.tag_config("hilight-" + recived_msg[2], foreground=recived_msg[2])
                top.update()

                msg_list.yview(tkinter.END)
                user_list.insert(tkinter.END, recived_msg[1])

            if prefix == 'l':  #Someone joined
                msg_list.insert(tkinter.END, "< " + recived_msg[1] + " " + leave_messages[random.randint(0, len(leave_messages) - 1)] + '\n')
                msg_list.yview(tkinter.END)
                idx = user_list.get(0, tkinter.END).index(recived_msg[1])
                user_list.delete(idx)

            if prefix == 'o':  #List of online members
                for user in recived_msg[1]:
                    user_list.insert(tkinter.END, user)
            
            if prefix == 'h':  #Message history
                if not history_recived:
                    history_object = recived_msg[1]
                    line_text = ""
                    line_count = 0

                    for message in history_object:
                        

                        if message[0] == 'm':
                            print(message)
                            if not message[1] == 'disconnect':
                                
                                message = list(message) #Make editable

                                wrapper = textwrap.TextWrapper(width=52)

                                formated_msg = wrapper.wrap(text=message[1])

                                i=0

                                for line in formated_msg:
                                    if i == 0: #Only show name on first line
                            
                                        line_text += message[2] + ': ' + line + '\n'
                                        line_count += 1
                                        top.update()

                                    else:
                                        line_text +=  '|   ' + line + '\n'
                                        line_count += 1

                                    i+=1
                                    msg_list.yview(tkinter.END)
                        
                        if message[0] == 'd':
                            if message[3] == username:
                                line_text += "[DM] You --> " + message[1] + ": " + message[2] + '\n'
                                line_count += 1
                            elif message[1] == username:
                                line_text +=  "[DM] " + message[3] + ": " + message[2] + '\n'
                                line_count += 1

                            top.update()

                            msg_list.yview(tkinter.END)

                    msg_list.insert('1.0', line_text)
                    msg_list.insert(str(line_count+1) + '.0', '-------------------------------CURRENT--------------------------------\n')
                    msg_list.insert(str(line_count+2) + '.0', '[SYSTEM] Welcome to PyChat! Type /help to list commands\n')

                    current_line = str(int(msg_list.index('end').split('.')[0]) - 2)
                    msg_list.tag_add("hilight_system", str(line_count+2) + ".0", str(line_count+2) + "." + "8") #Hilight [SYSTEM]
                    msg_list.tag_config("hilight_system", foreground="blue")
                    top.update()

                    msg_list.yview(tkinter.END)
                    
                    history_recived = True

            if prefix == 'i':  #Inbox (DM and @mention history)
                inbox_object = recived_msg[1]
                line_text = []
                line_count = 0

                inbox_window = tkinter.Toplevel(top)
                inbox_window.configure(bg=theme[0])
                inbox_window.resizable(False, False)
                inbox_window.title(username + "'s inbox")
                inbox_list = tkinter.Text(inbox_window, height=20, width=60)
                inbox_list.config(bg=theme[1], font=font, selectbackground=theme[0], highlightcolor=theme[0])
                inbox_list.bindtags((str(msg_list), str(top), "all"))
                inbox_list.pack()

                def refresh_inbox():
                    inbox_window.destroy()
                    send("/inbox") #Run command again to refresh

                refresh_button = tkinter.Button(inbox_window, text="Refresh", command=refresh_inbox)
                refresh_button.config(bg=theme[1], fg='black', highlightthickness=0, activebackground=theme[1])
                refresh_button.pack(pady=3)

                for message in inbox_object:
                    if message[0] == 'm':  
                        message = list(message) #Make editable

                        wrapper = textwrap.TextWrapper(width=44)

                        formated_msg = wrapper.wrap(text=message[1])

                        i=0

                        for line in formated_msg:
                            if i == 0: #Only show name on first line
                    
                                inbox_list.insert(tkinter.END, message[2] + ': ' + line + '\n')
                                line_count += 1

                                current_line = str(int(inbox_list.index('end').split('.')[0]) - 2)
                                inbox_list.tag_add("hilight-" + message[2], current_line + ".0", current_line + "." + str(len(message[2]))) #Hilight the username
                                inbox_list.tag_config("hilight-" + message[2], foreground=message[3])
                                top.update()

                            else:
                                inbox_list.insert(tkinter.END, '|   ' + line + '\n')
                                line_count += 1

                            i+=1
                            msg_list.yview(tkinter.END)
                    
                    if message[0] == 'd':
                        if message[1] == username:
                            inbox_list.insert(tkinter.END, "[DM] " + message[3] + ": " + message[2] + '\n')
                            line_count += 1

                            current_line = str(int(inbox_list.index('end').split('.')[0]) - 2)
                            inbox_list.tag_add("hilight-" + message[2], current_line + ".5", current_line + "." + str(len(message[3]) + 5)) #Hilight the username
                            inbox_list.tag_config("hilight-" + message[2], foreground=message[4])
                            top.update()


                        top.update()

                        msg_list.yview(tkinter.END)


            
            try:
                if prefix in ['m'] and not recived_msg[2] == "disconnect":
                    
                    wrapper = textwrap.TextWrapper(width=52)

                    formated_msg = wrapper.wrap(text=recived_msg[1])

                    i=0
                    print(formated_msg)
                    for line in formated_msg:
                        if i == 0: #Only show name on first line
                
                            msg_list.insert(tkinter.END, recived_msg[2] + ': ' + line + '\n')
                            current_line = str(int(msg_list.index('end').split('.')[0]) - 2)
                            msg_list.tag_add("hilight-" + recived_msg[2], current_line + ".0", current_line + "." + str(len(recived_msg[2]))) #Hilight the username
                            msg_list.tag_config("hilight-" + recived_msg[2], foreground=recived_msg[3])
                            top.update()

                        else:

                            msg_list.insert(tkinter.END, '|   ' + line + '\n')

                        i+=1

                    msg_list.yview(tkinter.END)

                    if not recived_msg[2] == username:  #Play message recive sound if the message isn't from the user
                        if not muted:
                            if '@' + username in recived_msg:
                                playsound('resources/client/mention.mp3')
                            else:
                                playsound('resources/client/recive.mp3')
            except IndexError:
                pass
        
    print("Exited recive")
    return 0

def clock():
    global running
    while running:

        for i in range(16):
            time.sleep(0.25)
            if not running:
                return 0
        
        time.sleep(4)
        msg = ('k', '') #Send keepalive
        message = pickle.dumps(msg)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        try:
            client.send(send_length)
            client.send(message)
        except BrokenPipeError:
            break
    print("exited clock")
    return 0


msg_list = None
user_list = None
entry_field = None
emoji_button = None
emoji_opt = None
send_button = None
loading = None

def on_start():
    global running
    global client
    global msg_list
    global user_list
    global entry_field
    global send_button
    global emoji_opt
    global emoji_button
    global loading

    while True:
        if server_bound: #Only start once the user has entered a server and port
            socket.setdefaulttimeout(1)

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

            top.title('PyChat')

            messages_frame = tkinter.Frame(top)
            msg_list = tkinter.Text(messages_frame, height=20, width=70)
            msg_list.config(bg=theme[1], font=font, selectbackground=theme[0], highlightcolor=theme[0])
            msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
            msg_list.bindtags((str(msg_list), str(top), "all"))
            msg_list.pack()

            messages_frame.pack()

            users_frame = tkinter.Frame(top)
            user_list = tkinter.Listbox(messages_frame, height=20, width=20)
            user_list.config(bg=theme[1])
            user_list.pack(side=tkinter.RIGHT, fill=tkinter.BOTH)
            user_list.pack()
            users_frame.pack()
            user_list.insert(tkinter.END, "ONLINE USERS:")
            entrymsg = tkinter.StringVar()
            entry_field = tkinter.Entry(top, textvariable=entrymsg, bg=theme[0], fg='black', highlightthickness=0)
            entry_field.config(bg=theme[0], fg='black', highlightthickness=1)
            entry_field.focus_set()

            def send_current_text(key): send(entry_field.get())
            entry_field.bind('<Return>', send_current_text)

            entry_field.pack()
            send_button = tkinter.Button(top, text="Send", command=lambda: send(entry_field.get()))
            send_button.config(bg=theme[1], fg='black', highlightthickness=0, activebackground=theme[1])####
            send_button.pack()

            variable = tkinter.StringVar(top)
            variable.set(emojis[0])
            emoji_opt = tkinter.OptionMenu(top, variable, *emojis)
            emoji_opt.config(bg=theme[1], fg='black', highlightthickness=0, activebackground=theme[1])
            emoji_opt.pack(side=tkinter.LEFT)

            def send_emoji(): entrymsg.set(entrymsg.get() + variable.get()[0])

            emoji_button = tkinter.Button(top, text="➡️", command=send_emoji)
            emoji_button.config(bg=theme[1], fg='black', highlightthickness=0, activebackground=theme[1])
            emoji_button.pack(side=tkinter.LEFT)
            
            print("UI initialised")

            rcv_thread = threading.Thread(target=recive)
            rcv_thread.start()
            clock_thread = threading.Thread(target=clock)
            clock_thread.start()


            msg = ('u', username, password, user_colour) #Send username and colour
            message = pickle.dumps(msg)
            msg_length = len(message)
            send_length = str(msg_length).encode(FORMAT)
            send_length += b' ' * (HEADER - len(send_length))
            client.send(send_length)
            client.send(message)

            msg = ('h', '') #Get message history
            message = pickle.dumps(msg)
            msg_length = len(message)
            send_length = str(msg_length).encode(FORMAT)
            send_length += b' ' * (HEADER - len(send_length))
            client.send(send_length)
            client.send(message)
            print("Request history")

            return 0


on_start_thread = threading.Thread(target=on_start) 
on_start_thread.start()

tkinter.mainloop()
