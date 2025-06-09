class RiskManager:
    def __init__(self, max_trade_size=0.1, stop_loss=0.02, take_profit=0.05):
        self.max_trade_size = max_trade_size  # % din portofoliu per trade
        self.stop_loss = stop_loss  # % pierdere
        self.take_profit = take_profit  # % profit
        self.active_trades = []
        
    def approve_trade(self):
        # Aici poți adăuga logici suplimentare de aprobare a tranzacțiilor
        return len(self.active_trades) < 5  # Limită de 5 tranzacții active
        
    def calculate_position_size(self, balance, current_price):
        max_trade_amount = balance * self.max_trade_size
        return min(max_trade_amount / current_price, balance / current_price)
    
    def check_trade_outcome(self, trade):
        # Verifică dacă un trade a atins stop loss sau take profit
        pass