from twisted.internet import ssl, reactor, protocol


class MumbleClientFactory(protocol.ClientFactory):
    protocol = None

    def __init__(self, protocol, nickname, password):
        self.nickname = nickname
        self.password = password
        self.protocol = protocol

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed"
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection lost"
        reactor.stop()


def load_certificate(cert_file):
    from OpenSSL import crypto, SSL
    p12 = crypto.load_pkcs12(file(cert_file, 'rb').read())

    class CtxFactory(ssl.ClientContextFactory):
        def getContext(self):
            self.method = SSL.SSLv23_METHOD
            ctx = ssl.ClientContextFactory.getContext(self)
            ctx.use_certificate(p12.get_certificate())
            ctx.use_privatekey(p12.get_privatekey())
            return ctx

    return CtxFactory


def create_client(protocol, user, pw=""):
    return MumbleClientFactory(protocol, user, pw)


def start_client(factory, ip, port, certificate=None):
    # Loads certificate if available
    if certificate:
        ctx = load_certificate(certificate)
    else:
        ctx = ssl.ClientContextFactory

    reactor.connectSSL(ip, port, factory, ctx())
    reactor.run()
