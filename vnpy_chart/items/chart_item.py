from abc import abstractmethod
from typing import List, Dict, Tuple

import pyqtgraph as pg
from vnpy.trader.ui import QtCore, QtGui, QtWidgets
from vnpy.trader.object import BarData

from ..base import BLACK_COLOR, UP_COLOR, DOWN_COLOR, PEN_WIDTH
from ..manager import BarManager


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
        self._to_repaint: bool = False

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

    def be_added_to_parent(self):
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

            if bar_picture is None or self._to_repaint:
                bar: BarData = self._manager.get_bar(ix)
                bar_picture = self._draw_bar_picture(ix, bar)
                self._bar_pictures[ix] = bar_picture

            bar_picture.play(painter)

        self._to_repaint = False

        painter.end()

    def clear_all(self) -> None:
        """
        Clear all data in the item.
        """
        self._item_picture = None
        self._bar_pictures.clear()
        self.update()
