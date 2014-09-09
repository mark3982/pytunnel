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
               runs client.py                     runs server.py

  The client connects to the server. The endpoint connects to the server. When the client connects to the server the
  endpoint is told to connect to the target and a tunnel is established.
  
  _The script named client.py is a little misleading. It is actually the endpoint or tunnel exit. The actual client requires
  no software to be installed and can be any machine that can access the server over TCP/IP._
  
  _At the moment only TCP/IPv4 is supported. I may added support for more protocols, and even multiple clients later._