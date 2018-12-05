import threading
import socket
import time
import player_pb2 as play
import tcp_packet_pb2 as tcp
import udp_packet_pb2 as udp
import tkinter as tk
# GUIIIIIII +++++++++++++++++++++++++++++++++++++++++++++
root = tk.Tk()
def prev(event):
  if drawFlag:
    global ix, iy
    x1, y1 = ( event.x - radius ), ( event.y - radius )
    x2, y2 = ( event.x + radius ), ( event.y + radius )
    canvas.create_oval( x1, y1, x2, y2, fill = color, outline="")
    ix, iy = event.x, event.y
    drawPacket = udp.UdpPacket.DrawPacket(
      type = udp.UdpPacket.DRAW,
      x = event.x,
      y = event.y,
      color = color,
      width = linewidth,
      start = True
    )
    udpSock.sendto(drawPacket.SerializeToString(), ('', 1234))

def draw(event):
  if drawFlag:
    global ix, iy
    x1, y1 = ( event.x - radius ), ( event.y - radius )
    x2, y2 = ( event.x + radius ), ( event.y + radius )
    canvas.create_oval( x1, y1, x2, y2, fill = color, outline="")
    canvas.create_line(ix, iy, event.x, event.y, fill = color, width = linewidth)
    ix, iy = event.x, event.y
    drawPacket = udp.UdpPacket.DrawPacket(
      type = udp.UdpPacket.DRAW,
      x = event.x,
      y = event.y,
      color = color,
      width = linewidth
    )
    udpSock.sendto(drawPacket.SerializeToString(), ('', 1234))

def erase(event):
  if drawFlag:
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
  if drawFlag:
    canvas.delete("all") #clear canvas
    drawPacket = udp.UdpPacket.DrawPacket(
      type = udp.UdpPacket.DRAW,
      clear = True
    )
    udpSock.sendto(drawPacket.SerializeToString(), ('', 1234))

root.geometry("1000x620") 
root.title("CHAT AREA")
canvas = tk.Canvas(root, state="disabled", bg="white", height=35, width=65)
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

labelID = tk.Label(root,text="",font=('Helvetica', '15'), fg="blue")
labelID.pack()

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
chatarea.pack()
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
############################################################

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

def receivePackets(sock, player):
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
        chatarea.insert(tk.END, 'You: ' + chatPacket.message + '\n') 
        chatarea.configure(state = 'disabled')
      else:
        chatarea.configure(state = 'normal')
        chatarea.insert(tk.END, chatPacket.player.name + ': ' + chatPacket.message + '\n') 
        chatarea.configure(state = 'disabled')
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

def currentPlayers(sock):
  playersInGame = getPlayerList(sock)
  players.configure(state = 'normal')
  players.delete(1.0, tk.END)
  for i in playersInGame:
    players.insert(tk.END, i.name + ' : 0 \n')
  players.configure(state = 'disabled')  

waitingForGameFlag = True
drawFlag = False
timer = 30
objectToDraw = None
winner = None
turn = None

def winnerListen(sock):
  global timer, winner, gametime
  udpPacket = udp.UdpPacket()
  while True:
    data, addr = sock.recvfrom(1024)
    udpPacket.ParseFromString(data)
    if udpPacket.type == udp.UdpPacket.WINNER:
      winnerPacket = udp.UdpPacket.WinnerPacket()
      winnerPacket.ParseFromString(data)
      winner = winnerPacket.player
      break
    elif udpPacket.type == udp.UdpPacket.TIME:
      timePacket = udp.UdpPacket.TimePacket()
      timePacket.ParseFromString(data)
      timer = timePacket.time
      gametime['text'] = timer
    elif udpPacket.type == udp.UdpPacket.TIMEOUT:
      break

def myTurnListener(sock, canvas):
  global objectToDraw, winner, timer, drawFlag
  winnerThread = threading.Thread(target=winnerListen, args=(sock,))
  winnerThread.start()
  while timer > 0 and not winner:
    time.sleep(0.25)
  if winner:
    chatarea.configure(state = 'normal')
    chatarea.insert(tk.END, winner.name + ' won! \n') 
    chatarea.configure(state = 'disabled')
  else:
    chatarea.configure(state = 'normal')
    chatarea.insert(tk.END, 'Nobody won. \n') 
    chatarea.configure(state = 'disabled')
  winnerThread.join()
  canvas.delete("all")
  objectToDraw = None
  winner = None
  timer = 30
  drawFlag = False

def userDraw(canvas, x, y, color, width, start, clear):
  if clear:
    canvas.delete("all") #clear canvas
  else:
    global ix, iy
    if start:
      ix = x
      iy = y
    x1, y1 = ( x - (width / 2) ), ( y - (width / 2) )
    x2, y2 = ( x + (width / 2) ), ( y + (width / 2) )
    canvas.create_oval( x1, y1, x2, y2, fill = color, outline="")
    if ix:
      canvas.create_line(ix, iy, x, y, fill = color, width = width)
    ix = x
    iy = y

