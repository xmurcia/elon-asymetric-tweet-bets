import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

const TradesTable = () => {
  const [trades, setTrades] = useState([]);
  const [bankroll, setBankroll] = useState(200.00);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newTrade, setNewTrade] = useState({
    marketId: '',
    action: 'BUY_YES',
    shares: 10,
    price: 0.50,
  });

  const fetchTrades = async () => {
    try {
      const response = await api.get('/api/trades/paper');
      if (response.data.success) {
        setTrades(response.data.trades);
        setBankroll(response.data.bankroll);
      } else {
        setError(response.data.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrades();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/api/trades/paper', newTrade);
      if (response.data.success) {
        // Refresh trades list
        fetchTrades();
        // Reset form
        setNewTrade({
          marketId: '',
          action: 'BUY_YES',
          shares: 10,
          price: 0.50,
        });
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setNewTrade(prev => ({
      ...prev,
      [name]: name === 'shares' || name === 'price' ? parseFloat(value) : value,
    }));
  };

  if (loading) return <div>Loading paper trades...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h2>Paper Trading Simulation</h2>
      <div style={{ marginBottom: '20px' }}>
        <h3>Current Bankroll: ${bankroll.toFixed(2)}</h3>
      </div>
      
      <h3>Submit New Trade</h3>
      <form onSubmit={handleSubmit} style={{ marginBottom: '30px' }}>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
          <div>
            <label>Market ID:</label>
            <input
              type="text"
              name="marketId"
              value={newTrade.marketId}
              onChange={handleChange}
              required
              placeholder="elon-tweet-burst"
            />
          </div>
          <div>
            <label>Action:</label>
            <select name="action" value={newTrade.action} onChange={handleChange}>
              <option value="BUY_YES">BUY YES</option>
              <option value="BUY_NO">BUY NO</option>
              <option value="SELL_YES">SELL YES</option>
              <option value="SELL_NO">SELL NO</option>
            </select>
          </div>
          <div>
            <label>Shares:</label>
            <input
              type="number"
              name="shares"
              value={newTrade.shares}
              onChange={handleChange}
              min="1"
              step="1"
              required
            />
          </div>
          <div>
            <label>Price per share ($):</label>
            <input
              type="number"
              name="price"
              value={newTrade.price}
              onChange={handleChange}
              min="0.01"
              step="0.01"
              required
            />
          </div>
          <button type="submit">Submit Trade</button>
        </div>
      </form>

      <h3>Trade History</h3>
      {trades.length === 0 ? (
        <p>No trades yet. Submit your first paper trade!</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ border: '1px solid #ccc', padding: '8px' }}>ID</th>
              <th style={{ border: '1px solid #ccc', padding: '8px' }}>Market</th>
              <th style={{ border: '1px solid #ccc', padding: '8px' }}>Action</th>
              <th style={{ border: '1px solid #ccc', padding: '8px' }}>Shares</th>
              <th style={{ border: '1px solid #ccc', padding: '8px' }}>Price</th>
              <th style={{ border: '1px solid #ccc', padding: '8px' }}>Timestamp</th>
              <th style={{ border: '1px solid #ccc', padding: '8px' }}>P&L</th>
            </tr>
          </thead>
          <tbody>
            {trades.map(trade => (
              <tr key={trade.id}>
                <td style={{ border: '1px solid #ccc', padding: '8px' }}>{trade.id}</td>
                <td style={{ border: '1px solid #ccc', padding: '8px' }}>{trade.marketId}</td>
                <td style={{ border: '1px solid #ccc', padding: '8px' }}>{trade.action}</td>
                <td style={{ border: '1px solid #ccc', padding: '8px' }}>{trade.shares}</td>
                <td style={{ border: '1px solid #ccc', padding: '8px' }}>${trade.price.toFixed(2)}</td>
                <td style={{ border: '1px solid #ccc', padding: '8px' }}>{new Date(trade.timestamp).toLocaleString()}</td>
                <td style={{ border: '1px solid #ccc', padding: '8px' }}>${trade.pnl.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default TradesTable;