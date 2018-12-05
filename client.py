import threading
import socket
import time
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
  message = input()
  while message != 'exit\n':
    packet = tcp.TcpPacket.ChatPacket(
      type = tcp.TcpPacket.CHAT,
      lobby_id = lobbyId,
      player = player,
      message = message
    )
    sock.send(packet.SerializeToString())
    message = input()
    print('\x1b[1A\x1b[2K', end='\r')

waitingForGameFlag = True
drawFlag = False
timer = 30
objectToDraw = None
winner = None;
turn = None;

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
  sock.send(drawPacket.SerializeToString())

def winnerListen(sock):
  global timer, winner
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
      print('TIME LEFT:', timer)
    elif udpPacket.type == udp.UdpPacket.TIMEOUT:
      break

def myTurnListener(sock, canvas):
  global objectToDraw, winner, timer
  # call draw() for every point drawn:
  winnerThread = threading.Thread(target=winnerListen, args=(sock,))
  winnerThread.start()
  while timer > 0 and not winner:
    time.sleep(0.25)
  if winner:
    print(winner.name, 'won.')
  else:
    print('Nobody won.')
  winnerThread.join()
  # declareWinner() # thread with timer for GUI (use `winner` variable)
  # clearCanvas() # for GUI
  objectToDraw = None
  winner = None
  timer = 30

def otherTurnListener(sock, canvas):
  global winner, timer
  udpPacket = udp.UdpPacket()
  while True:
    data, addr = sock.recvfrom(1024)
    udpPacket.ParseFromString(data)
    if udpPacket.type == udp.UdpPacket.TIME:
      timePacket = udp.UdpPacket.TimePacket()
      timePacket.ParseFromString(data)
      timer = timePacket.time
      print('TIME LEFT:', timer)
    # if udpPacket.type == udp.UdpPacket.DRAW:
    #   drawPacket = udp.UdpPacket.DrawPacket()
    #   drawPacket.ParseFromString(data)
    #   canvas.draw(drawPacket.x, drawPacket.y, drawPacket.color) # for GUI
    elif udpPacket.type == udp.UdpPacket.WINNER:
      winnerPacket = udp.UdpPacket.WinnerPacket()
      winnerPacket.ParseFromString(data)
      winner = winnerPacket.player
      break
    elif udpPacket.type == udp.UdpPacket.TIMEOUT:
      break

def othersTurn(sock, canvas, player):
  global objectToDraw, timer, winner
  # disableCanvas() # (disable drawing for player) for GUI
  drawingPlayerThread = threading.Thread(target=otherTurnListener, args=(sock, canvas))
  drawingPlayerThread.start()
  while timer > 0 and not winner:
    time.sleep(0.25)
  if winner == player:
    print('You won.')
  elif winner:
    print(winner.name, 'won.')
  else:
    print('Nobody won.')
  drawingPlayerThread.join()
  # declareWinner() # thread with timer for GUI
  # clearCanvas() # for GUI
  objectToDraw = None
  winner = None
  timer = 30

def printScores(scores):
  print("\nScores:")
  for score in scores:
    print(score.name, '-', score.score)

def gameStart(sock, player, canvas):
  global objectToDraw, turn, ipAddressPort
  udpPacket = udp.UdpPacket()
  turnPacket = udp.UdpPacket.TurnPacket()
  while True:
    data, addr = sock.recvfrom(1024)

    udpPacket.ParseFromString(data)
    if udpPacket.type == udp.UdpPacket.TURN:
      turnPacket.ParseFromString(data)
      turn = turnPacket.player
      objectToDraw = turnPacket.object
      printScores(turnPacket.scores)
      if turn == player:
        print('\nYour turn.')
        print('Object to Draw:', objectToDraw)
        time.sleep(3)
        myTurnListener(sock, canvas)
      else:
        print('\n' + turn.name + '\'s turn.')
        time.sleep(3)
        othersTurn(sock, canvas, player)
      turn = None

# Connect to server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("202.92.144.45", 80))

# Get player name
player = play.Player(
  name = input('\nPlayer Name: ')
)

lobbyId = input('Lobby ID: ')

# Connect to lobby & get player id
player = connectToLobby(sock, player, lobbyId)

# Get player list
playerList = getPlayerList(sock)

# Listen for messages
packetListener = threading.Thread(target=receivePackets, args=(sock, player))
packetListener.start()

# Chat
chat = threading.Thread(target=chatter, args=(sock, lobbyId, player))
chat.start()

# UDP Connection
udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
portPacket = udp.UdpPacket.PortPacket(type=udp.UdpPacket.PORT)
udpSock.sendto(portPacket.SerializeToString(), ('', 1234))

# Connect to game
canvas = ''; # fake
gameListener = threading.Thread(target=gameStart, args=(udpSock, player, canvas))
gameListener.start()