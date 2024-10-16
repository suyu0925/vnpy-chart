from .widget import ChartWidget
from .items import (
    CandleItem,
    VolumeItem,
    IconItem, IconEnum,
    LineItem, LineColor,
)


def mark_line(bar, line: tuple[str, float, LineColor] | tuple[str, float, LineColor, int]):
    if bar.extra is None:
        bar.extra = {}

    if not 'lines' in bar.extra:
        bar.extra['lines'] = []

    if len(line) == 3:
        line = (*line, None)
    bar.extra['lines'].append(line)


def mark_icon(bar, icon: tuple[IconEnum, float]):
    if bar.extra is None:
        bar.extra = {}

    if not 'icons' in bar.extra:
        bar.extra['icons'] = []

    bar.extra['icons'].append(icon)


__version__ = "0.0.3"
