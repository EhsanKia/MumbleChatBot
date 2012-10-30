from twisted.internet import ssl, reactor
from twisted.internet.protocol import ClientFactory
from client import *

# Server information
server_ip   = "mumble.ehsankia.com"
server_port = 64742

class BotClientFactory(ClientFactory):
    protocol = BotClient

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed"
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection lost"
        reactor.stop()

factory = BotClientFactory()
reactor.connectSSL(server_ip, server_port, factory, ssl.ClientContextFactory())
reactor.run()
