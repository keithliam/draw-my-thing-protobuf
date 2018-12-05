import threading
import socket
import time
import random
import player_pb2 as play
import tcp_packet_pb2 as tcp
import udp_packet_pb2 as udp
import tkinter as tk

# GUIIIIIIIIIIIIIIIII

root = tk.Tk()

def prev(event):
  global ix, iy
  ix, iy = event.x, event.y
  print("START:",event.x,event.y)

def draw(event):
  global ix, iy
  x1, y1 = ( event.x - radius ), ( event.y - radius )
  x2, y2 = ( event.x + radius ), ( event.y + radius )

  print("PT1:",ix,iy," PT2:",event.x,event.y)
  canvas.create_oval( x1, y1, x2, y2, fill = color, outline="")
  canvas.create_line(ix, iy, event.x, event.y, fill = color, width = linewidth)
  ix, iy = event.x, event.y


def erase(event):
  global ix, iy
  x1, y1 = ( event.x - 6 ), ( event.y - 6 )
  x2, y2 = ( event.x + 6 ), ( event.y + 6 )
  canvas.create_oval( x1, y1, x2, y2, fill = "white", outline = "white")
  canvas.create_line(ix, iy, event.x, event.y, fill = "white", width = 12)
  ix, iy = event.x, event.y

def submit(event=None):
    message = entry.get()   
    packet = tcp.TcpPacket.ChatPacket(
      type = tcp.TcpPacket.CHAT,
      lobby_id = lobbyId,
      player = player,
      message = message
    )
    sock.send(packet.SerializeToString())
    entry.delete(0, tk.END)

def yellow():
  global color
  color = "yellow"
def blue():
  global color
  color = "blue"
def red():
  global color
  color = "red"
def black():
  global color
  color = "black"
def line1():
  global radius, linewidth
  radius = 3
  linewidth = 6
def line2():
  global radius, linewidth
  radius = 6
  linewidth = 12
def line3():
  global radius, linewidth
  radius = 12
  linewidth = 24

def clear(event=None):
  canvas.delete("all") #clear canvas



root.geometry("1000x600") 
root.title("CHAT AREA")
canvas = tk.Canvas(root, bg="white", height=35, width=65)
canvas.bind("<Button-1>", prev)
canvas.bind("<Button-3>", prev)
canvas.bind("<B1-Motion>", draw)
canvas.bind("<B3-Motion>", erase)
ix = 0
iy = 0
color = "black"
yellow = tk.Button(root, bg="yellow", command=yellow)
blue = tk.Button(root, bg="blue", command=blue)
red = tk.Button(root, bg="red", command=red)
black = tk.Button(root, bg="black", command=black)
#Line thickness
sml = tk.Button(root, text="1", command=line1)
med = tk.Button(root, text="2", command=line2)
lrg = tk.Button(root, text="3", command=line3)
#default thickness
radius = 3
linewidth = 6
#delete canvas button
trash = tk.Button(root,text='clear',command=clear) 
entry = tk.Entry(root,  bd=5, width=60)
chatarea = tk.Text(root, state='disabled', height=35, width=65, fg="blue")
button = tk.Button(root,text='submit',command=submit)
root.bind('<Return>', submit)
#TIMER



#PlayerList
playerframe = tk.Frame(root)
playerframe.pack(side="left")
gametime = tk.Label(playerframe,text="TIMER",font=('Helvetica', '20'))
gametime.pack()
turnLabel = tk.Label(playerframe,text="TURN", fg="red", font=('Helvetica', '15'))
turnLabel.pack()
wordarea = tk.Text(playerframe, state='normal', height=4, width=15, fg="red", font=('Helvetica, 10'))
wordarea.insert(tk.END, "DRAW THIS: \n")
wordarea.configure(state = "disabled")
wordarea.pack()
playerLabel = tk.Label(playerframe,text="PLAYERS:")
players = tk.Text(playerframe, state='disabled', height=35, width=20, fg="black")
playerLabel.pack()
players.pack(side="left")



canvas.pack(side="left", expand = "YES", fill = "both")
chatarea.pack();
entry.pack()
button.pack()
yellow.pack(side="left")
blue.pack(side="left")
red.pack(side="left")
black.pack(side="left")
sml.pack(side="left")
med.pack(side="left")
lrg.pack(side="left")
trash.pack(side="left")
root.withdraw()
################################################################

def errCheck(data):
  tcpPacket = tcp.TcpPacket()
  tcpPacket.ParseFromString(data)
  if tcpPacket.type == tcp.TcpPacket.ERR_LDNE:
    errLdnePacket = tcp.TcpPacket.ErrLdnePacket()
    errLdnePacket.ParseFromString(data)
    print('Error:', errLdnePacket.err_message)
    exit()
  elif tcpPacket.type == tcp.TcpPacket.ERR_LFULL:
    errLfullPacket = tcp.TcpPacket.ErrLfullPacket()
    errLfullPacket.ParseFromString(data)
    print('Error:', errLfullPacket.err_message)
    exit()
  elif tcpPacket.type == tcp.TcpPacket.ERR:
    errPacket = tcp.TcpPacket.ErrPacket()
    errPacket.ParseFromString(data)
    print('Error:', errPacket.err_message)
    exit()

