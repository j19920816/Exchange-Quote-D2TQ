# -*- coding: utf-8 -*-
from enum import Enum
import threading
import threading
import websocket
import encodings.idna
from loguru import logger
from d2tq_stream import D2TQPacket
from tcp_server import TcpServerFactory

class StreamType(Enum):
    Trade = 0
    Quote = 1
    Other = 2

class ExWebsocketBase():
    def __init__(self, endpoint: str, callback):
        self._exchange:str=""
        self._send_opening_message:str=""
        self.__connect_endpoint: str = endpoint
        self.callback = callback
        self._d2tq_packet: D2TQPacket = D2TQPacket()

        self._ws: websocket.WebSocketApp = None
        self.wst: threading.Thread = None
        
    def set_socket(self, tcp_factory: TcpServerFactory):
        self._tcp_factory = tcp_factory
        
    def _set_websocket(self):
        self._ws = websocket.WebSocketApp(
            self.__connect_endpoint,
            on_open=self.__on_open,
            on_close=self.__on_close,
            on_message=self.__on_message,
            on_error=self.__on_error,
        )
        self.wst = threading.Thread(target=self._ws.run_forever)

    def __on_open(self, ws):
        if self._send_opening_message != "":
            ws.send(self._send_opening_message)
        logger.info(f"{self._exchange} connected")

    def __on_close(self, ws, close_status_code, msg):
        log_message = f"{self.__connect_endpoint} closed connection, reconnecting...\n"
        logger.info(f"{log_message}")
        self._set_websocket()
        self.wst.start()

    def __on_message(self, ws, message):
        self.callback(message)

    def __on_error(self, ws, error):
        logger.error(error)
