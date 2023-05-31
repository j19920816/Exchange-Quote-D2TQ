# -*- coding: utf-8 -*-
from enum import Enum

class D2TQHeader(Enum):
    Memory = "00_ID"
    Tick = "01_ID"
    ServerHeartbeat = "02_ServerDate"

# Define function to fetch remote data # demonstartion only #
class D2TQPacket(object):
    def __init__(self) -> None:
        self.__tick_count:dict = {} 
        self.__quote_count:dict = {} 

    def make_memory_stream(self, symbol:str, time:int, open:float, high:float, low:float, close:float, volume: float, bid:float, ask:float, pre_close:float, bid_size:float, ask_size: float, epoch:int)->str:
        if symbol in self.__quote_count:
            self.__quote_count[symbol] += 1
        else:
            self.__quote_count[symbol] = 1
        result = D2TQHeader.Memory.value + "=" + symbol + ","
        result += f"TickCount={self.__quote_count[symbol]},"
        result += f"Time={time},"
        if open > 0 and high > 0 and low > 0 and close and volume > 0:
            result += f"O={open},"
            result += f"H={high},"
            result += f"L={low},"
            result += f"C={close},"
            result += f"V={volume},"
        result += f"Bid={bid},"
        result += f"Ask={ask},"
        if pre_close > 0:
            result += f"PC={pre_close},"
        result += f"BSz={bid_size},"
        result += f"ASz={ask_size},"
        result += f"EPID={epoch},"
        result += f"\r\n"
        return result

    def make_tick_stream(self, symbol:str, time:int, close:float, volume: float, epoch:int)->str:        
        if symbol in self.__tick_count:
            self.__tick_count[symbol] += 1
        else:
            self.__tick_count[symbol] = 1
        
        result = D2TQHeader.Tick.value + "=" + symbol + ","
        result += f"Time={time},"
        result += f"C={close},"
        result += f"V={volume},"
        result += f"TC={self.__tick_count[symbol]},"
        result += f"EPID={epoch},"
        result += f"\r\n"
        return result

    def make_server_heartbeat_stream(self, server_date:int, server_time:int, epoch:int)->str:
        result = D2TQHeader.ServerHeartbeat.value + "=" + server_date + ","
        result += f"ServerTime={server_time},"
        result += f"EPID={epoch},"
        result += f"\r\n"
        return result