# -*- coding: utf-8 -*-
from  datetime import datetime
from loguru import logger
from ExWebsocket.ex_websocket import ExWebsocketBase
from threading import Timer
import json

class MaxExWebsocket(ExWebsocketBase):
    def __init__(self, endpoint: str, symbols: list):
        super().__init__(endpoint, self.__message_handler) 
        self._exchange = "MAX"
        self.timers:Timer = None
        methods:list = []

        for symbol in symbols:
            methods.append({"channel": "book","market": symbol.lower().replace("_",""),"depth": 1})
            methods.append({"channel": "trade","market": symbol.lower().replace("_","")})
            
        self._send_opening_message = json.dumps({"action": "sub","subscriptions": methods,"id": "client1"})
        self._set_websocket()

    def __message_handler(self, message:str)->None:
        json_message = json.loads(message)