def createLobby(sock):
  packet = tcp.TcpPacket.CreateLobbyPacket(
    type = tcp.TcpPacket.CREATE_LOBBY,
    max_players = 10
  )
  sock.send(packet.SerializeToString())
  data = sock.recv(1024)
  errCheck(data)
  packet.ParseFromString(data)
  lobby_id = packet.lobby_id
  print('Successfully created lobby ' + lobby_id + '.')
  return lobby_id

def connectToLobby(sock, player, lobbyId):
  packet = tcp.TcpPacket.ConnectPacket(
    type = tcp.TcpPacket.CONNECT,
    player = player,
    lobby_id = lobbyId
  )
  sock.send(packet.SerializeToString())
  data = sock.recv(1024)
  errCheck(data)
  packet.ParseFromString(data)
  print('Successfully connected to lobby ' + lobbyId + '.')
  currentPlayers(sock)
  return packet.player

def getPlayerList(sock):
  packet = tcp.TcpPacket.PlayerListPacket(
    type = tcp.TcpPacket.PLAYER_LIST
  )
  sock.send(packet.SerializeToString())
  data = sock.recv(1024)
  errCheck(data)
  packet.ParseFromString(data)
  return list(packet.player_list)

def currentPlayers(sock):
  playersInGame = getPlayerList(sock)
  players.configure(state = 'normal')
  players.delete(1.0, tk.END)
  for i in playersInGame:
    players.insert(tk.END, i.name + ' : <SCORE>\n')
  players.configure(state = 'disabled') 

def receivePackets(sock, player):
  global objectToDraw, turn, winner
  tcpPacket = tcp.TcpPacket()
  chatPacket = tcp.TcpPacket.ChatPacket()
  connectPacket = tcp.TcpPacket.ConnectPacket()
  disconnectPacket = tcp.TcpPacket.DisconnectPacket()
  while True:
    data = sock.recv(1024)
    errCheck(data)
    tcpPacket.ParseFromString(data)
    if tcpPacket.type == tcp.TcpPacket.CHAT:
      chatPacket.ParseFromString(data)
      if chatPacket.player == player:
        chatarea.configure(state = 'normal')
        chatarea.insert(tk.END, 'You : ' + chatPacket.message + '\n') 
        chatarea.configure(state = 'disabled')
      else:
        chatarea.configure(state = 'normal')
        chatarea.insert(tk.END, chatPacket.player.name + ' : ' + chatPacket.message + '\n') 
        chatarea.configure(state = 'disabled')
      if(chatPacket.message == objectToDraw and not (turn == chatPacket.player) and not winner):
        winner = chatPacket.player
    elif tcpPacket.type == tcp.TcpPacket.CONNECT:
      connectPacket.ParseFromString(data)
      playerList.append(connectPacket.player)
      chatarea.configure(state = 'normal')
      chatarea.insert(tk.END, connectPacket.player.name + ' joined the lobby! \n') 
      chatarea.configure(state = 'disabled')
      currentPlayers(sock)
    elif tcpPacket.type == tcp.TcpPacket.DISCONNECT:
      disconnectPacket.ParseFromString(data)
      playerList.remove(disconnectPacket.player)
      if disconnectPacket.update == tcp.TcpPacket.DisconnectPacket.NORMAL:
        chatarea.configure(state = 'normal')
        chatarea.insert(tk.END, disconnectPacket.player.name + ' disconnected from the lobby! \n') 
        chatarea.configure(state = 'disabled')
        currentPlayers(sock)
      else:
        chatarea.configure(state = 'normal')
        chatarea.insert(tk.END, disconnectPacket.player.name + ' lost connection to the lobby! \n') 
        chatarea.configure(state = 'disabled')
        currentPlayers(sock)



waitingForPlayersFlag = True;
drawFlag = False
timer = 30
objectToDraw = None
winner = None
turn = None

def countdown(sock):
  global timer
  while timer > 0 and not winner:
    time.sleep(1)
    timer -= 1
    gametime['text'] = timer;
    timePacket = udp.UdpPacket.TimePacket(type=udp.UdpPacket.TIME, time=timer)
    sock.sendto(timePacket.SerializeToString(), ('', 1235))
 

def draw(sock, canvas):
  xCoor = 0;  # fake
  yCoor = 0;  # fake
  color = 'black'
  drawPacket = udp.UdpPacket.DrawPacket(
    type = udp.UdpPacket.DRAW,
    x = xCoor,
    y = yCoor,
    color = color
  )
  sock.sendto(drawPacket.SerializeToString(), ('', 1235))

