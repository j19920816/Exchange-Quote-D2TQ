# -*- coding: utf-8 -*-
import datetime
import time
from loguru import logger
from twisted.internet.protocol import Protocol, ClientFactory

class TcpClientFactory(ClientFactory):
    def buildProtocol(self, addr):
        print("Connected To Tcp Server", addr)
        self.protocol = TcpClient()
        return self.protocol

    def startedConnecting(self, connector):
        print("Starting Connecting To Tcp Server", (connector.host, connector.port))

    def clientConnectionLost(self, connector, reason):
        print("Lost Connection from Tcp Server", (connector.host, connector.port), 'Reason:', reason)
        time.sleep(3)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print("Failed To Connect To Tcp Server", (connector.host, connector.port), 'Reason:', reason)
        time.sleep(3)
        connector.connect()


class TcpClient(Protocol):
    ENCODING = "utf-8"
    SERVER_MAP = {}

    def connectionMade(self):
        addr = self.transport.addr  # get server connection state
        print("connected", self.transport.socket)
        client_ip = addr[0]
        TcpClient.SERVER_MAP[client_ip] = self
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        str = f"connected server: {nowTime}\r\n"
        self.send_datapacket(str)

    def connectionLost(self, reason):
        addr = self.transport.addr  # get server connection state
        client_ip = addr[0]
        if client_ip in TcpClient.SERVER_MAP:
            del TcpClient.SERVER_MAP[client_ip]

    def dataReceived(self, tcp_data):
        addr = self.transport.addr  # get server connection state
        try:
            msg = tcp_data.decode(TcpClient.ENCODING)
            print("Received msg", msg, "from Tcp Server", addr)
        except BaseException as e:
            err = "client error: " + e
            logger.Debug(err)

    def send_datapacket(self, tcp_data: str):
        self.transport.write(tcp_data.encode(TcpClient.ENCODING))
