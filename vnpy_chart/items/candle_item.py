from typing import Tuple

from vnpy.trader.ui import QtCore, QtGui
from vnpy.trader.object import BarData

from ..base import BAR_WIDTH
from ..manager import BarManager
from .utils import format_decimal
from .chart_item import ChartItem


class CandleItem(ChartItem):
    def __init__(self, manager: BarManager) -> None:
        super().__init__(manager)

    def _draw_bar_picture(self, ix: int, bar: BarData) -> QtGui.QPicture:
        # Create objects
        candle_picture: QtGui.QPicture = QtGui.QPicture()
        painter: QtGui.QPainter = QtGui.QPainter(candle_picture)

        # Set painter color
        if bar.close_price >= bar.open_price:
            painter.setPen(self._up_pen)
            painter.setBrush(self._black_brush)
        else:
            painter.setPen(self._down_pen)
            painter.setBrush(self._down_brush)

        # Draw candle shadow
        if bar.high_price > bar.low_price:
            painter.drawLine(
                QtCore.QPointF(ix, bar.high_price),
                QtCore.QPointF(ix, bar.low_price)
            )

        # Draw candle body
        if bar.open_price == bar.close_price:
            painter.drawLine(
                QtCore.QPointF(ix - BAR_WIDTH, bar.open_price),
                QtCore.QPointF(ix + BAR_WIDTH, bar.open_price),
            )
        else:
            rect: QtCore.QRectF = QtCore.QRectF(
                ix - BAR_WIDTH,
                bar.open_price,
                BAR_WIDTH * 2,
                bar.close_price - bar.open_price
            )
            painter.drawRect(rect)

        # Finish
        painter.end()
        return candle_picture

    def boundingRect(self) -> QtCore.QRectF:
        min_price, max_price = self._manager.get_price_range()
        rect: QtCore.QRectF = QtCore.QRectF(
            0,
            min_price,
            len(self._bar_pictures),
            max_price - min_price
        )
        return rect

    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> Tuple[float, float]:
        min_price, max_price = self._manager.get_price_range(min_ix, max_ix)
        return min_price, max_price

    def get_info_text(self, ix: int) -> str:
        bar: BarData = self._manager.get_bar(ix)
        if not bar:
            return ''

        words: list = [
            "Date",
            bar.datetime.strftime("%Y-%m-%d"),
            "",
            "Time",
            bar.datetime.strftime("%H:%M"),
            "",
            "Open",
            format_decimal(bar.open_price),
            "",
            "High",
            format_decimal(bar.high_price),
            "",
            "Low",
            format_decimal(bar.low_price),
            "",
            "Close",
            format_decimal(bar.close_price)
        ]
        text: str = "\n".join(words)
        return text
