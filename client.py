import mumble_protobuf
import struct
from twisted.internet.protocol import Protocol
from twisted.internet.task import LoopingCall
from twisted.python.rebuild import rebuild
import plugins

# Packet types
class Packet:
    VERSION      = 0
    AUTHENTICATE = 2
    PING         = 3
    TEXTMESSAGE  = 11

username    = "PeeBot"
server_pass = ""

class BotClient(Protocol):
    def connectionMade(self):
        # Send Version
        buf = getClientVersion()
        self.transport.write( buf )

        # Authenticates
        buf = getAuthentication()
        self.transport.write( buf )

        # Starts sending heartbeat
        self.heartbeat = LoopingCall(self.sendHeartbeat)
        self.heartbeat.start(5, now=False)

    def dataReceived(self, data):
        while data:
            pType, pLen, pData, data = unpackData(data)
            
            if pType == 11:
                msg, chan = parseMessage(pData)
                resp = plugins.getResponse(msg)
                if resp:
                    buf = getMessage(resp, chan)
                    self.transport.write( buf )

    def sendHeartbeat(self):
        ping = mumble_protobuf.Ping()
        payload = ping.SerializeToString()
        buf = struct.pack(">hi%ds" % len(payload), Packet.PING, len(payload), payload)
        self.transport.write( buf )

def unpackData(data):
    packetType, packetLen = struct.unpack(">hi",data[:6])
    packetData = data[6:packetLen+6]
    return packetType, packetLen, packetData, data[packetLen+6:]

def getClientVersion():
    cVersion = mumble_protobuf.Version()
    cVersion.version = 66051
    payload = cVersion.SerializeToString()
    return struct.pack(">hi%ds" % len(payload), Packet.VERSION, len(payload), payload)
    
def getAuthentication():
    auth = mumble_protobuf.Authenticate()
    auth.username = username
    auth.password = server_pass
    payload = auth.SerializeToString()
    return struct.pack(">hi%ds" % len(payload), Packet.AUTHENTICATE, len(payload), payload)

def getMessage(text,channel=[0],session=None):
    msg = mumble_protobuf.TextMessage()
    msg.message = text
    msg.channel_id.extend(channel)
    payload = msg.SerializeToString()
    return struct.pack(">hi%ds" % len(payload), Packet.TEXTMESSAGE, len(payload), payload)

def parseMessage(data):
    msg = mumble_protobuf.TextMessage()
    msg.ParseFromString( data )
    return msg.message, msg.channel_id
