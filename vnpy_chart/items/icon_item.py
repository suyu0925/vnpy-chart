import os
from enum import Enum

import pyqtgraph as pg
from vnpy.trader.ui import QtCore, QtGui
from vnpy.trader.object import BarData

from ..base import BAR_WIDTH
from ..manager import BarManager
from .chart_item import ChartItem


MIN_ICON_SIZE = 12

ASSETS_FOLER = os.path.join(os.path.dirname(__file__), '../assets/')


class IconEnum(Enum):
    """
    枚举值为在assets下的文件名
    """
    SMILEY_FACE = 'smiley_face.png'


class IconItem(ChartItem):
    def __init__(self, manager: BarManager) -> None:
        super().__init__(manager)

        self._pixmaps = {}

    def be_added_to_parent(self):
        vb = self._get_client_viewbox()
        vb.sigXRangeChanged.connect(self.set_to_repaint)
        vb.sigYRangeChanged.connect(self.set_to_repaint)

    def viewTransformChanged(self):
        super().viewTransformChanged()
        self.set_to_repaint()
        self.update()

    def boundingRect(self) -> QtCore.QRectF:
        min_price, max_price = self._manager.get_price_range()
        rect: QtCore.QRectF = QtCore.QRectF(
            0,
            min_price,
            self._manager.get_count(),
            max_price - min_price
        )
        return rect

    def get_y_range(self, min_ix: int = None, max_ix: int = None) -> tuple[float, float]:
        min_price, max_price = self._manager.get_price_range(min_ix, max_ix)
        return min_price, max_price

    def get_info_text(self, ix: int) -> str:
        return ''

    def _draw_bar_picture(self, ix: int, bar: BarData) -> QtGui.QPicture:
        picture: QtGui.QPicture = QtGui.QPicture()
        painter: QtGui.QPainter = QtGui.QPainter(picture)

        icons: list[tuple[IconEnum, float]] = (
            bar.extra or {}).get('icons') or []
        if len(icons) > 0:
            for icon, y in icons:
                pixmap = self._get_pixmap(icon)
                ratio = self._get_aspect_ratio()
                client_ratio = self._get_client_aspect_ratio()
                w = self._get_icon_width()
                h = w / ratio * client_ratio
                rect: QtCore.QRectF = QtCore.QRectF(
                    ix - w/2,
                    y,
                    w,
                    h,
                )
                painter.drawPixmap(rect, pixmap, pixmap.rect())

        painter.end()
        return picture

    def set_to_repaint(self):
        self._to_repaint = True

    def _get_pixmap(self, icon: IconEnum) -> QtGui.QPixmap:
        if not icon.value in self._pixmaps:
            pixmap = QtGui.QPixmap(os.path.join(ASSETS_FOLER, icon.value))

            # 因为Y坐标系是越大越在上，所以要翻转图片
            transform = QtGui.QTransform()
            transform.scale(1, -1)
            transform.translate(0, -pixmap.height())
            pixmap = pixmap.transformed(transform)

            self._pixmaps[icon.value] = pixmap
        return self._pixmaps[icon.value]

    def _get_plot_item(self) -> pg.PlotItem:
        parent = self.parentItem()
        while parent is not None:
            if isinstance(parent, pg.PlotItem):
                return parent
            parent = parent.parentItem()
        raise Exception('IconItem is not in any PlotItem')

    def _get_client_viewbox(self) -> pg.ViewBox:
        parent = self.parentItem()
        while parent is not None:
            if isinstance(parent, pg.ViewBox):
                return parent
            parent = parent.parentItem()
        raise Exception('IconItem is not in any ViewBox')

    def _get_client_width(self) -> float:
        vb = self._get_client_viewbox()
        return vb.width()

    def _get_client_aspect_ratio(self) -> float:
        vb = self._get_client_viewbox()
        return vb.width() / vb.height()

    def _get_aspect_ratio(self) -> float:
        view_rect = self.viewRect()
        return view_rect.width() / view_rect.height()

    def _get_bar_count(self) -> int:
        plot_item = self._get_plot_item()
        vb = plot_item.getViewBox()
        xrange = vb.viewRange()[0]
        return xrange[1] - xrange[0]

    def _get_icon_width(self) -> float:
        client_width = self._get_client_width()
        bar_count = self._get_bar_count()
        if client_width / bar_count < MIN_ICON_SIZE:
            return MIN_ICON_SIZE / (client_width / bar_count)
        return 1
