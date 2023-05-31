# -*- coding: utf-8 -*-
from  datetime import datetime
import json

from loguru import logger
from ExWebsocket.ex_websocket import ExWebsocketBase

class BinanceSpotWebsocket(ExWebsocketBase):
    def __init__(self, endpoint: str):
        super().__init__(endpoint, self.__message_handler)
        self._exchange = "Binance"
        symbols = ["BTCUSDT", "ETHUSDT"]
        methods:list[str] = []
        self.__order_book:dict = {}

        for symbol in symbols:
            methods.append(symbol.lower() + "@trade")
            methods.append(symbol.lower() + "@bookTicker")
            self.__order_book[symbol] = {"lastUpdateId": 0, "bids": [], "asks": []}
            
        self._send_opening_message = json.dumps({"method": "SUBSCRIBE","params": methods,"id": 1})

        self._set_websocket()

    def __message_handler(self, message:str):
        try:
            json_message = json.loads(message)
            if "e" not in json_message and "s" in json_message:
                timestamp = int(datetime.now().timestamp())
                time_now = datetime.fromtimestamp(timestamp)
                d2tq_time = (time_now.hour * 10000 + time_now.minute * 100 + time_now.second) * 100
                pair = f"{json_message['s']}.{self._exchange}"
                bid_price = float(json_message["b"])
                bid_amount = float(json_message["B"])
                ask_price = float(json_message["a"])
                ask_amount = float(json_message["A"])
                packet = self._d2tq_packet.make_memory_stream(pair, d2tq_time, 0, 0, 0, 0, 0, bid_price, ask_price, 0, bid_amount, ask_amount, timestamp)
                self._tcp_factory.Broadcast(packet)
                
            elif "e" in json_message and json_message["e"] == "trade":
                pair = f"{json_message['s']}.{self._exchange}"
                timestamp = json_message["T"] / 1000
                trade_time = datetime.fromtimestamp(timestamp)
                d2tq_time = (trade_time.hour * 10000 + trade_time.minute * 100 + trade_time.second) * 100
                price = float(json_message["p"])
                volume = float(json_message["q"])
                packet = self._d2tq_packet.make_tick_stream(pair, d2tq_time, price, volume, json_message["T"])
                self._tcp_factory.Broadcast(packet)
        except Exception as err:
            info = f"{self._exchange} execute error: {err}"
            logger.Debug(info)
