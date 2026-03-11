// Backend API XTracker
const express = require('express');
const axios = require('axios');
const app = express();
app.get('/api/tweets', async (req, res) => {
  const data = await axios.get('https://xtracker.polymarket.com/api/users/elonmusk/posts?platform=X');
  res.json(data.data);
});
app.listen(3001, () => console.log('Server running'));