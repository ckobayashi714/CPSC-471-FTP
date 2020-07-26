import socket
import sys
import subprocess
import commands
import os

# Command line checks
if len(sys.argv) < 2:
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

data = ''

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

def recvAll(socket, numBytes):
    recvBuffer = ""
    tempBuffer = ""
    
    # ensure all data has been received
    while len(recvBuffer) < numBytes:
        tempBuffer = socket.recv(numBytes)
        
        # The other side has closed the socket
        if not tempBuffer:
            break
        recvBuffer += tempBuffer
    return recvBuffer

def recvHeader(socket):
    data = ""
    fileSize = 0
    fileSizeBuffer = ""
    # header size buffer
    fileSizeBuffer = recvAll(socket, 10)
    try:
        fileSize = int(fileSizeBuffer, base=10)
        # receive a file given a file size
        data = recvAll(socket, fileSize)
    except:
        pass
    return data

def connection():
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # open an ephemeral port to send data
    temp_socket.bind(('', 0))
    socket_number = str(temp_socket.getsockname()[1])
    sendData(clientSock,  socket_number)
    temp_socket.listen(1)
    new_socket, addr = temp_socket.accept()
    return new_socket

while True:
    command = recvHeader(clientSock)
    if command == "ls":      
        temp = ''
        dataSocket = connection()
        for line in commands.getoutput('ls -l'):
            temp += line
        sendData(dataSocket, temp)
        print('************ls command was successfully received and accepted*******')
        dataSocket.close()
        
     # exit command
    if command == "exit":
        print('***********exit command was successfully received and accepted*******')
        break

    if command == "get":
        dataSocket = connection()
        file_name = recvHeader(dataSocket)
        while True:
            try:
                file = open(file_name, "r")
            except:
                print("problem opening the file...", file_name)
            try:
                #send file byte
                byte = file.read(1)
                while byte != "":
                    sendData(dataSocket, byte)
                    byte = file.read(1)
                print("*********get command was successfully received and accepted")
            finally:
                file.close()
                dataSocket.close()
                break

    # put command
    if command == "put":
        dataSocket = connection()
        file_name = recvHeader(dataSocket)
        print("***********put command was successfully received and accepted")
        try:
            if os.path.exists(file_name):
                i = 1
                num = "(" + str(i) + ")"
                f_name, f_extension = os.path.splitext(file_name)
                tmp = f_name
                file_name = tmp + num + f_extension
                while os.path.exists(file_name):
                    i += 1
                    num = "(" + str(i) + ")"
                    file_name = tmp + num + f_extension
            file = open(file_name, "w+")
            while 1:
                tmp = recvHeader(dataSocket)
                if not tmp:
                    break
                file.write(tmp)
            file.close()
            print("File download is complete...")
        except socket.error as socketerror:
            print("Error: ", socketerror)
        dataSocket.close()

clientSock.close()
print("***********Command Socket Closed****************")






