
# client is invokable as follows:
# python client.py serverip port
# e.g.: python client.py 127.0.0.1 12000
# would cause the client to attempt to connect
# to a server already listening
# on 127.0.0.1 (the local system) port number 12000

import sys
# used to take arguments from the command line
import os.path
from os import path
# used to check if log file already exists or not
from socket import socket, AF_INET, SOCK_STREAM
# used to create TCP sockets
from datetime import datetime
# used for log file entries
import pickle
# enables the sending and receiving of
# data types other than strings (arrays in this case)
import select
# used for request timeout checking

def menu(boards):
    # this function presents the user with
    # the available boards and their options
    # it takes 1 argument, an array of board names
    print()
    # blank lines make the output easier for the user to read
    print('These are the available boards:')
    for x in range(len(boards)):
        print(str(x+1) + '. ' + boards[x])
    # formatting the array as a numbered list
    # with each board name on a new line
    print()
    print('x. See 100 most recent messages from board x')
    print('POST. Post a message to a board')
    print('QUIT. Quit')
    choice = ''
    # this loop will ask for an input from the user
    # until they enter a valid option
    # and it will break if they enter "QUIT" (or "quit")
    while choice.upper() != 'QUIT':
        choice = input('What do you want to do? > ')
        # ask for the user's input
        try:
            # this 'if' has to be in a 'try' statement
            # because the int() method would fail on any letter input
            if int(choice) <= len(boards) and int(choice) > 0:
                # checking if the number entered is valid
                # i.e. is in the range available
                result = GET_MESSAGES(boards[int(choice)-1])
                # -1 because of 0 index list
                now = datetime.now()
                # get the date and time, to be entered in the log file
                log = open('client.log','a')
                # open the log file in append mode
                # so that we add to it rather than overwriting it
                log.write('{}:{}\t{}\tGET_MESSAGES\t{}'.format(serverIP, serverPort, str(now)[:19], result))
                # [:19] to exclude milliseconds
                log.write('\n')
                log.close()
                # write to log file
        except:
            pass
            # there is no need to have anything here
            # this is only to catch the ValueError from int()
            # if a string is entered
        try:
            if choice.upper() == 'POST':
                result = POST_MESSAGE(boards)
                now = datetime.now()
                log = open('client.log','a')
                log.write('{}:{}\t{}\tPOST_MESSAGE\t{}'.format(serverIP, serverPort, str(now)[:19], result))
                # [:19] to exclude milliseconds
                log.write('\n')
                log.close()
                # write to log file
                # 'result' is returned by POST_MESSAGE(boards)
                # is either "OK" or "ERROR"
        except:
            pass
            # should never actually get here
    return 'QUIT'
    # if the 'while' loop is broken
    # i.e. the user has entered "QUIT" (or "quit")
    # the client will then be killed

def GET_BOARDS():
    # this function asks the server for
    # a list of defined message board titles
    try:
        now = datetime.now()
        clientSocket = socket(AF_INET, SOCK_STREAM)
        # create a new socket for every request
        clientSocket.connect((serverIP, serverPort))
        # 'serverIP' and 'serverPort' are defined in __main__
        # so are global variables and can be accessed here
        clientSocket.setblocking(False)
        # make sure the socket is not blocking
        # means the server doesn't hang whilst waiting for
        # an input from a slow client
        clientSocket.send(pickle.dumps(['GET_BOARDS']))
        # use pickle.dumps(obj) method to format array
        # so that it can be sent using socket.send()
        ready = select.select([clientSocket], [], [], 10)
        # this is how the client checks for timeout
        # which is set at 10 seconds
        # select.select() waits until data becomes available
        if ready[0]:
            # if data arrives at the socket before timeout
            boards = pickle.loads(clientSocket.recv(4096))
            # receive up to 4096 bytes from the socket
        else:
            # Timeout expired
            # Response not received in 10 seconds
            print('GET_BOARDS failed!')
            # notify user of error
            return 'ERROR'
        clientSocket.close()
        # close socket once done receiving data
        log = open('client.log','a')
        log.write('{}:{}\t{}\tGET_BOARDS\tOK'.format(serverIP, serverPort, str(now)[:19]))
        # [:19] to exclude milliseconds
        log.write('\n')
        log.close()
        print('GET_BOARDS was successful')
        # inform user that function worked
        return boards
        # return boards, which is then formatted by menu(boards)
    except:
        print('GET_BOARDS failed!')
        return 'ERROR'

