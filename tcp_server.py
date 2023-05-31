# -*- coding: utf-8 -*-
import datetime
from loguru import logger
from twisted.internet.protocol import Protocol, ServerFactory

class TcpServerFactory(ServerFactory):
    def __init__(self) -> None:
        super().__init__()
        self.clients = []  # keep client

    def buildProtocol(self, addr):
        self.protocol = TcpServer()
        self.protocol.factory = self
        self.clients.append(self.protocol)
        return self.protocol

    def Broadcast(self, data):
        for client in self.clients:
            client.send_data_packet(data)

class TcpServer(Protocol):
    ENCODING = "utf-8"
    def connectionMade(self):
        print("connected", self.transport.socket)
        
    def connectionLost(self, reason):
        addr = self.transport.client  # get client messege
        if self in self.factory.clients:
            print(addr, "Lost Connection from Tcp Server", 'Reason:', reason)
            i = self.factory.clients.index(self)
            del self.factory.clients[i]
 
    def dataReceived(self, tcp_data):
        try:
            msg = tcp_data.decode("utf-8")
            self.send_data_packet(f"From server: {msg}")
        except Exception as e:
            addr = self.transport.client  # get client messege
            nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            err = f"{nowTime} Comd Execute Error from {addr}, data:{tcp_data}, err:{e}"
            logger.Debug(err)
    
    def send_data_packet(self, tcp_data: str):
        self.transport.write(tcp_data.encode(TcpServer.ENCODING))
            