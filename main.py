# -*- coding: utf-8 -*-
from ExWebsocket.binance_spot_websocket import BinanceSpotWebsocket
from ExWebsocket.bitoex_websocket import BitoExWebsocket
from ExWebsocket.bybit_spot_websocket import BybitSpotWebsocket
from d2tq_crypto_manager import ExchangeWebSocketManager
from twisted.internet import reactor
from tcp_server import TcpServerFactory 
import sys
import os

os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(os.path.dirname(sys.argv[0]), "cacert.pem")

if __name__ == "__main__":
    #host = "0.0.0.0"
    port = 2000
    # tcp_factory:TcpClientFactory = TcpClientFactory()
    # reactor.connectTCP(host, port, tcp_factory)

    server_factory = TcpServerFactory()
    manager = ExchangeWebSocketManager(server_factory)
    manager.add_ex_webscoket(BitoExWebsocket(0, "wss://stream.bitopro.com:9443/ws/v1/pub/trades/USDT_TWD,BTC_TWD,ETH_TWD,BTC_USDT,ETH_USDT"))
    manager.add_ex_webscoket(BitoExWebsocket(1, "wss://stream.bitopro.com:9443/ws/v1/pub/order-books?pairs=USDT_TWD:1,BTC_USDT:1,ETH_USDT,BTC_TWD:1,ETH_TWD:1"))
    manager.add_ex_webscoket(BinanceSpotWebsocket("wss://stream.binance.com:9443/ws"))
    manager.add_ex_webscoket(BybitSpotWebsocket("wss://stream.bybit.com/spot/public/v3"))
    manager.start()
    reactor.listenTCP(port, server_factory)
    reactor.run()