def GET_MESSAGES(boardTitle):
    # this function asks the server for a list of the
    # 100 most recent messages in a specified board
    # it takes 1 argument, which is the title of the desired board
    try:
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverIP, serverPort))
        clientSocket.setblocking(False)
        clientSocket.send(pickle.dumps(['GET_MESSAGES', boardTitle]))
        # send multiple arguments to server using array
        ready = select.select([clientSocket], [], [], 10)
        if ready[0]:
            # data received before timeout
            messages = pickle.loads(clientSocket.recv(4096))
            # receive up to 4096 bytes from the socket
        else:
            # Timeout expired
            # Response not received in 10 seconds
            print('GET_MESSAGES failed!')
            return 'ERROR'
        clientSocket.close()
        if messages == []:
            # if received empty list
            print("There are no posts in {}".format(boardTitle))
        else:
            print('Here is the content of {}:'.format(boardTitle))
        for x in range(min(100,len(messages))):
            # only want the 100 most recent messages
            # so if there are less than 100, print all
            # but if more then print most recent 100
            print('{}.'.format(x+1))
            # x+1 because of zero indexed lists
            print(messages[x][0])
            print(messages[x][1])
            # 'messages' is a 2D array
            print()
            # blank line for clarity
        print('GET_MESSAGES was successful')
        return 'OK'
    except:
        print('GET_MESSAGES failed!')
        return 'ERROR'

def POST_MESSAGE(boards):
    # this function allows the user to post a message
    # to any of the available message boards
    # and then sends a request to the server to do this
    # it takes 1 argument 'boards' which is an array of board names
    try:
        print('Available boards:')
        for x in range(len(boards)):
            print(str(x+1) + '. ' + boards[x])
        # reiterate the available boards
        # to help the user
        choice = ''
        while choice != 'q' and choice != 'Q':
            choice = input('Post to board > ')
            # keep asking until receive valid input
            try:
                # use 'try' because int() will give ValueError on bad input
                if int(choice) <= len(boards) and int(choice) > 0:
                    break
            except:
                pass
        # only reach here once 'choice' is an integer in the valid range
        board = boards[int(choice)-1]
        # -1 because of 0 index list
        title = input('Enter your post title: ')
        # free space for single line user input
        message = input('Enter message below:\n')
        # free space for single line user input
        clientSocket = socket(AF_INET, SOCK_STREAM)
        # create socket
        clientSocket.connect((serverIP, serverPort))
        # connect to server
        clientSocket.setblocking(False)
        # make sure socket is not blocking
        clientSocket.send(pickle.dumps(['POST_MESSAGE', board, title, message]))
        # send data to server
        # using array to send multiple arguments
        clientSocket.close()
        # close socket
        print('POST_MESSAGE was successful')
        # inform user of success
        return 'OK'
    except KeyboardInterrupt:
        print()
        print('^C received')
        print('Exiting back to menu')
        # user is able to quit back to main menu
        return 'ERROR'
    except:
        print('POST_MESSAGE failed!')
        return 'ERROR'

if __name__ == "__main__":
    # when program is run directly
    try:
        serverIP = sys.argv[1]
        serverPort = int(sys.argv[2])
        # take command line arguments
        if not path.exists('client.log'):
            # if log file does not yet exist, then
            log = open('client.log','a')
            # open it, and
            log.write('IP : Port\tDate/Time\tType\tResult\n')
            # initialise it with column headers,
            log.close()
            # then close it
        now = datetime.now()
        boards = GET_BOARDS()
        # first function called it GET_BOARDS(), returns list of boards
        # boards == [] means there are no message boards defined
        # boards == 'ERROR' means request timed out
        # boards is None means server not running
        if boards is None or boards == 'ERROR' or boards == []:
            # if the server is not running, or request fails somehow
            print('error')
            log = open('client.log','a')
            log.write('{}:{}\t{}\tGET_BOARDS\tERROR'.format(serverIP, serverPort, str(now)[:19]))
            # [:19] to exclude milliseconds
            log.write('\n')
            log.close()
        else:
            menu(boards)
            # menu() formats and displays boards and gives user options
    except KeyboardInterrupt:
        # if ^C pressed at any point
        print()
        print('^C received')
        print('Shutting down client')
    except:
        # if any errors occur in __main__
        print('error')
