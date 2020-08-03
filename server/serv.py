import socket
import os.path
import sys
import subprocess
import commands

# Command line checks
if len(sys.argv) != 2:
	print ('ERROR:To Run: python3 ' + sys.argv[0] + ' <Port Number> ')

listenPort = sys.argv[1]

# Check for valid port
while True:
    try:
        if (listenPort.isdigit() == False):
            raise TypeError('You cannot have letters in your port number')
    except TypeError as typeerror:
        print('PORT NUMBER format {} is incorrect. Try again'.format(listenPort), typeerror)
        sys.exit()
    else:
        listenPort = int(listenPort)
        print('PORT NUMBER format is correct: OK to proceed')
        break

# Create a welcome socket.
print("Creating Welcome socket...")
welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
welcomeSock.bind(('', listenPort))

# Listen for a connection
welcomeSock.listen(1)
print ('Waiting for connections...')

# Accept connections
clientSock, addr = welcomeSock.accept()
print 'Accepted connection from client:', addr

def sendData(socket, data):
    dataSize = str(len(data))
    
    #set header to 10 bytes
    while len(dataSize) < 10:
        dataSize = "0" + dataSize

    data = dataSize + data
    dataSent = 0

    #ensure all data is sent
    while dataSent != len(data):
        dataSent += socket.send(data[dataSent:])

# ************************************************
# Receives the specified number of bytes
# from the specified socket
# @param socket - the socket from which to receive
# @param numBytes - the number of bytes to receive
# @return - the bytes received
# *************************************************
def recvAll(socket, numBytes):
    # The buffer
    recvBuffer = ""
    
    # The temporary buffer
    tempBuffer = ""
    
    # Keep receiving till all is received
    while len(recvBuffer) < numBytes:
        
        # Attempt to receive bytes
        tempBuffer = socket.recv(numBytes)
        
        # The other side has closed the socket
        if not tempBuffer:
            break
       
        # Add the received bytes to the buffer
        recvBuffer += tempBuffer

    return recvBuffer

def recvHeader(socket):
    data = ""
    fileSize = 0
    fileSizeBuffer = ""
    # Receive the first 10 bytes indicating the size of the file
    fileSizeBuffer = recvAll(socket, 10)
    try:
        # Get the file size
        fileSize = int(fileSizeBuffer)
        # receive a file given a file size
        data = recvAll(socket, fileSize)
    except:
        pass
    return data

def connection():
    tempSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # open an ephemeral port to send data
    tempSocket.bind(('', 0))
    socket_number = str(tempSocket.getsockname()[1])
    sendData(clientSock,  socket_number)
    tempSocket.listen(1)
    newSocket, addr = tempSocket.accept()
    return newSocket

while True:
    command = recvHeader(clientSock)
    if command == "ls":
        # myCmd = 'ls -hS'
        temp = ''
        dataSocket = connection()
        # os.system(myCmd)
        for line in commands.getoutput('ls -hS'):
            temp += line
        sendData(dataSocket, temp)
        print('ls command SUCCESS')
        dataSocket.close()
        
     # exit command
    if command == "exit":
        print('exit command SUCCESS')
        break

    if command == "get":
        dataSocket = connection()
        filename = recvHeader(dataSocket)
        if os.path.exists(filename):
            file = open(filename, "r")
            #send file byte
            byte = file.read(1)
            bytesCount = 0
            while byte != "":
                sendData(dataSocket, byte)
                byte = file.read(1)
                bytesCount += 1
            print("get command SUCCESS")
            print("SUCCESS: {} Uploaded to Client. The file size is {} bytes".format(
                filename, bytesCount))
            file.close()
        else:
            print("ERROR: Trying to transfer file that does not exist")
        dataSocket.close()

    # put command
    if command == "put":
        dataSocket = connection()
        filename = recvHeader(dataSocket)
        print("put command SUCCESS")
        try:
            if os.path.exists(filename):
                i = 1
                num = "(" + str(i) + ")"
                f_name, f_extension = os.path.splitext(filename)
                temp = f_name
                filename = temp + num + f_extension
                while os.path.exists(filename):
                    i += 1
                    num = "(" + str(i) + ")"
                    filename = temp + num + f_extension
            file = open(filename, "w+")
            while 1:
                temp = recvHeader(dataSocket)
                if not temp:
                    break
                file.write(temp)
            file.close()
            print("SUCCESS: {} downloaded to client".format(filename))
        except socket.error as socketerror:
            print("Error: ", socketerror)
        dataSocket.close()

clientSock.close()
print("Command Socket Closed")






