import math

from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen

from ..theme_colors import TX_ACCENT, RX_ACCENT


def _nice_tick_interval(span: float, target_ticks: int = 8) -> float:
    if span <= 0:
        return 1
    raw_step = span / target_ticks
    magnitude = 10 ** math.floor(math.log10(raw_step))
    for m in (1, 2, 5, 10):
        step = m * magnitude
        if step >= raw_step:
            return step
    return 10 * magnitude


class ActivityChart(QChartView):
    def __init__(self, parent=None):
        chart = QChart()
        chart.setTitle("Communication Activity (bytes per message)")
        chart.legend().setVisible(True)

        self.tx_series = QLineSeries()
        self.tx_series.setName("TX")
        self.tx_series.setPen(QPen(QColor(TX_ACCENT), 2))
        self.rx_series = QLineSeries()
        self.rx_series.setName("RX")
        self.rx_series.setPen(QPen(QColor(RX_ACCENT), 2))
        chart.addSeries(self.tx_series)
        chart.addSeries(self.rx_series)

        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("Message #")
        self.axis_x.setLabelFormat("%d")
        self.axis_x.setTickType(QValueAxis.TicksDynamic)
        self.axis_x.setTickInterval(1)
        self.axis_x.setRange(0, 10)
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Bytes")
        self.axis_y.setLabelFormat("%d")
        self.axis_y.setTickType(QValueAxis.TicksDynamic)
        self.axis_y.setTickInterval(2)
        self.axis_y.setRange(0, 10)
        chart.addAxis(self.axis_x, Qt.AlignBottom)
        chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.tx_series.attachAxis(self.axis_x)
        self.tx_series.attachAxis(self.axis_y)
        self.rx_series.attachAxis(self.axis_x)
        self.rx_series.attachAxis(self.axis_y)

        super().__init__(chart, parent)
        self.setRenderHint(QPainter.Antialiasing)

        self._tx_count = 0
        self._rx_count = 0
        self._max_bytes = 1

    def add_tx(self, data: bytes):
        self._tx_count += 1
        self.tx_series.append(self._tx_count, len(data))
        self._rescale(len(data))

    def add_rx(self, data: bytes):
        self._rx_count += 1
        self.rx_series.append(self._rx_count, len(data))
        self._rescale(len(data))

    def clear(self):
        self.tx_series.clear()
        self.rx_series.clear()
        self._tx_count = 0
        self._rx_count = 0
        self._max_bytes = 1
        self.axis_x.setRange(0, 10)
        self.axis_x.setTickInterval(1)
        self.axis_y.setRange(0, 10)
        self.axis_y.setTickInterval(2)

    def _rescale(self, latest_len: int):
        self._max_bytes = max(self._max_bytes, latest_len)

        x_max = max(self._tx_count, self._rx_count, 10)
        self.axis_x.setRange(0, x_max)
        self.axis_x.setTickInterval(_nice_tick_interval(x_max))

        y_max = self._max_bytes + 2
        self.axis_y.setRange(0, y_max)
        self.axis_y.setTickInterval(_nice_tick_interval(y_max))
