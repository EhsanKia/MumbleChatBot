from twisted.python.rebuild import rebuild
import mumble_client as mc
import mumble_protocol as mp
import peebot


OWNER = "Ph0X"  # Your mumble nickname
SERVER_IP = "ip.example.com"  # Server IP
SERVER_PORT = 12345  # Server PORT
USERNAME = "PeeBot"  # Bot's name

# Use empty string for optional fields to remove
PASSWORD = "hunter2"  # Optional password
CERTIFICATE = "somefile.p12"  # Optional certificate


class PeeBotClient(mp.MumbleClient):
    def connectionMade(self):
        mp.MumbleClient.connectionMade(self)

        self.users = {}
        self.channels = {}
        self.session = 0
        self.channel = 0
        self.shutup = []
        self.follow = 0
        self.c_order = []

    def reload(self):
        rebuild(mp)
        rebuild(peebot)

    def reply(self, p, msg):
        if p.channel_id:
            self.send_textmessage(msg, channels=p.channel_id)
        else:
            self.send_textmessage(msg, users=[p.actor])

    def handle_udptunnel(self, p):
        if self.users[p.session] in self.shutup:
            self.move_user(self.shutup_channel, p.session)

    def handle_channelstate(self, p):
        if p.name:
            self.channels[p.channel_id] = p.name

    def handle_userremove(self, p):
        # Remove user from userlist
        del self.users[p.session]

    def handle_userstate(self, p):
        # Add user id to the userlist
        if p.name:
            self.users[p.session] = p.name

        # Stores own session id
        if p.name == self.factory.nickname:
            self.session = p.session

        if p.session == self.session:
            self.channel = p.channel_id

        # Follows user around
        if self.users[p.session] == self.follow:
            if p.channel_id:
                self.move_user(p.channel_id, self.session)
            elif p.self_mute:
                self.mute_or_deaf(self.session, True, True)
            else:
                self.mute_or_deaf(self.session, False, False)

    def handle_textmessage(self, p):
        # Only listen to the owner
        if self.users[p.actor] != OWNER:
            return

        # Reload the script
        if p.message == "/reload":
            self.reload()
            print "Reloaded!"

        # Moves user every time they talk
        elif p.message.startswith("/shutup"):
            name = p.message.split(' ')[-1]
            if name in self.users.values():
                self.shutup_channel = 18
                self.shutup.append(name)
            else:
                self.reply(p, "Invalid name")

        elif p.message.startswith("/stop"):
            self.shutup = []

        # Follows user around different channels (and mute)
        elif p.message.startswith("/follow"):
            name = p.message.split(' ')[-1]
            if name in self.users.values():
                self.follow = name
            else:
                self.reply(p, "Invalid name")

        elif p.message.startswith("/unfollow"):
            self.follow = 0

        # List the channels in the console
        elif p.message.startswith("/channels"):
            print self.channels

        # List the users in the console
        elif p.message.startswith("/users"):
            print self.users


if __name__ == '__main__':
    factory = mc.create_client(peebot.PeeBotClient, USERNAME, PASSWORD)
    mc.start_client(factory, SERVER_IP, SERVER_PORT, certificate=CERTIFICATE)
