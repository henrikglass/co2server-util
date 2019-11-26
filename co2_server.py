import sys, getopt
import inotify.adapters
import socket
import time
import _thread

local_ip = "xxx.xxx.xxx.xxx"
local_port = 6666
co2_table = ""
co2_table_lock = _thread.allocate_lock()

# handle client
def handle_client(conn):
    with co2_table_lock:
        conn.send(co2_table.encode())
        conn.close()

# Updates co2_table from file.
def load_co2_table():
    global co2_table 
    with co2_table_lock:
        time.sleep(10) # Probably not necessary. But why not. We have time.
        file = open("co2_table.txt", "r")
        co2_table = file.read()
        file.close()

# periodically update co2_table contents
def perpetually_load_co2_table():
    
    # update table on start
    load_co2_table()
    print("read file!")
    
    i = inotify.adapters.Inotify()
    i.add_watch('co2_table.txt')

    # listen for inotify events 
    for event in i.event_gen(yield_nones=False):
        (a, type_names, path, filename) = event

        # If file was written to update co2_table
        if(type_names[0] == 'IN_CLOSE_WRITE'):
            print("read file again!")
            load_co2_table()

# parse args
def parse_args(argv):
    global local_ip
    global local_port
    try:
        opts, args = getopt.getopt(argv, "i:p:")
    except:
        print("Error parsing input arguments")
        sys.exit()
    for opt, arg in opts:
        if opt == '-i': local_ip = arg
        if opt == '-p': local_port = int(arg)

def main(argv): 
    parse_args(argv)
    _thread.start_new_thread(perpetually_load_co2_table, ())

    # handle incoming connections
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((local_ip, local_port))
    server.listen(5)
    while True:
        conn, addr = server.accept()
        _thread.start_new_thread(handle_client, (conn,))

if __name__ == '__main__':
    main(sys.argv[1:])
