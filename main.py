# -*- coding: utf-8 -*-
from ExWebsocket.binance_spot_websocket import BinanceSpotWebsocket
from ExWebsocket.bitoex_websocket import BitoExWebsocket, StreamType
from ExWebsocket.bybit_spot_websocket import BybitSpotWebsocket
from ExWebsocket.max_websocket import MaxExWebsocket
from configuration import Config
from d2tq_crypto_manager import ExchangeWebSocketManager
from twisted.internet import reactor
from tcp_server import TcpServerFactory 
import sys
import os

os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(os.path.dirname(sys.argv[0]), "cacert.pem")

if __name__ == "__main__":
    config = Config("config.ini")

    #host = "0.0.0.0"
    port = 2000
    # tcp_factory:TcpClientFactory = TcpClientFactory()
    # reactor.connectTCP(host, port, tcp_factory)

    server_factory = TcpServerFactory()
    manager = ExchangeWebSocketManager(server_factory)
    manager.add_ex_webscoket(BitoExWebsocket(StreamType.Trade, "wss://stream.bitopro.com:9443/ws/v1/pub/trades/", config.subscribe_symbols))
    manager.add_ex_webscoket(BitoExWebsocket(StreamType.Quote, "wss://stream.bitopro.com:9443/ws/v1/pub/order-books?pairs=", config.subscribe_symbols))
    manager.add_ex_webscoket(BinanceSpotWebsocket("wss://stream.binance.com:9443/ws", config.subscribe_symbols))
    manager.add_ex_webscoket(BybitSpotWebsocket("wss://stream.bybit.com/spot/public/v3", config.subscribe_symbols))
    manager.add_ex_webscoket(MaxExWebsocket("wss://max-stream.maicoin.com/ws", config.subscribe_symbols))
    manager.start()
    reactor.listenTCP(port, server_factory)
    reactor.run()