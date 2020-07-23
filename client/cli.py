import socket
import sys
import subprocess
from cmd import Cmd

# Command line checks
if len(sys.argv) < 3:
	print ('ERROR:To Run: python3 ' + sys.argv[0] + ' <Server Machine> ' + ' <Port Number> ')

serverAddr = sys.argv[1]
serverPort = sys.argv[2]


def send_data(sock, data):
    data_size = str(len(data))
    #set header to 10 bytes
    while len(data_size) < 10:
        data_size = "0" + data_size

    data = data_size + data
    data_sent = 0

    #ensure all data is sent
    while data_sent < len(data):
        data_sent += sock.send(data[data_sent:])

def recvAll(socket, numBytes):

    recvBuffer = ''
    tmpBuffer = ''
    # ensure all data has been recieved
    while len(recvBuffer) < numBytes:
        tmpBuffer = socket.recv(numBytes)
        # The other side has closed the socket
        if not tmpBuffer:
            break
        recvBuffer += tmpBuffer
    return recvBuffer

def recvHeader(socket):
    data = ''
    fileSize = 0
    fileSizeBuffer = ''
    # header size buffer
    fileSizeBuffer = recvAll(socket, 10)
    try:
        fileSize = int(fileSizeBuffer)
        # receive a file given a file size
        data = recvAll(socket, fileSize)
    except:
        pass
    return data
class ftp_command(Cmd):
    def do_ls(self, args):
        if len(args) == 0:
            msg = 'ls'
            subprocess.call(msg)
            # send ls command to server
            send_data(connSock, msg)
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
            print("ls does not take arguments")

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
prompt = ftp_command()
prompt.prompt = 'FTP> '
# enable client input commands
prompt.cmdloop('Connection established...')



connSock.close()
print("Command Socket Closed")
