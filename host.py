import threading
import socket
import time
import random
import player_pb2 as play
import tcp_packet_pb2 as tcp
import udp_packet_pb2 as udp
import tkinter as tk
from PIL import ImageTk
import sys
SCORE_GOAL = 150
TIMER_LENGTH = 30
MAX_PLAYERS = 16

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
    broadcast(udpSock, drawPacket)

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
    broadcast(udpSock, drawPacket)

def howToPlay():
  howToPlaypage.deiconify()

def gameFlow():
  flowPage.deiconify()

def changePhoto():
  global img, panel
  img = tk.PhotoImage(file='images/2.gif')
  panel = tk.Label(howToPlaypage, image = img)
  panel.grid(row=0)


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
    broadcast(udpSock, drawPacket)

def on_close():
  howToPlaypage.withdraw()

def off_close():
  flowPage.withdraw()

def all_close():
  root.destroy()
  sys.exit(0)

def showGameWinner(player):
  root.withdraw()
  winnerIs['text'] = player + " WINS! GAME OVER!"
  winPage.deiconify()

global img
root.geometry("1100x620") 
root.title("CHAT AREA")
canvas = tk.Canvas(root, state="disabled", bg="white", height=35, width=80)
canvas.bind("<Button-1>", prev)
canvas.bind("<Button-3>", prev)
canvas.bind("<B1-Motion>", draw)
canvas.bind("<B3-Motion>", erase)

howToPlaypage = tk.Toplevel()
howToPlaypage.title("MANUAL")
howToPlaypage.geometry('1000x620')
howToPlaypage.attributes('-topmost', 'true')
img = tk.PhotoImage(file='images/manual.gif')
panel = tk.Label(howToPlaypage, image = img)
panel.grid(row=0)
howToPlaypage.withdraw()
howToPlaypage.protocol("WM_DELETE_WINDOW",  on_close)

flowPage = tk.Toplevel()
flowPage.title("HOW TO PLAY")
flowPage.geometry('1000x620')
flowPage.attributes('-topmost', 'true')
img2 = tk.PhotoImage(file='images/hgame.gif')
panel2 = tk.Label(flowPage, image = img2)
panel2.grid(row=0)
flowPage.withdraw()
flowPage.protocol("WM_DELETE_WINDOW",  off_close)

winPage = tk.Toplevel()
winPage.title("GAME OVER! ")
winPage.geometry('500x100')
winPage.attributes('-topmost', 'true')
winPage.configure(background="white")
winnerIs = tk.Label(winPage,text="",font=('Helvetica', '20'), fg="red", bg="white", padx=9, pady=15)
winnerIs.grid(row=3, column=1)
exit = tk.Button(winPage,text='EXIT',command=all_close).grid(row=5, column=3)
winPage.withdraw()
winPage.protocol("WM_DELETE_WINDOW",  all_close)



ix = None
iy = None
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
htp = tk.Button(root,text='Manual',command=howToPlay, bg="white") 
gFlow = tk.Button(root,text='Game Flow',command=gameFlow, bg="white") 
entry = tk.Entry(root,  bd=5, width=50)
chatarea = tk.Text(root, state='disabled', height=35, width=55, fg="blue")
button = tk.Button(root,text='submit',command=submit)
root.bind('<Return>', submit)
#TIMER

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
wordarea.insert(tk.END, "Draw my thing: \n")
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
htp.pack(side="right")
gFlow.pack(side="right")
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
    max_players = MAX_PLAYERS
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
    players.insert(tk.END, i.name + ' : 0 \n')
  players.configure(state = 'disabled') 

def receivePackets(sock, player):
  global objectToDraw, turn, winner, nextPort, scores, addrList
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
        chatarea.insert(tk.END, chatPacket.player.name + ' : ' + chatPacket.message + '\n') 
        chatarea.configure(state = 'disabled')
      if(chatPacket.message.lower() == objectToDraw.lower() and not (turn == chatPacket.player) and not winner):
        winner = chatPacket.player
    elif tcpPacket.type == tcp.TcpPacket.CONNECT:
      connectPacket.ParseFromString(data)
      playerList.append(connectPacket.player)
      chatarea.configure(state = 'normal')
      chatarea.insert(tk.END, connectPacket.player.name + ' joined the lobby! \n') 
      chatarea.configure(state = 'disabled')
      scores[connectPacket.player.id] = {'name': connectPacket.player.name, 'score': 0}
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



waitingForPlayersFlag = True
drawFlag = False
timer = TIMER_LENGTH
objectToDraw = None
winner = None
turn = None
stopListen = True
scores = {}

