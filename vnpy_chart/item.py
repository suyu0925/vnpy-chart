from abc import abstractmethod
from typing import List, Dict, Tuple
import os
from enum import Enum

import pyqtgraph as pg

from vnpy.trader.ui import QtCore, QtGui, QtWidgets
from vnpy.trader.object import BarData

from .base import BLACK_COLOR, UP_COLOR, DOWN_COLOR, PEN_WIDTH, BAR_WIDTH
from .manager import BarManager


def format_decimal(number, decimal_places=2):
    formatted_number = f'{number:.{decimal_places}f}'
    if formatted_number.endswith('0' * decimal_places):
        return str(int(number))
    return formatted_number


class ChartItem(pg.GraphicsObject):
    """"""

    def __init__(self, manager: BarManager) -> None:
        """"""
        super().__init__()

        self._manager: BarManager = manager

        self._bar_pictures: Dict[int, QtGui.QPicture] = {}
        self._item_picture: QtGui.QPicture = None

        self._black_brush: QtGui.QBrush = pg.mkBrush(color=BLACK_COLOR)

        self._up_pen: QtGui.QPen = pg.mkPen(
            color=UP_COLOR, width=PEN_WIDTH
        )
        self._up_brush: QtGui.QBrush = pg.mkBrush(color=UP_COLOR)

        self._down_pen: QtGui.QPen = pg.mkPen(
            color=DOWN_COLOR, width=PEN_WIDTH
        )
        self._down_brush: QtGui.QBrush = pg.mkBrush(color=DOWN_COLOR)

        self._rect_area: Tuple[float, float] = None

        # Very important! Only redraw the visible part and improve speed a lot.
        self.setFlag(self.GraphicsItemFlag.ItemUsesExtendedStyleOption)

        # Force update during the next paint
        self._to_update: bool = False

    @abstractmethod
    def _draw_bar_picture(self, ix: int, bar: BarData) -> QtGui.QPicture:
        """
        Draw picture for specific bar.
        """
        pass

    @abstractmethod
    def boundingRect(self) -> QtCore.QRectF:
        """
        Get bounding rectangles for item.
        """
        pass

    @abstractmethod
    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> Tuple[float, float]:
        """
        Get range of y-axis with given x-axis range.

        If min_ix and max_ix not specified, then return range with whole data set.
        """
        pass

    @abstractmethod
    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        pass

    def update_history(self, history: List[BarData]) -> None:
        """
        Update a list of bar data.
        """
        self._bar_pictures.clear()

        bars: List[BarData] = self._manager.get_all_bars()
        for ix, bar in enumerate(bars):
            self._bar_pictures[ix] = None

        self.update()

    def update_bar(self, bar: BarData) -> None:
        """
        Update single bar data.
        """
        ix: int = self._manager.get_index(bar.datetime)

        self._bar_pictures[ix] = None

        self.update()

    def update(self) -> None:
        """
        Refresh the item.
        """
        if self.scene():
            self._to_update = True
            self.scene().update()

    def paint(
        self,
        painter: QtGui.QPainter,
        opt: QtWidgets.QStyleOptionGraphicsItem,
        w: QtWidgets.QWidget
    ) -> None:
        """
        Reimplement the paint method of parent class.

        This function is called by external QGraphicsView.
        """
        rect = opt.exposedRect

        min_ix: int = int(rect.left())
        max_ix: int = int(rect.right())
        max_ix: int = min(max_ix, len(self._bar_pictures))

        rect_area: tuple = (min_ix, max_ix)
        if (
            self._to_update
            or rect_area != self._rect_area
            or not self._item_picture
        ):
            self._to_update = False
            self._rect_area = rect_area
            self._draw_item_picture(min_ix, max_ix)

        self._item_picture.play(painter)

    def _draw_item_picture(self, min_ix: int, max_ix: int) -> None:
        """
        Draw the picture of item in specific range.
        """
        self._item_picture = QtGui.QPicture()
        painter: QtGui.QPainter = QtGui.QPainter(self._item_picture)

        for ix in range(min_ix, max_ix):
            bar_picture: QtGui.QPicture = self._bar_pictures[ix]

            if bar_picture is None:
                bar: BarData = self._manager.get_bar(ix)
                bar_picture = self._draw_bar_picture(ix, bar)
                self._bar_pictures[ix] = bar_picture

            bar_picture.play(painter)

        painter.end()

    def clear_all(self) -> None:
        """
        Clear all data in the item.
        """
        self._item_picture = None
        self._bar_pictures.clear()
        self.update()