def myTurnListener(sock, canvas):
  global objectToDraw, timer, winner
  timeThread = threading.Thread(target=countdown, args=(sock,))
  timeThread.start()
  # call draw() for every point drawn:
  while timer > 0 and not winner:
    time.sleep(0.25)
  if winner:
    winnerPacket = udp.UdpPacket.WinnerPacket(type=udp.UdpPacket.WINNER, player=winner)
    sock.sendto(winnerPacket.SerializeToString(), ('', 1235))
    print(winner.name, 'won.')
  else:
    timeoutPacket = udp.UdpPacket.TimeoutPacket(type=udp.UdpPacket.TIMEOUT)
    sock.sendto(timeoutPacket.SerializeToString(), ('', 1235))
    print('Nobody won.')
  timeThread.join()
  # declareWinner() # thread with timer for GUI (use `winner` variable)
  # clearCanvas() # for GUI
  objectToDraw = None
  winner = None
  timer = 30

# def otherTurnDrawListener(sock, canvas):
#   udpPacket = udp.UdpPacket()
#   while True:
#     data, addr = sock.recvfrom(1024)
#     udpPacket.ParseFromString(data)
#     if winner:
#       break
    # if udpPacket.type == udp.UdpPacket.DRAW:
    #   drawPacket = udp.UdpPacket.DrawPacket()
    #   drawPacket.ParseFromString(data)
    #   canvas.draw(drawPacket.x, drawPacket.y, drawPacket.color) # for GUI

def othersTurn(sock, canvas, player):
  global timer, winner, objectToDraw
  # disableCanvas() # (disable drawing for player) for GUI
  timeThread = threading.Thread(target=countdown, args=(sock,))
  timeThread.start()
  # drawingPlayerThread = threading.Thread(target=otherTurnDrawListener, args=(sock, canvas))
  # drawingPlayerThread.start()
  while timer > 0 and not winner:
    time.sleep(0.25)
  if winner:
    winnerPacket = udp.UdpPacket.WinnerPacket(type=udp.UdpPacket.WINNER, player=winner)
    sock.sendto(winnerPacket.SerializeToString(), ('', 1235))
    if winner == player:
      print('You won.')
    else:
      print(winner.name, 'won.')
  else:
    timeoutPacket = udp.UdpPacket.TimeoutPacket(type=udp.UdpPacket.TIMEOUT)
    sock.sendto(timeoutPacket.SerializeToString(), ('', 1235))
    print('Nobody won.')
  timeThread.join()
  # drawingPlayerThread.join()
  # declareWinner() # thread with timer for GUI
  # clearCanvas() # for GUI
  winner = None
  objectToDraw = None
  timer = 30

objects = ['Chicken', 'Pig', 'Cow', 'Horse', 'Goat', 'Carabao']

def gameStart(sock, player, canvas):
  global waitingForPlayersFlag, turn, objectToDraw, ipAddressPort

  print('Waiting for other players...')
  while len(playerList) == 1:  # no other players
    time.sleep(1)
  waitingForPlayersFlag = not waitingForPlayersFlag;
  print('Game started.')
  
  turnNo = 0
  while True:
    time.sleep(1)
    turn = playerList[turnNo]

    # send TURN packet
    objectToDraw = random.choice(objects)
    turnPacket = udp.UdpPacket.TurnPacket(type=udp.UdpPacket.TURN, player=turn, object=objectToDraw)
    sock.sendto(turnPacket.SerializeToString(), ('', 1235))

    if turn == player:
      turn['text'] = "Your turn!"
      wordarea
      print('Object to Draw:', objectToDraw)
      time.sleep(3)
      myTurnListener(sock, canvas)
    else:
      print('\n' + turn.name + '\'s turn.')
      time.sleep(3)
      othersTurn(sock, canvas, player)

    turnNo += 1
    if turnNo == len(playerList):
      turnNo = 0



# Connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("202.92.144.45", 80))

# Create lobby
lobbyId = createLobby(sock)
def getName():
  # Get player name
  global player, playerList, packetListener, udpSock, gameListener
  player = play.Player(
    name = hname.get()
  )
  hostPage.withdraw()
  # Connect to lobby & get player id
  player = connectToLobby(sock, player, lobbyId)
  # Get player list
  playerList = getPlayerList(sock)
  # Listen for messages
  packetListener = threading.Thread(target=receivePackets, args=(sock, player))
  packetListener.start()
  # UDP Connection
  udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udpSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  udpSock.bind(('', 1234))
  gameListener = threading.Thread(target=gameStart, args=(udpSock, player, canvas))
  gameListener.start()
  root.deiconify()

hostPage = tk.Toplevel()
hostPage.title("WELCOME, HOST")
hostPage.geometry('300x100')
hostPage.attributes('-topmost', 'true')
w = tk.Label(hostPage, text="Lobby ID: ").grid(row=0)
the_id = tk.Text(hostPage, height=1, width=20, fg="blue")
the_id.insert(tk.END, lobbyId)
the_id.grid(row=0, column=1)
z = tk.Label(hostPage, text="Player name: ").grid(row=1)
hname = tk.Entry(hostPage, width=20, fg="blue")
hname.grid(row=1, column=1)
enter1 = tk.Button(hostPage,text='Enter game',command=getName).grid(row=3, column=1)



root.mainloop()