def countdown(sock):
  global timer, gametime, winner
  while timer > 0 and not winner:
    time.sleep(1)
    timer -= 1
    gametime['text'] = timer
    timePacket = udp.UdpPacket.TimePacket(type=udp.UdpPacket.TIME, time=timer)
    broadcast(sock, timePacket)
 


def joinListener(sock):
  global addrList
  udpPacket = udp.UdpPacket()
  portPacket = udp.UdpPacket.PortPacket()
  while timer > 0 and not winner:
    try:
      data, addr = sock.recvfrom(1024)
      if addr not in addrList:
        addrList.append(addr)
    except:
      pass

def joinFlagListener(sock):
  global addrList, stopListen
  udpPacket = udp.UdpPacket()
  portPacket = udp.UdpPacket.PortPacket()
  while not stopListen:
    try:
      data, addr = sock.recvfrom(1024)
      if addr not in addrList:
        addrList.append(addr)
    except:
      pass

def myTurnListener(sock, canvas):
  global objectToDraw, timer, winner, drawFlag
  timeThread = threading.Thread(target=countdown, args=(sock,))
  timeThread.start()
  joinThread = threading.Thread(target=joinListener, args=(sock,))
  joinThread.start()
  while timer > 0 and not winner:
    time.sleep(0.25)
  if winner:
    scores[winner.id]['score'] = scores[winner.id]['score'] + timer
    winnerPacket = udp.UdpPacket.WinnerPacket(type=udp.UdpPacket.WINNER, player=winner)
    broadcast(sock, winnerPacket)
    chatarea.configure(state = 'normal')
    chatarea.insert(tk.END, winner.name + ' won! \n') 
    chatarea.configure(state = 'disabled')
  else:
    timeoutPacket = udp.UdpPacket.TimeoutPacket(type=udp.UdpPacket.TIMEOUT)
    broadcast(sock, timeoutPacket)
    chatarea.configure(state = 'normal')
    chatarea.insert(tk.END, 'Nobody won. \n') 
    chatarea.configure(state = 'disabled')
  timeThread.join()
  joinThread.join()
  # declareWinner() # thread with timer for GUI (use `winner` variable)
  canvas.delete("all")
  objectToDraw = None
  winner = None
  timer = TIMER_LENGTH
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

def otherTurnDrawListener(sock, canvas):
   global addrList
   udpPacket = udp.UdpPacket()
   while timer > 0 and not winner:
    try:
       data, addr = sock.recvfrom(1024)
       udpPacket.ParseFromString(data)
       if udpPacket.type == udp.UdpPacket.DRAW:
          drawPacket = udp.UdpPacket.DrawPacket()
          drawPacket.ParseFromString(data)
          userDraw(canvas, drawPacket.x, drawPacket.y, drawPacket.color, drawPacket.width, drawPacket.start, drawPacket.clear) # for GUI
          broadcast(sock, drawPacket)
       elif udpPacket.type == udp.UdpPacket.PORT:
          if addr not in addrList:
            addrList.append(addr)
    except:
      pass

def broadcast(sock, packet):
  global addrList
  for addr in addrList:
    sock.sendto(packet.SerializeToString(), addr)

def othersTurn(sock, canvas, player):
  global timer, winner, objectToDraw
  timeThread = threading.Thread(target=countdown, args=(sock,))
  timeThread.start()
  otherTurnDrawListener(sock, canvas)
  while timer > 0 and not winner:
    time.sleep(0.25)
  if winner:
    scores[winner.id]['score'] = scores[winner.id]['score'] + timer
    winnerPacket = udp.UdpPacket.WinnerPacket(type=udp.UdpPacket.WINNER, player=winner)
    broadcast(sock, winnerPacket)
    if winner == player:
      chatarea.configure(state = 'normal')
      chatarea.insert(tk.END, 'You won! \n') 
      chatarea.configure(state = 'disabled')
    else:
      chatarea.configure(state = 'normal')
      chatarea.insert(tk.END, winner.name + ' won! \n') 
      chatarea.configure(state = 'disabled')
  else:
    timeoutPacket = udp.UdpPacket.TimeoutPacket(type=udp.UdpPacket.TIMEOUT)
    broadcast(sock, timeoutPacket)
    chatarea.configure(state = 'normal')
    chatarea.insert(tk.END, 'Nobody won. \n') 
    chatarea.configure(state = 'disabled')
  timeThread.join()
  # drawingPlayerThread.join()
  # declareWinner() # thread with timer for GUI
  canvas.delete("all")
  ix = None
  iy = None
  winner = None
  objectToDraw = None
  timer = TIMER_LENGTH

