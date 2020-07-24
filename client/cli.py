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
            dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dataSocket.connect((serverAddr, temp_port))
            temp = ''
            while 1:
                temp = recvHeader(dataSocket)
                if not temp:
                    break
                print (temp)
            dataSocket.close()
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

    def do_get(self, get):
        self.get = get
        if len(get) > 0:
            msg = 'get'
            filename = get
            # send get to server
            sendData(connSock, msg)
            tmp_port = int(recvHeader(connSock))
            # uses tcp to transfer data
            dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dataSocket.connect((serverAddr, tmp_port))
            sendData(dataSocket, filename)
            print("downloading file...")
            # if valid file
            if os.path.exists(filename):
                i = 1
                num = "(" + str(i) + ")"
                f_name, f_extension = os.path.splitext(filename)
                tmp = f_name
                filename = tmp + num + f_extension
                while os.path.exists(filename):
                    i += 1
                    num = "(" + str(i) + ")"
                    filename = tmp + num + f_extension
            # open file to read and send
            file = open(filename, "w+")
            while 1:
                tmp = recvHeader(dataSocket)
                if not tmp:
                    break
                file.write(tmp)
            file.close()
            dataSocket.close()
            print("File download is complete!: {}".format(filename))
        else:
            print('Error: get command needs name of file to download, try again')

    def do_put(self, put):
        self.put = put
        if len(put) > 0:
            msg = 'put'
            filename = put
            # send put to server
            sendData(connSock, msg)
            tmp_port = int(recvHeader(connSock))
            dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dataSocket.connect((serverAddr, tmp_port))
            sendData(dataSocket, filename)
            print("Uploading file...")
            while 1:
                try:
                    file = open(filename, "r")
                except:
                    print("problem opening the file", filename)
                try:
                    #send at one byte at a time
                    bytesCount = 0
                    byte = file.read(1)
                    while byte != "":
                        sendData(dataSocket, byte)
                        byte = file.read(1)
                        bytesCount += 1
                finally:
                    file.close()
                    dataSocket.close()
                    print("File Upload is complete: {} The file size is {} bytes".format(
                        filename, bytesCount))
                    break
        else:
            print('Error: put command needs name of file to upload, try again')

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
        print('SERVER PORT NUMBER format is correct: OK to proceed')
        break

# Create a TCP socket
print("Creating socket...")
connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
print("Connecting to FTP server...")
connSock.connect((serverAddr, serverPort))

switch = ftpCommands()
switch.prompt = 'FTP> '
# enable client input commands
switch.cmdloop(
	'Connection established...\nAvailable Commands to use: ls, get, put, exit')
connSock.close()
print("Command Socket Closed")
