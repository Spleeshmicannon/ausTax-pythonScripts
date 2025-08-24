#!/bin/python3

import csv
import argparse
from collections import deque

class Trade:
    __slots__ = ("stockType_", "units_", "isBuy_", "value_", "_frozen")

    def __init__(self, stockType:str, units:float, isBuy:bool, value:float):
        object.__setattr__(self, "stockType_", stockType)
        object.__setattr__(self, "units_", units)
        object.__setattr__(self, "isBuy_", isBuy)
        object.__setattr__(self, "value_", value)
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name:str, value):
        if getattr(self, "_frozen", False):
            raise AttributeError(f"{self.__class__.__name__} is immutable")
        object.__setattr__(self, name, value)

    def __str__(self) -> str:
        side = "Buy" if self.isBuy_ else "Sell"
        return f"Trade(stockType={self.stockType_}, units={self.units_}, side={side}, value={self.value_})"

def find_col(key:str, heading:list[str]) -> int|None:
    for index, x in enumerate(heading):
        if key in x:
            return index

def lex_csv(filename:str) -> list[Trade]:
    if None == filename:
        print("Failed to read file, filename = None")
        return [] 
    
    try:
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            
            heading = next(reader)
            stockSymbolCol = find_col("Symbol", heading)
            totalValueCol = find_col("Total Value", heading)
            sideCol = find_col("Side" ,heading)
            unitsCol = find_col("Units", heading)

            if stockSymbolCol is None:
                print("Failed to find stockSymbolCol")
                return []
            elif totalValueCol is None:
                print("Failed to find totalValueCol")
                return []
            elif sideCol is None:
                print("Failed to find sideCol")
                return []
            elif unitsCol is None:
                print("Failed to find unitsCol")
                return []
            
            tradeList:list[Trade] = []
            for row in reader:
                isBuy:bool|None = None
                value:float = float(row[totalValueCol])
                symbol:str = row[stockSymbolCol]
                units:float = abs(float(row[unitsCol]))

                if "Buy" in row[sideCol]:
                    isBuy = True
                elif "Sell" in row[sideCol]:
                    isBuy = False
                else:
                    print("error finding side")
                    return []

                tradeList.append(Trade(symbol, units, isBuy, value))

            return tradeList


    except FileNotFoundError:
        print("Failed to read file, file not found")
    except StopIteration:
        print("Failed to read file, file empty")
    except ValueError:
        print("Failed to parse data from csv field")

    return []

def calculate_capital_gains(trades:list[Trade]) -> tuple[float, float]:
    # stock -> deque of (units, price per unit)
    holdings: dict[str, deque[tuple[float,float]]] = {}
    total_gains = 0.0
    net_gains = 0.0

    for trade in trades:
        symbol = trade.stockType_
        if symbol not in holdings:
            holdings[symbol] = deque()

        if trade.isBuy_: # tracking holdings on buys
            price_per_unit = round(trade.value_ / trade.units_, 2)
            holdings[symbol].append((trade.units_, price_per_unit))
        else: # calculating gains on sell
            units_to_sell = trade.units_
            sell_price_per_unit = round(trade.value_ / trade.units_, 2)

            while units_to_sell > 0 and holdings[symbol]:
                buy_units, buy_price_per_unit = holdings[symbol][0]

                if buy_units <= units_to_sell:
                    gain = round((sell_price_per_unit - buy_price_per_unit) * buy_units, 2)
                    net_gains += gain
                    if gain >= 0:
                        total_gains += gain

                    units_to_sell -= buy_units
                    holdings[symbol].popleft()
                else:
                    gain = round((sell_price_per_unit - buy_price_per_unit) * units_to_sell, 2)
                    net_gains += gain
                    if gain >= 0:
                        total_gains += gain

                    holdings[symbol][0] = (buy_units - units_to_sell, buy_price_per_unit)
                    units_to_sell = 0

    return round(net_gains, 2), round(total_gains, 2)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        prog="Stake - Captial Gains Calculator",
        description="calculates your capital gains based on a stake tax csv")

    argparser.add_argument('filename')

    args = argparser.parse_args()

    net, total = calculate_capital_gains(lex_csv(args.filename))

    print("Net Capital Gains is: ", net)
    print("Total Capital Gains is: ", total)