def addScores(turnPacket):
  global scores
  for playerId in scores:
    score = turnPacket.scores.add()
    score.name = scores[playerId]['name']
    score.score = scores[playerId]['score']
  return turnPacket

def printScores():
  global scores
  players.configure(state = 'normal')
  players.delete(1.0, tk.END)
  for score in scores.values():
    players.insert(tk.END, str(score['name']) + ' : ' + str(score['score']) + '\n')
  players.configure(state = 'disabled')   

def getWinner():
  global scores
  for score in scores.values():
    if score['score'] >= SCORE_GOAL:
      return score['name']
  return None

objects = ['Chicken', 'Pig', 'Cow', 'Horse', 'Goat', 'Carabao', 'Butterfly', 'Rock', 'Forest', 'Dog', 'Banana', 'Flower', 'Laptop', 'Chair', 'Table']

def gameStart(sock, player, canvas):
  global waitingForPlayersFlag, turn, objectToDraw, ipAddressPort, stopListen, turnPacket, drawFlag
  scores[player.id] = {'name': player.name, 'score': 0}
  chatarea.configure(state = 'normal')
  chatarea.insert(tk.END, 'Waiting for other players to join.. \n') 
  chatarea.configure(state = 'disabled')
  while len(playerList) == 1:  # no other players
    time.sleep(1)
  waitingForPlayersFlag = not waitingForPlayersFlag

  while True:
    try:
      data, addr = sock.recvfrom(1024)
      addrList.append(addr)
      break
    except: pass

  chatarea.configure(state = 'normal')
  chatarea.insert(tk.END, 'GAME STARTED! \n') 
  chatarea.configure(state = 'disabled')
  
  turnNo = 0
  while True:
    stopListen = False
    joinThread = threading.Thread(target=joinFlagListener, args=(sock,))
    joinThread.start()
    time.sleep(1)
    stopListen = True
    joinThread.join()
    turn = playerList[turnNo]
    # send TURN packet
    objectToDraw = random.choice(objects)
    turnPacket = udp.UdpPacket.TurnPacket(type=udp.UdpPacket.TURN, player=turn, object=objectToDraw)
    turnPacket = addScores(turnPacket)
    broadcast(sock, turnPacket)
    printScores()

    if turn == player:
      drawFlag = True
      turnLabel['text'] = "Your turn!"
      wordarea.configure(state="normal")
      wordarea.delete(1.0, tk.END)
      wordarea.insert(tk.END, "DRAW THIS: \n" + objectToDraw)
      wordarea.configure(state="disabled")
      stopListen = False
      joinThread = threading.Thread(target=joinFlagListener, args=(sock,))
      joinThread.start()
      time.sleep(3)
      stopListen = True
      joinThread.join()
      myTurnListener(sock, canvas)
    else:
      turnLabel['text'] = turn.name + "'s turn!"
      wordarea.configure(state="normal")
      wordarea.delete(1.0, tk.END)
      wordarea.insert(tk.END, "GUESS THE DRAWING!")
      wordarea.configure(state="disabled")
      stopListen = False
      joinThread = threading.Thread(target=joinFlagListener, args=(sock,))
      joinThread.start()
      time.sleep(3)
      stopListen = True
      joinThread.join()
      othersTurn(sock, canvas, player)

    winner = getWinner()
    if winner:
      endgamePacket = udp.UdpPacket.EndgamePacket(type=udp.UdpPacket.ENDGAME, winner=winner)
      broadcast(sock, endgamePacket)
      showGameWinner(winner) # TODO for GUI (show winner + exit button); passes player name (string); close all windows then exit()

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
  global player, playerList, packetListener, udpSock, gameListener, addrList
  player = play.Player(
    name = hname.get()
  )
  hostPage.withdraw()
  # Connect to lobby & get player id
  player = connectToLobby(sock, player, lobbyId)
  # Get player list
  playerList = getPlayerList(sock)
  addrList = []
  nextPort = 1235
  # Listen for messages
  packetListener = threading.Thread(target=receivePackets, args=(sock, player), daemon=True)
  packetListener.start()
  # UDP Connection
  udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udpSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  udpSock.bind(('', 1234))
  udpSock.settimeout(0.1)
  gameListener = threading.Thread(target=gameStart, args=(udpSock, player, canvas), daemon=True)
  gameListener.start()
  root.deiconify()

labelID['text'] = "LOBBY ID: " + lobbyId
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