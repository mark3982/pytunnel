'''
    The client connects to the server and provides an output for
    the tunnel to the target internet protocol address and TCP
    port.

    Author:           Leonard Kevin McGuire Jr
'''
import socket
import select
import time
import sys

def main(server, local):
    connected = False

    t = None

    lastping = time.time() 

    buf = b''

    while True:
        if not connected:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)                
                s.connect(server)
                s.settimeout(None)
            except Exception as e:
                time.sleep(5)
                continue
            connected = True

        r = [s]
        w = []
        e = [s]

        if t is not None:
            r.append(t)
            e.append(t)

        r, w, e = select.select(r, w, e, 1)

        # reconnect if we go too long with out a ping, the keepalive
        # was a little too platform specific so it was easier just to
        # add support right into the tunnel protocol instead -kmcg
        if time.time() - lastping > 20:
            connected = False
            s.close()
            continue

        if t in r:
            data = t.recv(4096)
            sendall(s, data)

        if s in r:
            data = s.recv(4096)
            if not data:
                # try to get connected again
                connected = False
                if t is not None:
                    t.close()
                    t = None
                continue
            buf = buf + data
            while len(buf) > 0:
                cmd = buf[0]
                if cmd == 0: # disconnect
                    lastping = time.time()
                    if t is not None:
                        t.close()
                        t = None
                    buf = buf[1:]
                    continue
                elif cmd == 1:
                    lastping = time.time()
                    if t is not None:
                        t.close()
                        t = None
                    t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    t.connect(local)
                    t.settimeout(None)
                    buf = buf[1:]
                elif cmd == 2:
                    lastping = time.time()
                    sz = buf[1] << 24 | buf[2] << 16 | buf[3] << 8 | buf[4]
                    if len(buf) >= 1 + 4 + sz:
                        data = buf[1 + 4:1 + 4 + sz]
                        buf = buf[1 + 4 + sz:]
                        if t is not None:
                            t.settimeout(0)
                            sendall(t, data)
                            t.settimeout(None)
                    else:
                        break
                elif cmd == 3:
                    lastping = time.time()
                    buf = buf[1:]
                else:
                    raise Exception('unknown command')

def sendall(sock, data):
    while len(data) > 0:
        try:
            sent = sock.send(data)
            data = data[sent:]
        except BlockingIOError:
            print('blocking io error')

'''
    The first argument is the server address, and the second
    argument is the target address. The address and port pairs
    are for a TCP/IP connection.
'''
args = sys.argv

if len(args) < 3:
    print('<server-ip>:<server-port> <target-ip>:<target-port>')
    exit()

server = args[1].split(':')
target = args[2].split(':')

# ('kmcg3413.net', 61001), ('192.168.1.118', 5900)
main(server, target)