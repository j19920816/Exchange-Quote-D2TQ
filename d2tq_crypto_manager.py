# -*- coding: utf-8 -*-
from ExWebsocket.ex_websocket import ExWebsocketBase
from twisted.internet.protocol import Factory


class ExchangeWebSocketManager(object):
    def __init__(self, tcp_factory:Factory) -> None:
        self.ex_websockets: list[ExWebsocketBase] = []
        self.__tcp_factory:tcp_factory = tcp_factory

    def add_ex_webscoket(self, ex: ExWebsocketBase):
        self.ex_websockets.append(ex)
        ex.set_socket(self.__tcp_factory)

    def start(self):
        for ex_websocket in self.ex_websockets:
            ex_websocket.wst.start()

        