class CandleItem(ChartItem):
    """"""

    def __init__(self, manager: BarManager) -> None:
        """"""
        super().__init__(manager)

    def _draw_bar_picture(self, ix: int, bar: BarData) -> QtGui.QPicture:
        """"""
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
        """"""
        min_price, max_price = self._manager.get_price_range()
        rect: QtCore.QRectF = QtCore.QRectF(
            0,
            min_price,
            len(self._bar_pictures),
            max_price - min_price
        )
        return rect

    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> Tuple[float, float]:
        """
        Get range of y-axis with given x-axis range.

        If min_ix and max_ix not specified, then return range with whole data set.
        """
        min_price, max_price = self._manager.get_price_range(min_ix, max_ix)
        return min_price, max_price

    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        bar: BarData = self._manager.get_bar(ix)

        if bar:
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
        else:
            text: str = ""

        return text


class VolumeItem(ChartItem):
    """"""

    def __init__(self, manager: BarManager) -> None:
        """"""
        super().__init__(manager)

    def _draw_bar_picture(self, ix: int, bar: BarData) -> QtGui.QPicture:
        """"""
        # Create objects
        volume_picture: QtGui.QPicture = QtGui.QPicture()
        painter: QtGui.QPainter = QtGui.QPainter(volume_picture)

        # Set painter color
        if bar.close_price >= bar.open_price:
            painter.setPen(self._up_pen)
            painter.setBrush(self._up_brush)
        else:
            painter.setPen(self._down_pen)
            painter.setBrush(self._down_brush)

        # Draw volume body
        rect: QtCore.QRectF = QtCore.QRectF(
            ix - BAR_WIDTH,
            0,
            BAR_WIDTH * 2,
            bar.volume
        )
        painter.drawRect(rect)

        # Finish
        painter.end()
        return volume_picture

    def boundingRect(self) -> QtCore.QRectF:
        """"""
        min_volume, max_volume = self._manager.get_volume_range()
        rect: QtCore.QRectF = QtCore.QRectF(
            0,
            min_volume,
            len(self._bar_pictures),
            max_volume - min_volume
        )
        return rect

    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> Tuple[float, float]:
        """
        Get range of y-axis with given x-axis range.

        If min_ix and max_ix not specified, then return range with whole data set.
        """
        min_volume, max_volume = self._manager.get_volume_range(min_ix, max_ix)
        return min_volume, max_volume

    def get_info_text(self, ix: int) -> str:
        """
        Get information text to show by cursor.
        """
        bar: BarData = self._manager.get_bar(ix)

        if bar:
            text: str = f"Volume {bar.volume}"
        else:
            text: str = ""

        return text


class IconEnum(Enum):
    """
    枚举值为在assets下的文件名
    """
    SMILEY_FACE = 'smiley_face.png'


class IconItem(ChartItem):
    def __init__(self, manager: BarManager) -> None:
        super().__init__(manager)

        self._pixmaps = {}

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
        text: str = f"icon {ix}"

        return text

    def _draw_bar_picture(self, ix: int, bar: BarData) -> QtGui.QPicture:
        candle_picture: QtGui.QPicture = QtGui.QPicture()
        painter: QtGui.QPainter = QtGui.QPainter(candle_picture)

        icons = (bar.extra or {}).get('icons') or []
        if len(icons) > 0:
            for icon, y in icons:
                pixmap = self.get_pixmap(icon)
                ratio = self.getAspectRatio()
                client_ratio = self.getClientAspectRatio()
                w = 1
                h = w / ratio * client_ratio
                rect: QtCore.QRectF = QtCore.QRectF(
                    ix - w/2,
                    y,
                    w,
                    h,
                )
                painter.drawPixmap(rect, pixmap, pixmap.rect())

        painter.end()
        return candle_picture

    def get_pixmap(self, icon: IconEnum) -> QtGui.QPixmap:
        if not icon.value in self._pixmaps:
            pixmap = QtGui.QPixmap(os.path.join(
                os.path.dirname(__file__), f'./assets/{icon.value}'))

            # 因为Y坐标系是越大越在上，所以要翻转图片
            transform = QtGui.QTransform()
            transform.scale(1, -1)
            transform.translate(0, -pixmap.height())
            pixmap = pixmap.transformed(transform)

            self._pixmaps[icon.value] = pixmap
        return self._pixmaps[icon.value]

    def getClientAspectRatio(self) -> float:
        parent = self.parentItem()
        while parent is not None:
            if isinstance(parent, pg.ViewBox):
                return parent.width() / parent.height()
            parent = parent.parentItem()
        raise Exception('IconItem is not in any ViewBox')

    def getAspectRatio(self) -> float:
        view_rect = self.viewRect()
        return view_rect.width() / view_rect.height()
