#############################################################################
##            __          __  _  _______            _                      ##
##            \ \        / / | ||__   __|          | |                     ##
##             \ \  /\  / /__| |__ | |_ __ __ _  __| | ___ _ __            ##
##              \ \/  \/ / _ \ '_ \| | '__/ _` |/ _` |/ _ \ '__|           ##
##               \  /\  /  __/ |_) | | | | (_| | (_| |  __/ |              ##
##                \/  \/ \___|_.__/|_|_|  \__,_|\__,_|\___|_|              ##
##                                                                         ##
##        Copyright (c) 2020 MarcosVs98 - Todos os Direitos Reservados     ##
##                                                                         ##
#############################################################################
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


class WBPlottingExeception(Exception):
	pass


class WBTraceError(WBPlottingExeception):
	pass


class WBIndicatoImplementedError(WBPlottingExeception):
	pass


class CandlestickChartIndicator(abc.ABC):

	def __init__(self, candlesticks, currency_pair, ranges_lider=False):
		self.ohlc = (c for c in candlesticks)
		self.currency_pair  = currency_pair
		self.df = pd.DataFrame(self.ohlc)
		self.data = []
		self.rangeslider = rangeslider

	def _init_candles(self, *args, **kwargs):
		try:
			self.df['from'] = pd.to_datetime(self.df['from'], unit='s')
			self.df['to']   = pd.to_datetime(self.df['to'],   unit='s')
			self.df = self.df.set_index(pd.DatetimeIndex(self.df['to'].values))

			trace_candles = go.Candlestick(
			      x    = self.df.index,
			      open  = self.df['open'],
			      high  = self.df['max'],
			      low   = self.df['min'],
			      close = self.df['close'],
			      name  = self.self.currency_pair
			)
			self.data.append(trace_candles)
		except WBTraceError as e:
			print(e)

	@abc.abstractmethod
	def inicate(self):
		pass

	@property
	def get_dataframe(self):
		return self.df


class MA(CandlestickIndicator):

	def indicate(self, days=21, **kwargs):
		"""
		Método responsável por implementar uma Média Movel simples que ajuda
		filtrar oscilações de preço ajudando na identificação de tendências.
		"""
		try:
			MA = self.df['close'].rolling(window=days).mean()
			trace_avg = go.Scatter(x=MA.index, y=MA, name='MA', line=dict(color='#BEBECF'), opacity=0.8)
			self.data.append(trace_avg)

		except WBIndicatoImplementedError as e:
			print(e)


class EMA(CandlestickIndicator):
	def indicate(self, days=21, **kwargs):
		"""
		Método responsável por implementar uma Média móvel expoencial
		MME = Preço hoje * K + MME ontem x (1-k) onde K = 2 /(N+1)
		"""
		try:
			k = (2 / (days + 1))
			MA = self.df['close'].rolling(window=days).mean()
			ema_data = pd.DataFrame(index=MA.index)
			ema_data['PRICE'] = self.df['close']
			ema_data['MA'] = MA
			ema_data['EMA'] = np.NaN
			ema_data['EMA'][0] = ema_data['MA'][1]
			for i in range(1, len(ema_data)):
				ema_data['EMA'][i] = (ema_data['PRICE'][i] * k) + ((1-k) * ema_data['EMA'][i-1])
			trace_ema = go.Scatter(
					x=ema_data.index, y=ema_data['MA'], name='EMA', line=dict(color='#17BECF'), opacity=0.8)
			self.data.append(trace_ema)

		except WBIndicatoImplementedError as e:
			print(e)


