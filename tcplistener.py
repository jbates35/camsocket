import socket
import netifaces as ni
import threading
import signal
import time

#Messages for managing address list
MSG_ACCEPT = b'accept'
MSG_DELETE = b'delete'

class TcpListener:
    """Threaded class to listen for incoming socket connections and load them to a list
    
    Starts automatically
    Call .end() to close the object.
    """
    
    def __init__(self, port=3513, debug=False):
        """Constructor for tcp listener. Initiate threads for socketing

        Args:
            port (int, optional): server-side port to set incoming tcp connections to listen through. Defaults to 3513.
            debug (bool, optional): turns a debugging mode on for seeing if socket is working properly. Defaults to False.
        """
        self.port = port
        self.debug = debug

        #Server info
        self.server = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
        
        #TCP Thread information
        self.thread_count = 0
        self.tcp_threads = list()
        self.tcp_thread_bools = list()

        #Thread bools
        self.socket_manager_run = True
        self.tcp_listener_run = True
        self.tcp_debug_run = True

        #Address list to send UDP messages to
        self.addr_list = set()

        #TCP part - get any address that might want to connect
        #Open TCP Server socket for program
        self.s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
        try:
            self.s_tcp.bind((self.server, self.port))
        except socket.error as e:
            print(str(e))
        self.s_tcp.listen(5)
        
        #Start threads
        #Main socket listener
        self.tcp_listener_thread = threading.Thread(target=self.tcp_listener, daemon=True)
        self.tcp_listener_thread.start()

        #Manual thread executor
        self.socket_manager_thread = threading.Thread(target=self.socket_manager)
        self.socket_manager_thread.start()
        
        #Debug thread
        if self.debug:        
            self.tcp_debug_thread = threading.Thread(target=self.tcp_debug)
            self.tcp_debug_thread.start()


    def end(self):
        """Closes socket objects and debug so object can close
        """
        #Close socket manager
        print("\nClosing socket manager...")
        self.socket_manager_run = False
        self.socket_manager_thread.join()
        
        #Close tcp debug, if debug mode was turned on
        if self.debug:
            print("Closing tcp debug...")
            self.tcp_debug_run = False
            self.tcp_debug_thread.join()
    
    def multi_threaded_client(self, connection, ind):
        """Listens for protocol messages from client to add address and port

        Args:
            connection (obj): socket object from s_tcp init
            ind (int): index of connection to say whether connection should be closed
        """
        while True:        
            data = connection.recv(2048)
            
            #If data is b'accept', add address and port
            if data == MSG_ACCEPT:
                self.addr_list.add(connection.getpeername())
                print("Address list: \n", self.addr_list) if len(self.addr_list) > 0 else print("No addresses found")
        
            #If data is b'delete', delete address/port and tell executor to close thread
            elif data == MSG_DELETE:
                self.addr_list.remove(connection.getpeername())
                print("Address list: \n", self.addr_list) if len(self.addr_list) > 0 else print("No addresses found")
                print("Socket " + str(ind) + " will be deleted")
                self.tcp_thread_bools[ind] = False
                
            if not data:
                break  
            
                
    def tcp_listener(self):
        """TCP - listening for addrs to handshake
        """      
        #Listening while program is running
        while True:
            #Accept TCP connection
            client, address = self.s_tcp.accept()  
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            
            #Increase self.thread_count as that is the index   
            self.thread_count += 1
            
            #Add socket and thread conditions to threads
            self.tcp_threads.append(threading.Thread(target=self.multi_threaded_client, args=(client, self.thread_count-1)))
            self.tcp_threads[len(self.tcp_threads)-1].start()
            self.tcp_thread_bools.append(True)


    def socket_manager(self):
        """Manual thread executor
        """       
        #When MSG_DELETE is received, delete the socket that was flagged now as False
        while self.socket_manager_run:
            for i in range(len(self.tcp_thread_bools)):
                if self.tcp_thread_bools[i]==False:
                    self.thread_count -= 1
                    del self.tcp_thread_bools[i]
                    del self.tcp_threads[i]    
    
    
    def tcp_debug(self):
        """For debugging, print out how many threads there are to make sure garbage collection is working
        """
        while self.tcp_debug_run:
            print("Thread count: ", len(self.tcp_threads))
            print("Socket bools: ", self.tcp_thread_bools)
            print("Sockets opened: ", self.addr_list, "\n")
            time.sleep(.5)
    
def main():
    tcp_listen = TcpListener(debug=True)
    
    print ("Program started. Server is: ", tcp_listen.server) 
    
    # If ctrl-c is pressed, close tcp socket
    def signal_handler(signum, frame):       
        tcp_listen.end()
          
    # If ctrl+c is pressed ...
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()

if __name__ == "__main__":
    main()