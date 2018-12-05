import threading
import socket
import time
import random
import player_pb2 as play
import tcp_packet_pb2 as tcp
import udp_packet_pb2 as udp

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
  global objectToDraw, turn, winner, addrList, nextPort
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
        print('You:', chatPacket.message)
      else:
        print(chatPacket.player.name + ': ' + chatPacket.message)
      if(chatPacket.message == objectToDraw and not (turn == chatPacket.player) and not winner):
        winner = chatPacket.player
    elif tcpPacket.type == tcp.TcpPacket.CONNECT:
      connectPacket.ParseFromString(data)
      playerList.append(connectPacket.player)
      print('\n' + connectPacket.player.name + ' joined the lobby.')
    elif tcpPacket.type == tcp.TcpPacket.DISCONNECT:
      disconnectPacket.ParseFromString(data)
      playerList.remove(disconnectPacket.player)
      if disconnectPacket.update == tcp.TcpPacket.DisconnectPacket.NORMAL:
        print('\n' + disconnectPacket.player.name + ' disconnected from the lobby.')
      else:
        print('\n' + disconnectPacket.player.name + ' lost connection to the lobby.')

def chatter(sock, lobbyId, player):
  global objectToDraw, turn, winner
  message = input()
  while message != 'exit':
    if message != '':
      packet = tcp.TcpPacket.ChatPacket(
        type = tcp.TcpPacket.CHAT,
        lobby_id = lobbyId,
        player = player,
        message = message
      )
      sock.send(packet.SerializeToString())
    message = input()
    if(message == objectToDraw and not (turn == player) and not winner):
      winner = player
    print('\x1b[1A\x1b[2K', end='\r')

waitingForPlayersFlag = True;
drawFlag = False
timer = 30
objectToDraw = None
winner = None
turn = None
stopListen = True

def broadcast(sock, packet):
  global addrList
  for addr in addrList:
    sock.sendto(packet.SerializeToString(), addr)

def countdown(sock):
  global timer
  while timer > 0 and not winner:
    time.sleep(1)
    timer -= 1
    print('TIME LEFT:', timer)
    timePacket = udp.UdpPacket.TimePacket(type=udp.UdpPacket.TIME, time=timer)
    broadcast(sock, timePacket)


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
  broadcast(sock, drawPacket)

def joinListener(sock):
  global addrList
  udpPacket = udp.UdpPacket()
  portPacket = udp.UdpPacket.PortPacket()
  while timer > 0 and not winner:
    try:
      data, addr = sock.recvfrom(1024)
      print(addr)
      if addr not in addrList:
        addrList.append(addr)
    except:
      pass

def joinFlagListener(sock):
  global addrList
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
  global objectToDraw, timer, winner
  timeThread = threading.Thread(target=countdown, args=(sock,))
  timeThread.start()
  joinThread = threading.Thread(target=joinListener, args=(sock,))
  joinThread.start()
  # call draw() for every point drawn:
  while timer > 0 and not winner:
    time.sleep(0.25)
  if winner:
    winnerPacket = udp.UdpPacket.WinnerPacket(type=udp.UdpPacket.WINNER, player=winner)
    broadcast(sock, winnerPacket)
    print(winner.name, 'won.')
  else:
    timeoutPacket = udp.UdpPacket.TimeoutPacket(type=udp.UdpPacket.TIMEOUT)
    broadcast(sock, timeoutPacket)
    print('Nobody won.')
  timeThread.join()
  joinThread.join()
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
  joinThread = threading.Thread(target=joinListener, args=(sock,))
  joinThread.start()
  while timer > 0 and not winner:
    time.sleep(0.25)
  if winner:
    winnerPacket = udp.UdpPacket.WinnerPacket(type=udp.UdpPacket.WINNER, player=winner)
    broadcast(sock, winnerPacket)
    if winner == player:
      print('You won.')
    else:
      print(winner.name, 'won.')
  else:
    timeoutPacket = udp.UdpPacket.TimeoutPacket(type=udp.UdpPacket.TIMEOUT)
    broadcast(sock, timeoutPacket)
    print('Nobody won.')
  timeThread.join()
  joinThread.join()
  # drawingPlayerThread.join()
  # declareWinner() # thread with timer for GUI
  # clearCanvas() # for GUI
  winner = None
  objectToDraw = None
  timer = 30

objects = ['Chicken', 'Pig', 'Cow', 'Horse', 'Goat', 'Carabao']

def gameStart(sock, player, canvas):
  global waitingForPlayersFlag, turn, objectToDraw, ipAddressPort, stopListen

  print('Waiting for other players...')
  while len(playerList) == 1:  # no other players
    time.sleep(1)
  waitingForPlayersFlag = not waitingForPlayersFlag;

  while True:
    try:
      data, addr = sock.recvfrom(1024)
      addrList.append(addr)
      print(addr)
      break
    except: pass

  print('Game started.')
  
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
    broadcast(sock, turnPacket)

    if turn == player:
      print('\nYour turn.')
      print('Object to Draw:', objectToDraw)
      stopListen = False
      joinThread = threading.Thread(target=joinFlagListener, args=(sock,))
      joinThread.start()
      time.sleep(3)
      stopListen = True
      joinThread.join()
      myTurnListener(sock, canvas)
    else:
      print('\n' + turn.name + '\'s turn.')
      stopListen = False
      joinThread = threading.Thread(target=joinFlagListener, args=(sock,))
      joinThread.start()
      time.sleep(3)
      stopListen = True
      joinThread.join()
      othersTurn(sock, canvas, player)

    turnNo += 1
    if turnNo == len(playerList):
      turnNo = 0





# Connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("202.92.144.45", 80))

# Create lobby
lobbyId = createLobby(sock)

# Get player name
player = play.Player(
  name = input('\nPlayer Name: ')
)

# Connect to lobby & get player id
player = connectToLobby(sock, player, lobbyId)

# Get player list
playerList = getPlayerList(sock)
addrList = []
nextPort = 1235

# Listen for messages
packetListener = threading.Thread(target=receivePackets, args=(sock, player))
packetListener.start()

# Chat
chat = threading.Thread(target=chatter, args=(sock, lobbyId, player))
chat.start()

# UDP Connection
udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
udpSock.bind(('', 1234))
udpSock.settimeout(0.1)

# Connect to game
canvas = '' #fake
gameListener = threading.Thread(target=gameStart, args=(udpSock, player, canvas))
gameListener.start()