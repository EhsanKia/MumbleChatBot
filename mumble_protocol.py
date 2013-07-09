from twisted.internet import protocol, task
from utils import parse_varint
import mumble_protobuf
import struct

MUMBLE_VERSION = 66052  # 1.2.4
LOGGING = True


# Packet types
class Packet:
    VERSION      = 0
    UDPTUNNEL    = 1
    AUTHENTICATE = 2
    PING         = 3
    USERSTATE    = 9
    TEXTMESSAGE  = 11

PACKET_NAMES = {
    0: "Version",
    1: "UDPTunnel",
    2: "Authenticate",
    3: "Ping",
    4: "Reject",
    5: "ServerSync",
    6: "ChannelRemove",
    7: "ChannelState",
    8: "UserRemove",
    9: "UserState",
    10: "BanList",
    11: "TextMessage",
    12: "PermissionDenied",
    13: "ACL",
    14: "QueryUsers",
    15: "CryptSetup",
    16: "ContextActionModify",
    17: "ContextAction",
    18: "UserList",
    19: "VoiceTarget",
    20: "PermissionQuery",
    21: "CodecVersion",
    22: "UserStats",
    23: "RequestBlob",
    24: "ServerConfig",
    25: "SuggestConfig"
}


class VoicePacket():
    def __init__(self):
        self.session = 0
        self.type = 0
        self.target = 0
        self.sequence = 0
        self.lengths = []
        self.frames = []

    def __str__(self):
        s = "Session: {}\nType: {}\nTarget: {}\nSequence: {}\n"
        return s.format(self.session, self.type, self.target, self.sequence)


class MumbleClient(protocol.Protocol):
    """Implements mumble's protocol for communicating with a murmur server.
    http://mumble.sourceforge.net/Protocol"""

    def connectionMade(self):
        # Send version packet
        self.send_version()

        # Sends authentication packet
        self.send_auth()

        # Starts sending heartbeat
        self.heartbeat = task.LoopingCall(self.send_ping)
        self.heartbeat.start(10, now=False)

    def dataReceived(self, data):
        while data:
            p_type, parsed, data = self.unpack_data(data)

            if LOGGING and p_type not in [1, 3, 7]:
                print "Type:", parsed.DESCRIPTOR.name
                print parsed

            if p_type in self.get_handlers().keys():
                self.get_handlers()[p_type](parsed)

    def connectionLost(self, reason):
        print "Connection lost"

    # Generates the mumble protocol packets
    def pack_data(self, packet_type, payload):
        return struct.pack(">hi%ds" % len(payload), packet_type, len(payload), payload)

    def send_version(self):
        client_version = mumble_protobuf.Version()
        client_version.version = MUMBLE_VERSION
        payload = client_version.SerializeToString()
        packet = self.pack_data(Packet.VERSION, payload)
        self.transport.write(packet)

    def send_auth(self):
        client_auth = mumble_protobuf.Authenticate()
        client_auth.username = self.factory.nickname
        client_auth.password = self.factory.password
        client_auth.celt_versions.append(-2147483637)
        client_auth.celt_versions.append(-2147483632)
        client_auth.opus = True
        payload = client_auth.SerializeToString()
        packet = self.pack_data(Packet.AUTHENTICATE, payload)
        self.transport.write(packet)

    def send_ping(self):
        ping = mumble_protobuf.Ping()
        payload = ping.SerializeToString()
        packet = self.pack_data(Packet.PING, payload)
        self.transport.write(packet)

    def send_textmessage(self, text, channels=[], users=[]):
        """Send chat message to a list of channels or users by ids"""
        msg = mumble_protobuf.TextMessage()
        msg.message = text
        if channels:
            msg.channel_id.extend(channels)
        if users:
            msg.session.extend(users)
        payload = msg.SerializeToString()
        packet = self.pack_data(Packet.TEXTMESSAGE, payload)
        self.transport.write(packet)

    def move_user(self, channel_id, user_id):
        state = mumble_protobuf.UserState()
        state.session = user_id
        state.channel_id = channel_id
        payload = state.SerializeToString()
        packet = self.pack_data(Packet.USERSTATE, payload)
        self.transport.write(packet)

    def mute_or_deaf(self, user_id, mute=True, deaf=True):
        state = mumble_protobuf.UserState()
        state.session = user_id
        if user_id == self.session:
            state.self_mute = mute
            state.self_deaf = deaf
        else:
            state.mute = mute
            state.deaf = deaf
        payload = state.SerializeToString()
        packet = self.pack_data(Packet.USERSTATE, payload)
        self.transport.write(packet)

    # Parse mumble protocol packets
    def unpack_data(self, data):
        p_type, p_length = struct.unpack(">hi", data[:6])
        p_data = data[6:p_length+6]
        parsed = getattr(mumble_protobuf, PACKET_NAMES[p_type])()

        if p_type == Packet.UDPTUNNEL:
            parsed = self.parse_voicedata(p_data)
        else:
            parsed.ParseFromString(p_data)

        return p_type, parsed, data[p_length+6:]

    def parse_voicedata(self, data):
        p = VoicePacket()
        header, = struct.unpack(">B", data[0])
        p.type, p.target = header >> 5, header & 31
        p.session, data = parse_varint(data[1:])
        p.sequence, data = parse_varint(data)

        # Swap to enable saving voice packets
        # while data:
        while False:
            audio, = struct.unpack(">B", data[0])
            a_terminator, a_length = audio >> 7, audio & 127
            audio_data, data = data[1:a_length+1], data[a_length+1:]
            p.frames.append(audio_data)
            p.lengths.append(a_length)
            if a_terminator == 0:
                break

        return p

    # Handles various interactions
    def get_handlers(self):
        handlers = {
            1:  self.handle_udptunnel,
            7:  self.handle_channelstate,
            8:  self.handle_userremove,
            9:  self.handle_userstate,
            11: self.handle_textmessage
        }
        return handlers

    def handle_udptunnel(self, p):
        pass

    def handle_channelstate(self, p):
        pass

    def handle_userremove(self, p):
        pass

    def handle_userstate(self, p):
        pass

    def handle_textmessage(self, p):
        pass
