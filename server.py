import socket
import select
import struct

def main():
    tss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tss.bind(('0.0.0.0', 61001))

    ess = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ess.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ess.bind(('0.0.0.0', 61002))

    tss.listen(1)
    ess.listen(1)

    tsock = None
    esock = None

    tunnels = []

    while True:
        r = [tss, ess]
        w = []
        e = []

        if tsock is not None:
            r.append(tsock)
            e.append(tsock)
        if esock is not None:
            r.append(esock)
            e.append(esock)

        r, w, e = select.select(r, w, e)

        if tss in r:
            print('tunnel connection')
            tsock, addr = tss.accept()
            tsock.settimeout(None)
            r.remove(tss)

        if ess in r:
            print('client connected')
            esock, addr = ess.accept()
            esock.settimeout(None)
            r.remove(ess)
            if tsock is not None:
                print('   tunnel notified of connection')
                tsock.send(struct.pack('>B', 1))
            else:
                # no tunnel so just close the client back out
                esock.close()
                esock = None

        if esock in e:
            tsock.send(struct.pack('>B', 0))
            esock = None

        if tsock in e:
            if esock is not None:
                esock.close()
                esock = None
            tsock = None

        # only esock or tsock should be here now
        for sock in r:
            # recieve data from this client
            try:
                data = sock.recv(4096)
            except ConnectionResetError:
                print('connection reset error')
                data = b''
            if not data:
                if tsock is sock:
                    print('tunnel dropped')
                    if esock is not None:
                        print('    dropping client')
                        esock.close()
                        esock = None
                    tsock = None
                    continue
                if esock is sock:
                    esock.settimeout(0)
                    sendall(tsock, struct.pack('>B', 0))
                    esock.settimeout(None)
                    esock = None
                    continue
            if tsock is sock:
                #print('data (tunnel -> client)')
                # send it as raw data to the E client
                if esock is not None:
                    esock.settimeout(0)
                    sendall(esock, data)
                    esock.settimeout(None)
                continue
            if esock is sock:
                #print('data (client -> tunnel) %s' % len(data))
                # transform it into the format the T client expects
                if tsock is not None and len(data) > 0:
                    tsock.settimeout(0)
                    sendall(tsock, struct.pack('>BI', 2, len(data)) + data)
                    tsock.settimeout(None)
                continue
    return

def sendall(sock, data):
    while len(data) > 0:
        try:
            sent = sock.send(data)
            data = data[sent:]
        except BlockingIOError:
            print('blocking io error')

while True:
    try:
        main()
    except Exception as e:
        print(e)
        print('failure restarting')
        continue