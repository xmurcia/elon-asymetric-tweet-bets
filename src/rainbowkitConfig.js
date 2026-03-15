import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import { polygon } from 'wagmi/chains';

const walletConnectProjectId = process.env.REACT_APP_WALLETCONNECT_PROJECT_ID;

export const config = getDefaultConfig({
  appName: 'Elon Asymmetric Tweet Bets',
  // WalletConnect requires a Project ID. In CRA we load it from REACT_APP_* env.
  projectId: walletConnectProjectId || 'MISSING_WALLETCONNECT_PROJECT_ID',
  chains: [polygon],
  // CRA is a client-only app; disable SSR mode.
  ssr: false,
});