from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import get_database
import datetime
import pandas as pd


CSV_PATH = 'tests/test_data.csv'


def load_from_database():
    symbol = "SA00"
    exchange = Exchange.CZCE

    bars = get_database().load_bar_data(
        symbol=symbol,
        exchange=exchange,
        interval=Interval.DAILY,
        start=datetime.datetime(2023, 1, 1),
        end=datetime.datetime(2023, 12, 31)
    )
    return bars


def save_to_csv(bars: list[BarData]):
    df = pd.DataFrame(bars)
    df.to_csv(CSV_PATH, index=False)


def load_from_csv():
    def convert_dict_to_bar(bar: dict) -> BarData:
        del bar['extra']
        bar['exchange'] = getattr(Exchange, bar['exchange'].split('.')[1])
        bar['datetime'] = datetime.datetime.fromisoformat(bar['datetime'])
        bar['interval'] = getattr(Interval, bar['interval'].split('.')[1])
        return BarData(**bar)

    df = pd.read_csv(CSV_PATH)
    bars = [convert_dict_to_bar(row) for _, row in df.iterrows()]
    return bars


def get_test_bars() -> list[BarData]:
    return load_from_csv()
