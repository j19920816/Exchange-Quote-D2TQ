# -*- coding: utf-8 -*-
from  datetime import datetime
from loguru import logger
from ExWebsocket.ex_websocket import ExWebsocketBase
from threading import Timer
import json

class MaxExWebsocket(ExWebsocketBase):
    def __init__(self, endpoint: str, symbols: list):
        super().__init__(endpoint, symbols, self.__message_handler) 
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

        if self._tcp_factory.protocol != None:
            if json_message["event"] == "TRADE":
                pair = f"{json_message['pair'].replace('_', '')}.{self._exchange}"
                timestamp = json_message["data"][0]["timestamp"]
                time = datetime.fromtimestamp(timestamp)
                d2tq_time = (time.hour * 10000 + time.minute * 100 + time.second) * 100
                price = float(json_message["data"][0]["price"])
                volume = float(json_message["data"][0]["amount"])
                packet = self._d2tq_packet.make_tick_stream(pair, d2tq_time, price, volume, timestamp)
                try:
                    self._tcp_factory.Broadcast(packet)
                except Exception as err:
                    info = f"{self._exchange} execute trade error: {err}"
                    logger.Debug(info)

    def quote_to_D2tq_tick(self, message:str)->None:
        json_message = json.loads(message)
        try:
            if self._tcp_factory.protocol != None:
                if json_message["event"] == "ORDER_BOOK":
                    pair = f"{json_message['pair'].replace('_', '')}.{self._exchange}"
                    timestamp = json_message["timestamp"] / 1000
                    time = datetime.fromtimestamp(timestamp)
                    d2tq_time = (time.hour * 10000 + time.minute * 100 + time.second) * 100
                    bid = json_message["bids"][0]
                    ask = json_message["asks"][0]
                    bid_price = float(bid["price"])
                    bid_amount = float(bid["amount"])
                    ask_price = float(ask["price"])
                    ask_amount = float(ask["amount"])
                    packet = self._d2tq_packet.make_memory_stream(pair, d2tq_time, 0, 0, 0, 0, 0, bid_price, ask_price, 0, bid_amount, ask_amount, timestamp)
                    self._tcp_factory.Broadcast(packet)
        except Exception as err:
            info = f"{self._exchange} execute quote error: {err}"
            logger.Debug(info)