import logging
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


class ChartIndicatorException(Exception):
	pass


class PlottingExeception(ChartIndicatorException):
	pass


class TraceCandlesException(ChartIndicatorException):
	pass


class ErrorImplementingIndicator(ChartIndicatorException):
	pass


log = logging.getLogger("candlestick-chart-indicator")


class CandlestickChartIndicator(ABC):
	"""
	Base class responsible for the implementation of candlestick graphics, and their data.

	detail:
		This class implements a "Chain of Responsibility" design pattern.
		https://en.wikipedia.org/wiki/Chain-of-responsibility_pattern.
	"""
	@abc.abstractmethod
	def inicate(self):
		pass


class MA(CandlestickChartIndicator):
	"""
	Class responsible for implementing a simple Moving Average that stops
	filter out price fluctuations helping to identify trends.
	"""
	def indicate(self, data_frame, data=[], **kwargs):
		try:
			ma = data_frame['close'].rolling(window=kwargs.get("days", 21)).mean()
			trace_avg = go.Scatter(x=ma.index, y=MA, name='MA', line=dict(color='#BEBECF'), opacity=0.8)
			data.append(trace_avg)
		except (ErrorImplementingIndicator, TypeError) as e:
			log.warning(f"Error implementing 'ma' indicator: {e}")
		finally:
			return data


class EMA(CandlestickChartIndicator):
	"""
	Class responsible for implementing an exponential moving average
	EMA = Price today * K + EMA yesterday x (1-k) where K = 2 /(N+1)
	"""
	def indicate(self, data_frame, data=[], **kwargs):
		try:
			k = (2 / (kwargs.get("days", 21) + 1))
			ma = data_frame['close'].rolling(window=kwargs.get("days", 21)).mean()
			ema_data = pd.DataFrame(index=ma.index)
			ema_data['PRICE'] = data_frame['close']
			ema_data['MA'] = ma
			ema_data['EMA'] = np.NaN
			ema_data['EMA'][0] = ema_data['MA'][1]
			for i in range(1, len(ema_data)):
				ema_data['EMA'][i] = (ema_data['PRICE'][i] * k) + ((1-k) * ema_data['EMA'][i-1])
			trace_ema = go.Scatter(
				x=ema_data.index, y=ema_data['MA'], name='EMA', line=dict(color='#17BECF'), opacity=0.8)
			data.append(trace_ema)
		except (ErrorImplementingIndicator, TypeError) as e:
			log.warning(f"Error implementing 'ema' indicator: {e}")
		finally:
			return data


class CrossingMovingAvarege(CandlestickChartIndicator):
	"""
	Class responsible for implementing the crossing of moving averages that consists of indicating
	buying and selling an asset whenever the averages cross.

	detail:
		This indicator consists of 2 sets of simple moving averages. an acquaintance
		as short average or short and another known as long average or long whenever short crosses
		the long down we make a sale, whenever the long crosses the short up we buy.
	"""
	def indicate(self, data_frame, data=[], **kwargs):
		try:
			short_rolling = data_frame['close'].rolling(window=kwargs.get("short_rolling", 9)).mean()
			long_rolling  = data_frame['close'].rolling(window=kwargs.get("long_rolling", 21)).mean()
			trace_short_rolling = go.Scatter(
				x=short_rolling.index, y=short_rolling, name='SHORT', line=dict(color='#17BECF'), opacity=0.5)
			trace_long_rolling  = go.Scatter(
				x=long_rolling.index, y=long_rolling, name='LONG', line=dict(color='#17becf'), opacity=0.5)
			data.append(trace_short_rolling)
			data.append(trace_long_rolling)
		except (ErrorImplementingIndicator, TypeError) as e:
			log.warning(f"Error implementing 'crossing moving avarege' indicator: {e}")
		finally:
			return data


class MACD(CandlestickChartIndicator):

	"""
	Class responsible for implementing a MACD -> Convergence - Divergence
	of the moving average, which uses 3 exponential moving averages.
	"""
	def indicator(self, data_frame, data=[], **kwargs):
		try:
			high_average = data_frame['max'].rolling(window=kwargs.get("high", 8)).mean()
			low_average  = data_frame['min'].rolling(window=kwargs.get("low", 8)).mean()
			hilo_high = pd.DataFrame(index=data_frame.index)
			hilo_low  = pd.DataFrame(index=data_frame.index)
			hilo_high['max'] = np.where(data_frame['close'] > high_average, low_average, np.NaN)
			hilo_low['min']  = np.where(data_frame['close'] < low_average, high_average, np.NaN)
			trace_high = go.Scatter(x=hilo_high.index, y=hilo_high, line=dict(color='#17BECF'), opacity=1)
			trace_low = go.Scatter(x=hilo_low.index, y=hilo_low, line=dict(color='#B22222'), opacity=1)
			data.append(trace_high)
			data.append(trace_low)
		except (ErrorImplementingIndicator, TypeError) as e:
			log.warning(f"Error implementing 'macd' indicator: {e}")
		finally:
			return data


class BollingerBands(CandlestickChartIndicator):
	"""
	Class responsible for implementing boolinger bands based on variations
	prices at standard deviation levels.

	detail:
	This indicator is able to measure price volatility.
	"""
	def indicate(self, data_frame, data=[], **kwargs):
		try:
			df_avg = data_frame['close'].rolling(window=kwargs.get("days", 21)).mean().dropna()
			df_std = data_frame['close'].rolling(window=kwargs.get("days", 21)).std().dropna()
			df_bollinger = pd.DataFrame(index=df_avg.index)

			df_bollinger['mband'] = df_avg
			df_bollinger['uband'] = df_avg + df_std.apply(lambda x: (x * 2))
			df_bollinger['iband'] = df_avg - df_std.apply(lambda x: (x * 2))
			df_price = data_frame[df_bollinger.index[0]:]

			trace_prices = go.Candlestick(
			   x     = df_price.index,
			   open  = df_price['open'],
			   high  = df_price['max'],
			   low   = df_price['min'],
			   close = df_price['close'],
			   name='prices')
			uband = go.Scatter(
				x=df_bollinger.index, y=df_bollinger['uband'], name='Upper Band',
				line=dict(color='#17BECF'), opacity=0.8)
			mband = go.Scatter(
				x=df_bollinger.index, y=df_bollinger['mband'], name='Moving Band',
				line=dict(color='#B22222'), opacity=0.5)
			iband = go.Scatter(
				x=df_bollinger.index, y=df_bollinger['iband'], name='Lower Band',
				line=dict(color='#17BECF'), opacity=0.8)
			data.append(uband)
			data.append(mband)
			data.append(iband)
			data.append(trace_prices)
		except (ErrorImplementingIndicator, TypeError) as e:
			log.warning(f"Error implementing 'bollinger bands' indicator: {e}")
		finally:
			return data


# end-of-file