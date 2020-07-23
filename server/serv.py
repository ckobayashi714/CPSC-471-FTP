import socket
import sys
import subprocess
import commands

# import commands

# Command line checks
if len(sys.argv) < 2:
	print ('ERROR:To Run: python3 ' + sys.argv[0] + ' <Port Number> ')

listenPort = sys.argv[1]

#check for valid port
while True:
    try:
        if (listenPort.isdigit() == False):
            raise TypeError('You cannot have letters in your port number')
    except TypeError as typeerror:
        print('PORT NUMBER format {} is incorrect. Try again'.format(listenPort), typeerror)
        sys.exit()
    else:
        listenPort = int(listenPort)
        print('PORT NUMBER format is correct: proceed')
        break


# Create a welcome socket.
welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
welcomeSock.bind(('', listenPort))

#Listen for a connection
welcomeSock.listen(1)
print ('Waiting for connections...')

# Accept connections
clientSock, addr = welcomeSock.accept()
print ('Accepted connection from client: ', addr)
print ('\n')

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
    recvBuffer = ''
    tempBuffer = ''
    # ensure all data has been received
    while len(recvBuffer) < numBytes:
        tempBuffer = socket.recv(numBytes)
        # The other side has closed the socket
        if not tempBuffer:
            break
        recvBuffer += tempBuffer
    return recvBuffer

# def recvHeader(socket):
#     data = ""
#     fileSize = 0
#     fileSizeBuffer = ""
#     #receive header size
#     fileSizeBuffer = recvAll(socket, 10)
#     #initialize buffer for file
#     fileSize = int(fileSizeBuffer)

#     # receive a file given a file size
#     data = recvAll(socket, fileSize)
#     return data

def recv(sock):
    data = ""
    file_size = 0
    file_size_buff = ""
    #receive header size
    file_size_buff = recvAll(sock, 10)
    #initialize buffer for file
    file_size = int(file_size_buff, base=10)

    # receive a file given a file size
    data = recvAll(sock, file_size)
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

# def switchcase():
#     print(('What would you like to do?\n'))
#     print('List files, type < ls >')
#     print('Receive files from the Client? type < get >\n')
#     print('Send files to the Client? type < put >\n')
#     print('Close the connection, type < exit >\n')
#     choice = raw_input()
#     args = shlex.split(choice)
#     print(args)
    
while True:
    try:
        command = recv(clientSock)
        if command == 'ls':      
            temp = ''
            dataSocket = connection()
            for line in commands.getoutput('ls'):
                temp += line


            sendData(dataSocket, temp)
            print('************SUCCESS of ls cmd*******')
            dataSocket.close()
    except:
        pass
clientSock.close()
print("Command Socket Closed")






