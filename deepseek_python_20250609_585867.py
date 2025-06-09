import ccxt
import pandas as pd
import numpy as np
from ta import add_all_ta_features
from datetime import datetime
import time
import json
import logging
from .strategies import Strategy, MovingAverageCrossover, RSIStrategy
from .risk_management import RiskManager

class TradingBot:
    def __init__(self, config_path='config/config.json'):
        self.load_config(config_path)
        self.setup_logging()
        self.exchange = self.connect_to_exchange()
        self.strategy = self.select_strategy()
        self.risk_manager = RiskManager(
            max_trade_size=self.config['risk']['max_trade_size'],
            stop_loss=self.config['risk']['stop_loss'],
            take_profit=self.config['risk']['take_profit']
        )
        self.running = False
        
    def load_config(self, config_path):
        with open(config_path) as f:
            self.config = json.load(f)
        
    def setup_logging(self):
        logging.basicConfig(
            filename='trading_bot.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('TradingBot')
        
    def connect_to_exchange(self):
        exchange_class = getattr(ccxt, self.config['exchange']['name'])
        exchange = exchange_class({
            'apiKey': self.config['exchange']['api_key'],
            'secret': self.config['exchange']['api_secret'],
            'enableRateLimit': True
        })
        self.logger.info(f"Connected to {self.config['exchange']['name']}")
        return exchange
        
    def select_strategy(self):
        strategy_name = self.config['strategy']['name']
        if strategy_name == 'MovingAverageCrossover':
            return MovingAverageCrossover(
                short_window=self.config['strategy']['params']['short_window'],
                long_window=self.config['strategy']['params']['long_window']
            )
        elif strategy_name == 'RSIStrategy':
            return RSIStrategy(
                rsi_period=self.config['strategy']['params']['rsi_period'],
                overbought=self.config['strategy']['params']['overbought'],
                oversold=self.config['strategy']['params']['oversold']
            )
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")
    
    def fetch_market_data(self, symbol, timeframe, limit=100):
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df = add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume")
            return df
        except Exception as e:
            self.logger.error(f"Error fetching market data: {e}")
            return None
    
    def execute_trade(self, symbol, side, amount, price=None):
        try:
            if price is None:
                order = self.exchange.create_market_order(symbol, side, amount)
            else:
                order = self.exchange.create_limit_order(symbol, side, amount, price)
            self.logger.info(f"Executed {side} order for {amount} {symbol}: {order}")
            return order
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return None
    
    def run(self):
        self.running = True
        self.logger.info("Starting trading bot...")
        
        while self.running:
            try:
                symbol = self.config['trading']['symbol']
                timeframe = self.config['trading']['timeframe']
                
                # Fetch market data
                data = self.fetch_market_data(symbol, timeframe)
                if data is None:
                    time.sleep(60)
                    continue
                
                # Get trading signal from strategy
                signal = self.strategy.generate_signal(data.iloc[-1])
                
                # Check risk management
                if signal != 0 and self.risk_manager.approve_trade():
                    amount = self.risk_manager.calculate_position_size(
                        self.exchange.fetch_balance()[self.config['trading']['base_currency']]['free'],
                        data['close'].iloc[-1]
                    )
                    if signal == 1:
                        self.execute_trade(symbol, 'buy', amount)
                    elif signal == -1:
                        self.execute_trade(symbol, 'sell', amount)
                
                time.sleep(self.config['trading']['interval'])
                
            except KeyboardInterrupt:
                self.logger.info("Shutting down trading bot...")
                self.running = False
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(60)