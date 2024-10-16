from vnpy.trader.object import BarData
from vnpy_chart import IconEnum, LineColor, mark_line, mark_icon
import numpy as np
import pandas as pd


def MA(s: np.ndarray, n: int) -> np.ndarray:
    """
    求序列的n日简单移动平均值, 返回序列
    """
    return pd.Series(s).rolling(n).mean().values


def CROSS(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    上穿。
    """
    return np.concatenate(([False], (a <= b)[:-1] & (a > b)[1:]))


class ArrayManager(object):
    def __init__(self, size: int = 100):
        self.count: int = 0
        self.size: int = size
        self.inited: bool = False

        self.close_array: np.ndarray = np.zeros(size)

    def update_bar(self, bar: BarData) -> None:
        self.count += 1
        if not self.inited and self.count >= self.size:
            self.inited = True

        self.close_array[:-1] = self.close_array[1:]

        self.close_array[-1] = bar.close_price

    @property
    def close(self) -> np.ndarray:
        return self.close_array


def add_smiley_face_to_gloden_cross(bars: list[BarData]) -> list[BarData]:
    """
    如果5日均线上穿20日均线, 就在BarData.extra中增加笑脸标记
    """
    am = ArrayManager(21)
    for bar in bars:
        am.update_bar(bar)
        if not am.inited:
            continue

        ma5 = MA(am.close, 5)
        ma20 = MA(am.close, 20)

        mark_line(bar, ('ma5', ma5[-1], LineColor.YELLOW, 1))
        mark_line(bar, ('ma20', ma20[-1], LineColor.GREEN))

        if (CROSS(ma5, ma20)[-1]):
            if not 'icons' in bar.extra:
                bar.extra['icons'] = []

            mark_icon(bar, (IconEnum.SMILEY_FACE, ma5[-1]))

    return bars
