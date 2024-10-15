import unittest
import sys

from vnpy_chart import ChartWidget, CandleItem, VolumeItem
from PySide6.QtWidgets import QApplication
from tests.data import get_test_bars

HANG_UP = True

app = QApplication(sys.argv)

class TestWidget(unittest.TestCase):
    def setUp(self):
        self.widget = ChartWidget()
        self.widget.add_plot('candle', hide_x_axis=True)
        self.widget.add_plot('volume', maximum_height=250)
        self.widget.add_item(CandleItem, "candle", "candle")
        self.widget.add_item(VolumeItem, "volume", "volume")        
        self.widget.add_cursor()
        self.widget.update_history(get_test_bars())
        self.widget.showMaximized()

        if HANG_UP:
            app.exec()

    def tearDown(self):
        # self.widget.close()
        pass

    def testSomething(self):
        pass


if __name__ == '__main__':
    unittest.main()
