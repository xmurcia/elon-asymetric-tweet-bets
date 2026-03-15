import './App.css';
import { useEffect, useMemo, useState } from 'react';
import { WagmiProvider } from 'wagmi';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RainbowKitProvider, ConnectButton } from '@rainbow-me/rainbowkit';
import { Toaster } from 'react-hot-toast';
import { config } from './rainbowkitConfig';
import { api } from './api/client';
import '@rainbow-me/rainbowkit/styles.css';

const queryClient = new QueryClient();

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—';
  return `${Math.round(Number(value) * 100)}%`;
}

function formatDate(value) {
  if (!value) return 'Date TBD';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return 'Date TBD';
  return parsed.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
  });
}

function getEventStatus(event) {
  if (event.closed) return 'Closed';
  if (event.active) return 'Live';
  return 'Watching';
}

function getPrimaryOutcome(event) {
  if (!event?.predictions?.length) return null;

  const withPrice = event.predictions.filter(item => item.price !== null && item.price !== undefined);
  const sorted = (withPrice.length ? withPrice : event.predictions)
    .slice()
    .sort((a, b) => {
      const aPrice = a.price ?? -1;
      const bPrice = b.price ?? -1;
      return bPrice - aPrice;
    });

  return sorted[0] || null;
}

function getSecondaryOutcome(event, primaryOutcome) {
  if (!event?.predictions?.length) return null;
  return event.predictions.find(item => item.outcome_id !== primaryOutcome?.outcome_id) || null;
}

function EventCard({ event }) {
  const primaryOutcome = getPrimaryOutcome(event);
  const secondaryOutcome = getSecondaryOutcome(event, primaryOutcome);
  const hasRealPricing = Boolean(primaryOutcome && primaryOutcome.price !== null && primaryOutcome.price !== undefined);

  return (
    <article className="event-card">
      <div className="event-card__topline">
        <span className={`status-pill status-pill--${getEventStatus(event).toLowerCase()}`}>
          {getEventStatus(event)}
        </span>
        <span className="event-card__date">{formatDate(event.end_date)}</span>
      </div>

      <h2 className="event-card__title">{event.question || event.slug || `Event #${event.id}`}</h2>

      <div className="event-card__body">
        <div className="event-metric event-metric--primary">
          <span className="event-metric__label">Market lean</span>
          <strong className="event-metric__value">
            {primaryOutcome ? `${primaryOutcome.outcome_name} ${formatPercent(primaryOutcome.price)}` : 'No pricing yet'}
          </strong>
          <span className="event-metric__hint">
            {hasRealPricing
              ? 'Latest implied probability from backend snapshots'
              : 'Backend has the event, but no latest price is available yet'}
          </span>
        </div>

        {secondaryOutcome && (
          <div className="event-metric">
            <span className="event-metric__label">Other side</span>
            <strong className="event-metric__value">
              {secondaryOutcome.outcome_name} {formatPercent(secondaryOutcome.price)}
            </strong>
          </div>
        )}
      </div>

      <div className="event-card__footer">
        <button className="primary-cta" type="button">
          {hasRealPricing ? 'Review setup' : 'Join waitlist for execution'}
        </button>
        <p className="event-card__footnote">
          {hasRealPricing
            ? 'Execution flow still placeholder: wallet is connected, order UX is not closed yet.'
            : 'Honest placeholder until live trading flow is defined.'}
        </p>
      </div>
    </article>
  );
}

function WalletStrip() {
  return (
    <section className="wallet-strip">
      <div>
        <p className="wallet-strip__eyebrow">Wallet</p>
        <h3>Connect when you are ready</h3>
        <p>Useful for the real trade flow, but it no longer blocks browsing events.</p>
      </div>
      <ConnectButton showBalance={false} chainStatus="icon" accountStatus="avatar" />
    </section>
  );
}

function MobileMvpScreen() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [coverage, setCoverage] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError('');

      try {
        const [eventsResponse, coverageResponse] = await Promise.allSettled([
          api.get('/events'),
          api.get('/coverage'),
        ]);

        if (cancelled) return;

        const rawEvents = eventsResponse.status === 'fulfilled' ? eventsResponse.value.data : null;
        const safeEvents = Array.isArray(rawEvents) ? rawEvents : [];

        if (eventsResponse.status === 'rejected') {
          throw new Error('Could not load events from backend. Check API availability.');
        }

        const enrichedEvents = await Promise.all(
          safeEvents.slice(0, 24).map(async event => {
            try {
              const predictionsResponse = await api.get(`/events/${event.id}/predictions`);
              return {
                ...event,
                predictions: predictionsResponse.data?.predictions || [],
              };
            } catch (predictionError) {
              return {
                ...event,
                predictions: [],
              };
            }
          })
        );

        if (cancelled) return;

        setEvents(enrichedEvents);
        if (coverageResponse.status === 'fulfilled') {
          setCoverage(coverageResponse.value.data);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError.message || 'Unknown error loading mobile MVP');
          setEvents([]);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, []);

  const liveCount = useMemo(
    () => events.filter(event => event.active && !event.closed).length,
    [events]
  );

  return (
    <main className="mobile-shell">
      <section className="hero-card">
        <p className="hero-card__eyebrow">MVP mobile</p>
        <h1>Elon tweet bets</h1>
        <p className="hero-card__copy">
          Browse live events fast, see the latest market lean, and keep the next action obvious.
        </p>

        <div className="hero-stats">
          <div className="hero-stat">
            <span className="hero-stat__label">Events</span>
            <strong>{events.length}</strong>
          </div>
          <div className="hero-stat">
            <span className="hero-stat__label">Live</span>
            <strong>{liveCount}</strong>
          </div>
          <div className="hero-stat">
            <span className="hero-stat__label">Coverage</span>
            <strong>{coverage?.coverage_pct != null ? `${coverage.coverage_pct}%` : '—'}</strong>
          </div>
        </div>
      </section>

      <WalletStrip />

      <section className="events-section">
        <div className="section-heading">
          <div>
            <p className="section-heading__eyebrow">Events</p>
            <h2>Current opportunities</h2>
          </div>
          <button className="ghost-button" type="button" onClick={() => window.location.reload()}>
            Refresh
          </button>
        </div>

        {loading && (
          <div className="feedback-card">
            <strong>Loading events…</strong>
            <p>Pulling markets and latest probabilities from the backend.</p>
          </div>
        )}

        {!loading && error && (
          <div className="feedback-card feedback-card--error">
            <strong>Backend unavailable</strong>
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && events.length === 0 && (
          <div className="feedback-card">
            <strong>No events yet</strong>
            <p>The mobile shell is ready, but the backend has not returned any event rows.</p>
          </div>
        )}

        {!loading && !error && events.length > 0 && (
          <div className="events-list">
            {events.map(event => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

function App() {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider>
          <div className="App">
            <Toaster position="top-right" />
            <MobileMvpScreen />
          </div>
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
}

export default App;
