// Backend API for Asymetric Elon Bets
const express = require('express');
const cors = require('cors');
const axios = require('axios');
const analysis = require('./analysis');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// In-memory storage for paper trades
let paperTrades = [];
let bankroll = 200.00; // Initial virtual bankroll

// Helper: fetch Elon Musk tweets from XTracker
async function fetchElonTweets() {
  try {
    const response = await axios.get('https://xtracker.polymarket.com/api/users/elonmusk/posts?platform=X');
    // Assuming response.data is an array of tweet objects with timestamp and text
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    console.error('Error fetching Elon tweets:', error.message);
    return [];
  }
}

// Helper: fetch Polymarket Elon-related markets (placeholder)
async function fetchElonMarkets() {
  // In a real implementation, we would call Polymarket API
  // For now, return mock data
  return [
    { id: 'elon-tweet-burst', question: 'Will Elon tweet ≥8 times in 15min today?', yes: 0.35, no: 0.65 },
    { id: 'tesla-stock-up', question: 'Will Tesla stock rise >5% after next Elon tweet?', yes: 0.42, no: 0.58 },
    { id: 'spacex-launch', question: 'Will SpaceX launch be announced this week?', yes: 0.28, no: 0.72 },
    { id: 'grok-release', question: 'Will Grok 3 be released within 30 days?', yes: 0.15, no: 0.85 },
  ];
}

// Endpoint: Elon tweets (existing)
app.get('/api/tweets', async (req, res) => {
  try {
    const tweets = await fetchElonTweets();
    res.json({ success: true, count: tweets.length, data: tweets });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Endpoint: Polymarket Elon-related markets
app.get('/api/polymarket/elon-markets', async (req, res) => {
  try {
    const markets = await fetchElonMarkets();
    res.json({ success: true, data: markets });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Endpoint: Paper trading simulation (GET)
app.get('/api/trades/paper', (req, res) => {
  try {
    res.json({
      success: true,
      bankroll,
      trades: paperTrades,
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Endpoint: Submit a paper trade (POST)
app.post('/api/trades/paper', (req, res) => {
  try {
    const { marketId, action, shares, price } = req.body;
    if (!marketId || !action || !shares || !price) {
      return res.status(400).json({ success: false, error: 'Missing required fields' });
    }
    const trade = {
      id: Date.now(),
      marketId,
      action,
      shares,
      price,
      timestamp: new Date().toISOString(),
      pnl: 0, // will be calculated later
    };
    paperTrades.push(trade);
    // Deduct cost from bankroll (simplified)
    const cost = shares * price;
    bankroll -= cost;
    res.json({ success: true, trade, bankroll });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Endpoint: Gaussian distribution data
app.get('/api/analysis/gaussian', (req, res) => {
  try {
    const data = analysis.generateGaussianData();
    res.json({ success: true, data });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Endpoint: Asymmetric trading recommendations
app.get('/api/analysis/asymetric', async (req, res) => {
  try {
    const tweets = await fetchElonTweets();
    const markets = await fetchElonMarkets();
    const bursts = analysis.detectBursts(tweets);
    const recommendations = analysis.generateAsymmetricRecommendations(bursts, markets);
    res.json({
      success: true,
      bursts,
      markets,
      recommendations,
      tweetCount: tweets.length,
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Endpoint: Burst detection only
app.get('/api/analysis/bursts', async (req, res) => {
  try {
    const tweets = await fetchElonTweets();
    const bursts = analysis.detectBursts(tweets);
    res.json({ success: true, bursts });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Global error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ success: false, error: 'Something broke!' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});