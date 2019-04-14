import os.path
import sys

from twisted.application import internet, service
from twisted.python import log
from twisted.spread import pb

from icl0ud.push.dispatch import LoggingHandler, HexdumpHandler
from icl0ud.push.notification_sender import PushNotificationSender
from icl0ud.push.pushtoken_handler import PushTokenHandler
from icl0ud.push.intercept import InterceptServerFactory


SERVER_CERT_PATH = os.path.join(os.path.curdir,
                   '../certs/courier.push.apple.com/server.pem')
APPLE_CERT_CHAIN_PATH = os.path.join(os.path.curdir,
                                     '../certs/apple/apple-cert-chain.pem')
CLIENT_CERT_DIR = os.path.join(os.path.curdir, '../certs/device/')
CA_CERT_CHAIN_PATH = os.path.join(os.path.curdir,
                                  '../certs/entrust/entrust-roots.pem')

# log_file = open('data/error.log', 'a')
pushTokenHandler = PushTokenHandler()
pushNotificationSender = PushNotificationSender(pushTokenHandler)
DISPATCH_HANDLERS = [LoggingHandler(),
                     pushTokenHandler,
                     pushNotificationSender,
                     # HexdumpHandler(sys.stdout),
                     ]


APPLE_PUSH_IPS = (
        '1-courier.push.apple.com',
        '2-courier.push.apple.com',
        '3-courier.push.apple.com',
        '4-courier.push.apple.com')

factory = InterceptServerFactory(
    hosts=APPLE_PUSH_IPS,
    port=5223,
    serverCert=SERVER_CERT_PATH,
    clientCertDir=CLIENT_CERT_DIR,
    caCertChain=CA_CERT_CHAIN_PATH,
    serverChain=APPLE_CERT_CHAIN_PATH,
    dispatchHandlers=DISPATCH_HANDLERS,
)
contextFactory = factory.getServerContextFactory()

application = service.Application('i4d-push')
serviceCollection = service.IServiceCollection(application)
internet.SSLServer(5223, factory, contextFactory) \
                  .setServiceParent(serviceCollection)

internet.TCPServer(1234,
                   pb.PBServerFactory(pushNotificationSender),
                   interface='127.0.0.1') \
                  .setServiceParent(serviceCollection)
