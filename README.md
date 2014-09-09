pytunnel
========

A simple tool used to create a TCP tunnel. This can be used as a solution to the problem of not being able to accept incoming connections because of network limitations. You can find the exact same functionality using SSH with added security. This tool is only intended to be used when added security is not needed and SSH is unable to be used. _This tool will run on both Linux and Windows, or any system capable of running Python._

You would generally need to use three machines to make this tunnel possible. You have your one client machine which
requires not software, the server (requires server.py), and the tunnel end-point (requires client.py). What happens
is the client (tunnel) will connect to the server. You then connect to the server which tunnels your connection to the tunnel
end-point which then connects to the target.

A more graphical view looks something like this:

    (target)<----(endpoint)---->[firewall/nat]---->(server)<----------(client)
                    ^                                 ^
                    |                                 |
               runs endpoint.py                     runs server.py

The client connects to the server. The endpoint connects to the server. When the client connects to the server the
endpoint is told to connect to the target and a tunnel is established.

_The client requires
no software to be installed and can be any machine that can access the server over TCP/IP._

_At the moment only TCP/IPv4 is supported. I may added support for more protocols, and even multiple clients later. You can run multiple instances of the server to support multiple
endpoint instances. I may even add support for endpoints to authenticate with the server and
automatically open the desired port._

_Also on my mind is adding SSH support for the tunnel._

You can chain tunnels together for example consider:

     (T)<--------------(E1)----->(S1)(E2)<-------(S2)(C)
      ^                  ^           ^              ^
      |                  |           |              |
    target server      machine     machine         client

In this case `T` is the target. The `S1` and `E2` reside on the internet server which is
accessible for incomining connections from `E1` and `S2`. The `S2` and `C` reside on the
same machine (your local machine). The client `C` connects to the server `S2` which is
connected to by `E2` and thus the connection is forward from `S2` to `E2`. The `E2` then
forwards the connection into `S1` which is connected to by `E1` navigating across the NAT.
The connection is then forwarded from `E1` to `T`. The purpose here would be more clear if
SSH was implemented thus encrypting the entire connection across the internet until it reaches
`E1` which would turn into the application protocol.


examples
========  

To serve a website with limitations (mostly just an understandable example).

     python3 server.py 61001 61002
     python3 endpoint.py mytarget.com:80 myserver.net:61001
     http://myserver.net:61002

To use VNC with the tunnel. 

     python3 server.py 61001 61002
     python3 endpoint.py localhost:5900 myserver.net:61001
     vnc myserver.net::61002

_This is one I use personally. I have some machines behind a NAT that does not allow
ports to be forwarded. To overcome this I setup the tunnel and the endpoint machine
connects outbound to my server. The clients connect to my server which tunnels the data
back to the persistent connection with the endpoint. The endpoint forwards the connect
to the VNC server running locally thus overcoming the NAT._

To use SSH with the tunnel.

     python3 server.py 61001 61002
     python3 endpoint.py localnetserver:22 myserver.net:61001
     ssh myserver.net:61002

_Also a similar situation where I needed to overcome the NAT. In this case localnetserver could be
localhost or another computer accessable for example 192.168.1.10 could be a local server and you are unable to install the endpoint directly onto it. Or, in the case you can you would use localhost._

The arguments:
    
     python3 server.py <tunnel-port> <client-port>
     python3 endpoint.py <target-host>:<target-port> <server-host>:<tunnel-port>
     <application> <server-host>:<tunnel-port>

_The server simply needs a port to listen on for the endpoint (`tunnel-port`), and a port
to listen on for the client (`client-port`). The endpoint needs to know the server IP/host
and the port to connect to, and it needs to know the target (aka destination) for the forwarded
connection with the `target-host` and `target-port`.