def otherTurnListener(sock, canvas):
  global winner, timer, gametime
  udpPacket = udp.UdpPacket()
  while True:
    data, addr = sock.recvfrom(1024)
    udpPacket.ParseFromString(data)
    if udpPacket.type == udp.UdpPacket.TIME:
      timePacket = udp.UdpPacket.TimePacket()
      timePacket.ParseFromString(data)
      timer = timePacket.time
      gametime['text'] = timer
    elif udpPacket.type == udp.UdpPacket.DRAW:
      drawPacket = udp.UdpPacket.DrawPacket()
      drawPacket.ParseFromString(data)
      userDraw(canvas, drawPacket.x, drawPacket.y, drawPacket.color, drawPacket.width, drawPacket.start, drawPacket.clear) # for GUI
    elif udpPacket.type == udp.UdpPacket.WINNER:
      winnerPacket = udp.UdpPacket.WinnerPacket()
      winnerPacket.ParseFromString(data)
      winner = winnerPacket.player
      break
    elif udpPacket.type == udp.UdpPacket.TIMEOUT:
      break

def othersTurn(sock, canvas, player):
  global objectToDraw, timer, winner
  drawingPlayerThread = threading.Thread(target=otherTurnListener, args=(sock, canvas))
  drawingPlayerThread.start()
  while timer > 0 and not winner:
    time.sleep(0.25)
  if winner == player:
    chatarea.configure(state = 'normal')
    chatarea.insert(tk.END, 'You won! \n') 
    chatarea.configure(state = 'disabled')
  elif winner:
    chatarea.configure(state = 'normal')
    chatarea.insert(tk.END, winner.name + ' won! \n') 
    chatarea.configure(state = 'disabled')
  else:
    chatarea.configure(state = 'normal')
    chatarea.insert(tk.END, 'Nobody won. \n') 
    chatarea.configure(state = 'disabled')
  drawingPlayerThread.join()
  canvas.delete("all")
  ix = None
  iy = None
  objectToDraw = None
  winner = None
  timer = 30

def gameStart(sock, player, canvas):
  global objectToDraw, turn, ipAddressPort, turnPacket, drawFlag
  udpPacket = udp.UdpPacket()
  turnPacket = udp.UdpPacket.TurnPacket()

  while True:
    data, addr = sock.recvfrom(1024)
    udpPacket.ParseFromString(data)
    if udpPacket.type == udp.UdpPacket.TURN:
      canvas.delete("all")
      ix = None
      iy = None
      turnPacket.ParseFromString(data)
      printScores(turnPacket.scores)
      turn = turnPacket.player
      objectToDraw = turnPacket.object
      if turn == player:
        drawFlag = True
        turnLabel['text'] = "Your turn!"
        wordarea.configure(state="normal")
        wordarea.delete(1.0, tk.END)
        wordarea.insert(tk.END, "DRAW THIS: \n" + objectToDraw)
        wordarea.configure(state="disabled")
        time.sleep(3)
        myTurnListener(sock, canvas)
      else:
        turnLabel['text'] = turn.name + "'s turn!"
        wordarea.configure(state="normal")
        wordarea.delete(1.0, tk.END)
        wordarea.insert(tk.END, "GUESS THE DRAWING!")
        wordarea.configure(state="disabled")
        time.sleep(3)
        othersTurn(sock, canvas, player)
      turn = None
    elif udpPacket.type == udp.UdpPacket.DRAW:
      drawPacket = udp.UdpPacket.DrawPacket()
      drawPacket.ParseFromString(data)
      userDraw(canvas, drawPacket.x, drawPacket.y, drawPacket.color, drawPacket.width, drawPacket.start, drawPacket.clear)

def printScores(scores):
  players.configure(state = 'normal')
  players.delete(1.0, tk.END)
  for score in scores:
    players.insert(tk.END, str(score.name) + ' : ' + str(score.score) + '\n')
  players.configure(state = 'disabled')   


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("202.92.144.45", 80))

def getName():
  # Get player name
  global player, playerList, packetListener, udpSock, gameListener, lobbyId, portPacket
  player = play.Player(
    name = hname.get()
  )
  lobbyId = the_id.get()
  labelID['text'] = "LOBBY ID: " + lobbyId
  hostPage.withdraw()
  # Connect to lobby & get player id
  player = connectToLobby(sock, player, lobbyId)
  # Get player list
  playerList = getPlayerList(sock)
  # Listen for messages
  packetListener = threading.Thread(target=receivePackets, args=(sock, player))
  packetListener.start()
  # UDP Connection
  udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  portPacket = udp.UdpPacket.PortPacket(type=udp.UdpPacket.PORT)
  udpSock.sendto(portPacket.SerializeToString(), ('', 1234))

  gameListener = threading.Thread(target=gameStart, args=(udpSock, player, canvas))
  gameListener.start()
  root.deiconify()



hostPage = tk.Toplevel()
hostPage.title("WELCOME, CLIENT")
hostPage.geometry('300x100')
hostPage.attributes('-topmost', 'true')
w = tk.Label(hostPage, text="Lobby ID: ").grid(row=0)
the_id = tk.Entry(hostPage, width=20, fg="blue")
the_id.grid(row=0, column=1)
z = tk.Label(hostPage, text="Player name: ").grid(row=1)
hname = tk.Entry(hostPage, width=20, fg="blue")
hname.grid(row=1, column=1)
enter1 = tk.Button(hostPage,text='Enter game',command=getName).grid(row=3, column=1)
root.mainloop()