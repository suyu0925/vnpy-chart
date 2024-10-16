import os
from enum import Enum

import pyqtgraph as pg
from vnpy.trader.ui import QtCore, QtGui
from vnpy.trader.object import BarData

from ..manager import BarManager
from .chart_item import ChartItem
from .utils import format_decimal


class LineColor(Enum):
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)


LineType = tuple[str, float, LineColor, int | None]


class LineItem(ChartItem):
    def __init__(self, manager: BarManager) -> None:
        super().__init__(manager)

        self.pens: dict[str, QtGui.QPen] = {}

    def boundingRect(self) -> QtCore.QRectF:
        min_price, max_price = self._manager.get_price_range()
        rect: QtCore.QRectF = QtCore.QRectF(
            0,
            min_price,
            len(self._bar_pictures),
            max_price - min_price
        )
        return rect

    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> tuple[float, float]:
        min_price, max_price = self._manager.get_price_range(min_ix, max_ix)
        return min_price, max_price

    def get_info_text(self, ix: int) -> str:
        bar: BarData = self._manager.get_bar(ix)
        if not bar:
            return ''

        lines: list[LineType] = (bar.extra or {}).get('lines') or []
        text: str = ''
        for idx, (label, y, color, width) in enumerate(lines):
            text += '\n' if idx > 0 else ''
            text += f"{label}: {format_decimal(y)}"
        return text

    def _draw_bar_picture(self, ix: int, bar: BarData) -> QtGui.QPicture:
        picture: QtGui.QPicture = QtGui.QPicture()
        painter: QtGui.QPainter = QtGui.QPainter(picture)

        lines: list[LineType] = (bar.extra or {}).get('lines') or []
        if len(lines) > 0:
            for label, y, color, width in lines:
                previous_value = self.get_line_value(ix-1, label)
                value = self.get_line_value(ix, label)

                if value is not None and previous_value is not None:
                    painter.setPen(self.get_pen(color, width=width))
                    start_point = QtCore.QPointF(ix-1, previous_value)
                    end_point = QtCore.QPointF(ix, value)
                    painter.drawLine(start_point, end_point)

        painter.end()
        return picture

    def get_pen(self, color: LineColor, **kwg) -> QtGui.QPen:
        width = kwg.get('width') or 1
        key = f'{color.name}_{width}'
        if not key in self.pens:
            self.pens[key] = pg.mkPen(color=color.value, width=width)
        return self.pens[key]

    def get_line_value(self, ix: int, label: str) -> float:
        if ix < 0:
            return None
        bar = self._manager.get_bar(ix)
        lines: list[LineType] = (bar.extra or {}).get('lines') or []
        for _label, y, color, width in lines:
            if _label == label:
                return y
