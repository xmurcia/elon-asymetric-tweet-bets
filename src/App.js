import './App.css';
import { WagmiProvider } from 'wagmi';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RainbowKitProvider, ConnectButton } from '@rainbow-me/rainbowkit';
import { config } from './rainbowkitConfig';
import '@rainbow-me/rainbowkit/styles.css';

const queryClient = new QueryClient();

function App() {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider>
          <div className="App">
            <header className="App-header">
              <p>
                Elon Asymmetric Tweet Bets
              </p>
              <ConnectButton />
            </header>
          </div>
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  );
}

export default App;