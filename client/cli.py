import socket
import sys
import subprocess
from cmd import Cmd
import os

# Command line checks
if len(sys.argv) < 3:
	print ('ERROR:To Run: python3 ' + sys.argv[0] + ' <Server Machine> ' + ' <Port Number> ')

serverAddr = sys.argv[1]
serverPort = sys.argv[2]

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
        fileSize = int(fileSizeBuffer)
        # receive a file given a file size
        data = recvAll(socket, fileSize)
    except:
        pass
    return data
class ftpCommands(Cmd):
    def do_ls(self, ls):
        self.ls = ls
        if len(ls) == 0:
            msg = 'ls'
            subprocess.call(msg)
            # send ls command to server
            sendData(connSock, msg)
            temp_port = int(recvHeader(connSock))
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.connect((serverAddr, temp_port))
            temp = ''
            while 1:
                temp = recvHeader(data_socket)
                if not temp:
                    break
                print (temp)
            data_socket.close()
        else:
            print('Error: try again')

    def do_exit(self, exit):
        self.exit = exit
        if len(exit) == 0:
            msg = 'exit'
            # End connection to server
            sendData(connSock, msg)
            print(recvHeader(connSock))
            return True
        else:
            print('Error: try again')



#check for valid port
while True:
    try:
        if (serverPort.isdigit() == False):
            raise TypeError('You cannot have letters in your port number')
    except TypeError as typeerror:
        print('PORT NUMBER format {} is incorrect. Try again'.format(serverPort), typeerror)
        sys.exit()
    else:
        serverPort = int(serverPort)
        print('SERVER PORT NUMBER format is correct: proceed')
        break

# Create a TCP socket
print("Creating socket...")
connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
print("Connecting to server...")
connSock.connect((serverAddr, serverPort))

print("Available Commands to use: ls, get, put, exit")
switch = ftpCommands()
switch.prompt = 'FTP> '
# enable client input commands
switch.cmdloop('Connection established...')
connSock.close()
print("Command Socket Closed")
