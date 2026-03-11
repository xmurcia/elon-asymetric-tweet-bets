// Analysis module for Asymetric Elon Bets
// Implements burst detection, Gaussian distribution, and thematic classification

/**
 * Gaussian probability density function
 * @param {number} x - input value
 * @param {number} mu - mean
 * @param {number} sigma - standard deviation
 * @returns {number} PDF value
 */
function gaussianPDF(x, mu = 220, sigma = 50) {
  const exponent = -0.5 * ((x - mu) / sigma) ** 2;
  return (1 / (sigma * Math.sqrt(2 * Math.PI))) * Math.exp(exponent);
}

/**
 * Generate Gaussian distribution data points
 * @param {number} min - min x
 * @param {number} max - max x
 * @param {number} step - step size
 * @returns {Array} [{x, y}]
 */
function generateGaussianData(min = 0, max = 400, step = 1) {
  const data = [];
  for (let x = min; x <= max; x += step) {
    data.push({ x, y: gaussianPDF(x) });
  }
  return data;
}

/**
 * Detect bursts from tweet timestamps
 * A burst is defined as ≥8 tweets within a 15-minute window
 * @param {Array} tweets - array of tweet objects with timestamp
 * @returns {Array} bursts with start, end, count, and theme
 */
function detectBursts(tweets) {
  if (!tweets || tweets.length === 0) return [];

  // Sort tweets by timestamp
  const sorted = tweets.slice().sort((a, b) => new Date(a.timestamp || a.created_at) - new Date(b.timestamp || b.created_at));
  const burstWindows = [];
  const windowMs = 15 * 60 * 1000; // 15 minutes in milliseconds

  for (let i = 0; i < sorted.length; i++) {
    const startTime = new Date(sorted[i].timestamp || sorted[i].created_at);
    const endTime = new Date(startTime.getTime() + windowMs);
    let count = 0;
    for (let j = i; j < sorted.length; j++) {
      const tweetTime = new Date(sorted[j].timestamp || sorted[j].created_at);
      if (tweetTime < endTime) {
        count++;
      } else {
        break;
      }
    }
    if (count >= 8) {
      burstWindows.push({
        start: startTime.toISOString(),
        end: endTime.toISOString(),
        count,
        // Determine theme based on tweet content (placeholder)
        theme: classifyTheme(sorted[i].text || '')
      });
      // Skip ahead to avoid overlapping windows
      i += count - 1;
    }
  }
  return burstWindows;
}

/**
 * Classify tweet theme based on keywords
 * @param {string} text - tweet content
 * @returns {string} theme: 'AI', 'Politics', 'Tesla', 'SpaceX', 'Grok', 'X', 'Other'
 */
function classifyTheme(text) {
  const lower = text.toLowerCase();
  if (lower.includes('ai') || lower.includes('artificial intelligence') || lower.includes('grok')) {
    return 'AI';
  } else if (lower.includes('tesla') || lower.includes('cybertruck') || lower.includes('ev')) {
    return 'Tesla';
  } else if (lower.includes('spacex') || lower.includes('starship') || lower.includes('falcon')) {
    return 'SpaceX';
  } else if (lower.includes('politic') || lower.includes('election') || lower.includes('government')) {
    return 'Politics';
  } else if (lower.includes('x.com') || lower.includes('twitter') || lower.includes('social')) {
    return 'X';
  } else {
    return 'Other';
  }
}

/**
 * Compute asymmetric trading recommendations based on bursts and markets
 * @param {Array} bursts - detected bursts
 * @param {Array} markets - Polymarket markets
 * @returns {Array} recommendations
 */
function generateAsymmetricRecommendations(bursts, markets) {
  const recommendations = [];
  // For each burst, find markets with matching theme
  bursts.forEach(burst => {
    markets.forEach(market => {
      const marketQuestion = market.question.toLowerCase();
      if (marketQuestion.includes(burst.theme.toLowerCase())) {
        // Determine action: if burst count high, buy YES (expect price increase)
        const action = burst.count > 10 ? 'BUY_YES' : 'BUY_NO';
        const confidence = Math.min(0.9, burst.count / 15);
        recommendations.push({
          marketId: market.id,
          marketQuestion: market.question,
          action,
          confidence,
          reasoning: `Burst of ${burst.count} tweets on ${burst.theme} within 15 minutes`,
          burstStart: burst.start,
          burstEnd: burst.end,
        });
      }
    });
  });
  // If no bursts, maybe recommend based on Gaussian distribution (placeholder)
  if (recommendations.length === 0) {
    // Example: recommend based on odds bucket near mean
    const meanBucket = 220;
    markets.forEach(market => {
      if (market.yes < 0.3) {
        recommendations.push({
          marketId: market.id,
          marketQuestion: market.question,
          action: 'BUY_YES',
          confidence: 0.5,
          reasoning: `Low YES price (${market.yes}) near Gaussian mean bucket ${meanBucket}`,
        });
      }
    });
  }
  return recommendations.slice(0, 5); // limit to top 5
}

module.exports = {
  gaussianPDF,
  generateGaussianData,
  detectBursts,
  classifyTheme,
  generateAsymmetricRecommendations,
};