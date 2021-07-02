import logging
from candlesticks_indicator.CandlestickIndicators import CandlestickChartIndicator
from candlesticks_indicator.CandlestickIndicators import MA
from candlesticks_indicator.CandlestickIndicators import EMA
from candlesticks_indicator.CandlestickIndicators import MACD
from candlesticks_indicator.CandlestickIndicators import BollingerBands
from candlesticks_indicator.CandlestickIndicators import TraceCandlesException
from candlesticks_indicator.CandlestickIndicators import PlottingExeception

log = logging.getLogger("candlestick-chart-builder")


class CandlestickIndicatorBuilder():
	"""
		Implementa um criador de Indicadores (Builder Pattern)
		https://en.wikipedia.org/wiki/Builder_pattern.
	"""
	def __init__(self, data, ticker, rangeslider=False):
		self.data_frame = pd.DataFrame((c for c in data))
		self.tiker = tiker
		self.data = []
		self.rangeslider = rangeslider
		self._initialize_candles()

	def _initialize_candles(self):
		try:
			self.data_frame['from'] = pd.to_datetime(self.data_frame['from'], unit='s')
			self.data_frame['to']   = pd.to_datetime(self.data_frame['to'], unit='s')
			self.data_frame = self.data_frame.set_index(pd.DatetimeIndex(self.data_frame['to'].values))

			trace_candles = go.Candlestick(
			      x     = self.data_frame.index,
			      open  = self.data_frame['open'],
			      high  = self.data_frame['max'],
			      low   = self.data_frame['min'],
			      close = self.data_frame['close'],
			      name  = self.self.tiker
			)
			self.data.append(trace_candles)
		except TraceCandlesException as e:
			raise ChartIndicatorException(f"Unexpected error while trace candles: {e}")

	def create(self, **kwargs):
		"""
		Implementa um criador de indicadores (Builder Pattern)
		"""
		try:
			data = self.data

			a = MA()
			data = a.indicate(data, self.data_frame, **kwargs)

			b = EMA()
			data = b.indicate(data, self.data_frame, **kwargs)

			c = CrossingMovingAvarege()
			data = c.indicate(data, self.data_frame, **kwargs)

			d = MACD()
			data = d.indicate(data, self.data_frame, **kwargs)

			e = BollingerBands()
			data = d.indicate(data, self.data_frame, **kwargs)

			fig = go.Figure(dict(data=data))
			fig.update_layout(xaxis_rangeslider_visible=self.rangeslider)
			fig.show()

		except PlottingExeception as e:
			log.error(f"error when trying to implement candlestick graphics {e}")
		except TraceCandlesException as e:
			raise TraceCandlesException(e)

# end-of-file