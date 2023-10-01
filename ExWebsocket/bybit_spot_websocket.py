# -*- coding: utf-8 -*-
from  datetime import datetime
import json
from loguru import logger
from threading import Timer
import requests
from ExWebsocket.ex_websocket import ExWebsocketBase

class BybitSpotWebsocket(ExWebsocketBase):
    def __init__(self, endpoint: str, symbols: list):
        super().__init__(endpoint, self.__message_handler) 
        self._exchange = "Bybit"
        self.timers:Timer = None
        self.__set_timer()
        methods:list[str] = []

        response = requests.get("https://api.bybit.com/v5/market/instruments-info", params={"category":"spot"})
        if response.status_code != requests.codes.ok:
            logger.error(f"Cannot get {self._exchange} pair info")
            return
        
        bybit_symbols = json.loads(response.text)["result"]["list"]
        for symbol in symbols:
            sub_symbol = symbol.upper().replace("_","")
            sub_symbol = [obj for obj in bybit_symbols if obj["symbol"] == sub_symbol]
            if len(sub_symbol) > 0:
                methods.append(f"orderbook.40.{sub_symbol}")
                methods.append(f"trade.{sub_symbol}")
            
        self._send_opening_message = json.dumps({"op": "subscribe","args": methods,"req_id": "depth00001"})
        self._set_websocket()

    def __set_timer(self):
        self.timers = Timer(19.8, self.__send_heart_beat)
        self.timers.start()

    def __send_heart_beat(self):
        self._ws.send(json.dumps({"req_id": "100001", "op": "ping"}))
        self.__set_timer()

    def __message_handler(self, message:str):
        try:
            json_message = json.loads(message)
            if "topic" in json_message:
                if "orderbook" in json_message["topic"]:
                    data = json_message["data"]
                    pair = f"{data['s']}.{self._exchange}"
                    timestamp = data["t"] / 1000
                    time = datetime.fromtimestamp(timestamp)
                    d2tq_time = (time.hour * 10000 + time.minute * 100 + time.second) * 100
                    bid = data["b"]
                    ask = data["a"]
                    bid_price = float(bid[0][0])
                    bid_amount = float(bid[0][1])
                    ask_price = float(ask[0][0])
                    ask_amount = float(ask[0][1])
                    packet = self._d2tq_packet.make_memory_stream(pair, d2tq_time, 0, 0, 0, 0, 0, bid_price, ask_price, 0, bid_amount, ask_amount, timestamp)
                    self._tcp_factory.Broadcast(packet)
                elif "trade" in json_message["topic"]:
                    data = json_message["data"]
                    pair = json_message["topic"].split(".")[1] + "." + self._exchange
                    timestamp = data["t"] / 1000
                    time = datetime.fromtimestamp(timestamp)
                    d2tq_time = (time.hour * 10000 + time.minute * 100 + time.second) * 100
                    price = float(data["p"])
                    volume = float(data["q"])
                    packet = self._d2tq_packet.make_tick_stream(pair, d2tq_time, price, volume, timestamp)
                    self._tcp_factory.Broadcast(packet)
        except Exception as err:
            info = f"{self._exchange} execute error: {err}"
            logger.Debug(info)

