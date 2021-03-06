import socket
import os.path
import sys
import subprocess
from cmd import Cmd

# Command line checks
if len(sys.argv) != 3:
	print ('ERROR:To Run: python3 ' + sys.argv[0] + ' <Server Machine> ' + ' <Port Number> ')

serverAddr = sys.argv[1]
serverPort = sys.argv[2]

#check for valid port
while True:
    try:
        if (serverPort.isdigit() == False):
            raise TypeError('You cannot have letters in your port number')
    except TypeError as typeerror:
        print('PORT NUMBER format {} is incorrect. Try again'.format(
            serverPort), typeerror)
        sys.exit()
    else:
        serverPort = int(serverPort)
        print('SERVER PORT NUMBER format is correct: OK to proceed')
        break

# Create a TCP socket
print("Creating TCP socket...")
connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
print("Connecting to FTP server...")
connSock.connect((serverAddr, serverPort))

# ************************************************
# Sends the specified data from the specified socket
# @param socket - the socket from which to receive
# @param data - data to send
# *************************************************
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
# Receives the number of bytes from the specified socket
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

# ************************************************
# Receives the filesize and data from the header from the specified socket
# @param socket - the socket from which to receive
# @return - the filesize and data
# *************************************************
def recvHeader(socket):
    data = ""
    fileSize = 0
    fileSizeBuffer = ""
    # Receive the first 10 bytes indicating the size of the file
    fileSizeBuffer = recvAll(socket, 10)
    try:
        # Get the file size
        fileSize = int(fileSizeBuffer)
        # Get the file data
        data = recvAll(socket, fileSize)
    except:
        pass
    return data

# class to handle all the commands sent to server
class MyPrompt(Cmd):
    def do_ls(self, ls):
        # myCmd = 'ls -hS'
        self.ls = ls
        if len(ls) == 0:
            msg = 'ls'
            # subprocess.call(msg)
            # send ls command to server
            # os.system(myCmd)
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
            # Sends exit command to server
            sendData(connSock, msg)
            print(recvHeader(connSock))
            return True
        else:
            print('Error: try again')

    def do_get(self, args):
        self.args = args
        if len(args) > 0:
            msg = 'get'
            filename = args
            # Sends get command to server
            sendData(connSock, msg)
            temp_port = int(recvHeader(connSock))
            # uses tcp to transfer data
            dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dataSocket.connect((serverAddr, temp_port))
            sendData(dataSocket, filename)            
            file = open(filename, "wb")
            print("downloading file...")
            while True:
                temp = recvHeader(dataSocket)
                if not temp:
                    break
                file.write(temp)
            file.close()
            dataSocket.close()
            print("File download is complete: {}".format(filename))       
        else:
            print('Error: get command needs name of file to download, try again')

    def do_put(self, args):
        self.args = args
        if len(args) > 0:
            msg = 'put'
            filename = args
            if os.path.exists(filename):
                print("Uploading file...")
                # Sends put command to server
                sendData(connSock, msg)
                tmp_port = int(recvHeader(connSock))
                dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dataSocket.connect((serverAddr, tmp_port))
                sendData(dataSocket, filename)
                file = True
            else:
                print ("ERROR: {} does not exist in client, try again".format(filename))
                file = False
            while file:
                file = open(filename, "rb")
                #send at one byte at a time
                bytesCount = 0
                byte = file.read(1)
                while byte != "":
                    sendData(dataSocket, byte)
                    byte = file.read(1)
                    bytesCount += 1
                file.close()
                dataSocket.close()
                print("SUCCESS: {} Uploaded to Server. The file size is {} bytes".format(
                    filename, bytesCount))
                break
        else:
            print('Error: put command needs name of file to upload, try again')

# main program loop
if __name__ == '__main__':
    prompt = MyPrompt()
    prompt.prompt = 'FTP> '
    prompt.cmdloop(
    	'Connection established...\nAvailable Commands to use: ls, get, put, exit')
    connSock.close()
    print("Command Socket Closed")
