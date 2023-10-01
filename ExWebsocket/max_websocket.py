# -*- coding: utf-8 -*-
from  datetime import datetime
from loguru import logger
import requests
from ExWebsocket.ex_websocket import ExWebsocketBase
from threading import Timer
import json

class MaxExWebsocket(ExWebsocketBase):
    def __init__(self, endpoint: str, symbols: list):
        super().__init__(endpoint, self.__message_handler) 
        self._exchange = "MAX"
        self.timers:Timer = None
        methods:list = []
        
        response = requests.get("https://max-api.maicoin.com/api/v2/markets")
        if response.status_code != requests.codes.ok:
            logger.error(f"Cannot get {self._exchange} pair info")
            return
        max_symbols = json.loads(response.text)

        for symbol in symbols:
            sub_symbol = symbol.lower().replace("_","")
            if len([obj for obj in max_symbols if obj["id"] == sub_symbol]) > 0:
                methods.append({"channel": "book","market": sub_symbol,"depth": 1})
                methods.append({"channel": "trade","market": sub_symbol})
            
        self._send_opening_message = json.dumps({"action": "sub","subscriptions": methods,"id": "client1"})
        self._set_websocket()

        self._ask:list = []
        self._bid:list = []

    def __message_handler(self, message:str)->None:
        try:
            json_message = json.loads(message)
            if "c" in json_message:
                if json_message["c"] == "book" and "e" in json_message:
                    timestamp = int(json_message["T"])
                    time_now = datetime.fromtimestamp(timestamp/1000)
                    d2tq_time = (time_now.hour * 10000 + time_now.minute * 100 + time_now.second) * 100
                    pair = f"{json_message['M']}.{self._exchange}"
                    if json_message["e"] == "snapshot":
                        self._ask = json_message["a"]
                        self._bid = json_message["b"]
                    else:
                        if len(json_message["a"]) > 0:
                            self._ask = json_message["a"]
                        if len(json_message["b"]) > 0:
                            self._bid = json_message["b"]    
                    ask_price = float(self._ask[0][0])
                    ask_amount = float(self._ask[0][1])
                    bid_price = float(self._bid[0][0])
                    bid_amount = float(self._bid[0][1])
                    packet = self._d2tq_packet.make_memory_stream(pair, d2tq_time, 0, 0, 0, 0, 0, bid_price, ask_price, 0, bid_amount, ask_amount, timestamp)
                    self._tcp_factory.Broadcast(packet)
                elif json_message["c"] == "trade":
                    pair = f"{json_message['M']}.{self._exchange}"
                    timestamp = int(json_message["t"][0]["T"]/1000)
                    trade_time = datetime.fromtimestamp(timestamp)
                    d2tq_time = (trade_time.hour * 10000 + trade_time.minute * 100 + trade_time.second) * 100
                    price = float(json_message["t"][0]["p"])
                    volume = float(json_message["t"][0]["v"])
                    packet = self._d2tq_packet.make_tick_stream(pair, d2tq_time, price, volume, json_message["T"])
                    self._tcp_factory.Broadcast(packet)
        except Exception as err:
            info = f"{self._exchange} execute error: {err}"
            logger.Debug(info)
