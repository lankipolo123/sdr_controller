from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter


class ActivityChart(QChartView):
    """Live line graph of bytes-per-message for TX/RX, one point per event."""

    def __init__(self, parent=None):
        chart = QChart()
        chart.setTitle("Communication Activity (bytes per message)")
        chart.legend().setVisible(True)

        self.tx_series = QLineSeries()
        self.tx_series.setName("TX")
        self.rx_series = QLineSeries()
        self.rx_series.setName("RX")
        chart.addSeries(self.tx_series)
        chart.addSeries(self.rx_series)

        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("Message #")
        self.axis_x.setLabelFormat("%d")
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Bytes")
        self.axis_y.setLabelFormat("%d")
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

    def _rescale(self, latest_len: int):
        self._max_bytes = max(self._max_bytes, latest_len)
        self.axis_x.setRange(0, max(self._tx_count, self._rx_count, 1))
        self.axis_y.setRange(0, self._max_bytes + 2)
