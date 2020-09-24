
# server is invokable as follows:
# python server.py serverip port
# e.g.: python server.py 127.0.0.1 12000
# would cause the server to listen
# on 127.0.0.1 (the local system) port number 12000

import sys
# used to take arguments from the command line
import os.path
from os import path
# used to check if log file already exists or not
from os import walk
# used to traverse the "board" folder
from socket import socket, AF_INET, SOCK_STREAM
# used to create TCP sockets
from datetime import datetime
# used for log file entries and for post titles
import pickle
# enables the sending and receiving of
# data types other than strings (arrays in this case)

def GET_BOARDS():
    # this function sends a list of 
    # the titles of available boards to the client
    try:
        path = "./board"
        # the 'board' sub-directory contains
        # all of the message boards
        boards = []
        # we are going to be returning an array
        for root, directories, files in os.walk(path):
            # traverse the 'board' directory
            for folder in directories:
                # look at all of the folders (message boards)
                boards.append(folder.replace('_',' '))
                # replace any underscores with spaces
                # because folder names represent board titles
                # but folder names use '_' whenever the title contains a ' '
        connectionSocket.send(pickle.dumps(boards))
        # use pickle.dumps(obj) method to format array
        # so that it can be sent using socket.send()
        if boards == []:
            # if there are no boards defined
            return False
        return 'OK'
        # to be used in log file
    except:
        return 'ERROR'
        # to be used in log file

def GET_MESSAGES(boardTitle):
    # this function sends the client a list of the 
    # 100 most recent messages in a specified board
    # it takes 1 argument, which is the title of the desired board
    try:
        boardTitle = boardTitle.replace(' ','_')
        # replace any spaces in 'boardTitle' with underscores
        # because all folder names use '_'
        # to represent ' ' in the board title
        path = "./board/{}".format(boardTitle)
        # we are going to be traversing this sub-directory
        messages = []
        # will return a 2D array of message titles and message content
        for root, directories, filenames in os.walk(path):
            # traverse the 'board/"boardTitle"' directory
            for file in filenames:
                    # look at all of the files (messages)
                    messages.append([file[16:].replace('_',' ')])
                    # [16:] so that we don't include the 'board/"boardTitle"' prefix
                    # also replace any underscores in with spaces
                    # since these file names represent message titles
                    message = open(os.path.join(root, file),'r')
                    # open the file
                    # os.path.join() formats the path
                    messages[-1].append(message.readline())
                    # message content is only 1 line, so this is fine
        connectionSocket.send(pickle.dumps(messages))
        # send response back to the server
        # messages is a 2D array, formatted as such:
        # [[message title, message content],[...],...]
        return 'OK'
        # to be used in log files
    except:
        return 'ERROR'
        # to be used in log files

def POST_MESSAGE(boardTitle, postTitle, messageContent):
    # this function creates a file in the corresponding folder
    # to represent the message
    try:
        now = str(datetime.now())
        # get date and time, to be used in filename
        now = now.replace('-','')
        now = now.replace(' ','-')
        now = now.replace(':','')
        now = now[:15]
        # format date and time to look like:
        # 20191101-091100
        boardTitle = boardTitle.replace(' ','_')
        # replace spaces in 'boardTitle' with underscores
        postTitle = postTitle.replace(' ','_')
        # replace spaces in 'postTitle' with underscores
        post = open("./board/{}/{}-{}".format(boardTitle,now,postTitle),"w+")
        # create new file with specified name
        post.write("{}".format(messageContent))
        # then write message content to file
        return 'OK'
        # to be used in log files
    except:
        return 'ERROR'
        # to be used in log files

if __name__ == "__main__":
    # when program is run directly
    try:
        serverIP = sys.argv[1]
        serverPort = int(sys.argv[2])
        # take command line arguments
        serverSocket = socket(AF_INET, SOCK_STREAM)
        # create a server socket
        serverSocket.bind((serverIP, serverPort))
        # bind the socket to an address
        serverSocket.listen(5)
        # allow up to 5 clients concurrently
        print("server running at {} on port {}".format(serverIP, serverPort))
        # inform user that the server is running
        if not path.exists('server.log'):
            # if log file does not yet exist, then
            log = open('server.log','a')
            # open it, and
            log.write('IP : Port\tDate/Time\tType\tResult\n')
            # initialise it with column headers,
            log.close()
            # then close it
        while True:
            # main program loop, wait for a request, and serve it
            connectionSocket, addr = serverSocket.accept()
            # accept connections from outside
            connectionSocket.setblocking(False)
            # make sure socket does not block
            command = pickle.loads(connectionSocket.recv(4096))
            # receive up to 4096 bytes from the socket
            # this is plenty

            # command is an array of format:
            # [Function, agrument 1*, argument 2*, argument 3*]
            # * if applicable
            # GET_BOARDS take no arguments
            # GET_MESSAGES takes 1 argument
            # POST_MESSAGE takes 3 arguments
            log = open('server.log','a')
            # open log file
            now = datetime.now()
            # get time of request, for server.log
            if command[0] == 'GET_BOARDS':
                # if client has sent a GET_BOARDS request
                result = GET_BOARDS()
                # result is False if there are no boards defined
                if not result:
                    print('error')
                    # there are no message boards defined
                    break
                    # will print error and exit
            elif command[0] == 'GET_MESSAGES':
                # if client has sent a GET_MESSAGES request
                result = GET_MESSAGES(command[1])
                # the argument for GET_MESSAGES is the
                # second item in the command array
            elif command[0] == 'POST_MESSAGE':
                # if client has sent a POST_MESSAGE request
                result = POST_MESSAGE(command[1],command[2],command[3])
                # the arguments for POST_MESSAGE are the
                # 2nd, 3rd, and 4th items in the command array
            log.write('{}:{}\t{}\t{}\t{}'.format(serverIP, serverPort, str(now)[:19], command[0], result))
            # [:19] to exclude milliseconds
            # write to log file
            log.write('\n')
            # new line in log file
            log.close()
            # close log file
        # if server breaks out of its running loop
        # will only do this if there are no message boards defined
        connectionSocket.close()
        # close connectionSocket
        serverSocket.close()
        # close serverSocket
        # kill connections before server program finishes
        # last things to happen before server shuts down
    except KeyboardInterrupt:
        # if ^C pressed at any point
        print()
        print('^C received')
        print('Shutting down server')
    except:
        # if any errors occur in __main__
        print('error')