class CrossingMovingAvarege(CandlestickIndicator):
	def indicate(self, short_rolling=9, long_rolling=21, **kwargs):
		"""
		Cruzamento de médias móveis consiste em comprar e vender um ativo sempre que as médias
		cruzarem. Este indicador é composto por 2 conjuntos de média moveis simples. Uma conhecida
		como média curta ou short e outra conhecida como média longa ou long Sempre que short cruzar
		a long para baixo realizamos uma venda, sempre que a long cruzar a short para cima compramos.
		"""
		try:
			short_rolling = self.df['close'].rolling(window=short_rolling).mean()
			long_rolling  = self.df['close'].rolling(window=long_rolling).mean()
			trace_short_rolling = go.Scatter(
				x=short_rolling.index, y=short_rolling, name='SHORT', line=dict(color='#17BECF'), opacity=0.5)
			trace_long_rolling  = go.Scatter(
				x=long_rolling.index, y=long_rolling, name='LONG', line=dict(color='#17becf'), opacity=0.5)
			self.data.append(trace_short_rolling)
			self.data.append(trace_long_rolling)

		except WBIndicatoImplementedError as e:
			print(e)



class MACD(CandlestickChartIndicator):

	def indicator(self, high=8, low=8, **kwargs):
		"""
		Método responsável por implementar MACD -> Convergência-Divergência
		da Média Movel, que utiliza 3 medias moveis expoencial.
		"""
		try:
			high_average = self.df['max'].rolling(window=high).mean()
			low_average  = self.df['min'].rolling(window=low).mean()
			hilo_high = pd.DataFrame(index=self.df.index)
			hilo_low  = pd.DataFrame(index=self.df.index)
			hilo_high['max'] = np.where(self.df['close'] > high_average, low_average, np.NaN)
			hilo_low['min']  = np.where(self.df['close'] < low_average, high_average, np.NaN)
			trace_high = go.Scatter(x=hilo_high.index, y=hilo_high, line=dict(color='#17BECF'), opacity=1)
			trace_low = go.Scatter(x=hilo_low.index, y=hilo_low, line=dict(color='#B22222'), opacity=1)
			self.data.append(trace_high)
			self.data.append(trace_low)
		except WBIndicatorError as e:
			print(e)


class BollingerBands(CandlestickChartIndicator):

	def indicate(self, days=21, **kwargs):
		"""
		Método responsável por implementar bandas de boolinger com base nas variações
		dos preços em niveis de desvios padrões. Este indicador é capaz de medir
		volatilidade do preço.
		"""
		try:
			df_avg = self.df['close'].rolling(window=days).mean().dropna()
			df_std = self.df['close'].rolling(window=days).std().dropna()
			df_bollinger = pd.DataFrame(index=df_avg.index)
			df_bollinger['mband'] = df_avg
			df_bollinger['uband'] = df_avg + df_std.apply(lambda x: (x * 2))
			df_bollinger['iband'] = df_avg - df_std.apply(lambda x: (x * 2))
			df_price = self.df[df_bollinger.index[0]:]
			try:
				trace_prices = go.Candlestick(
						  x    = df_price.index,
						 open  = df_price['open'],
						 high  = df_price['max'],
						 low   = df_price['min'],
						 close = df_price['close'],
						 name='prices')
			except WBTraceError as e:
				print(e)
			uband = go.Scatter(
				x=df_bollinger.index, y=df_bollinger['uband'], name='Upper Band',
				line=dict(color='#17BECF'), opacity=0.8)
			mband = go.Scatter(
				x=df_bollinger.index, y=df_bollinger['mband'], name='Moving Band',
				line=dict(color='#B22222'), opacity=0.5)
			iband = go.Scatter(
				x=df_bollinger.index, y=df_bollinger['iband'], name='Lower Band',
				line=dict(color='#17BECF'), opacity=0.8)
			self.data.append(uband)
			self.data.append(mband)
			self.data.append(iband)
			self.data.append(trace_prices)

		except WBIndicatoImplementedError as e:
			print(e)


class IndicatorBuilder():

	def create(self, **kwargs):
		"""
		Método responsável por implementar uma vizualização do gráfico
		traçado e seus indicadores.
		"""
		try:
			self._init_candles(**kwargs)
			self._on_ma_candle(**kwargs)
			self._on_ema_candle(**kwargs)
			self._on_macd_candle(**kwargs)
			self._on_crossing_moving_average_candle(**kwargs)
			self._on_bollinger_bands_candle(**kwargs)
			fig = go.Figure(dict(data=self.data)).update_layout(xaxis_rangeslider_visible=self.rangeslider)
			fig.show()

		except WBTraceError as e:
			print(e)


# end-of-file
