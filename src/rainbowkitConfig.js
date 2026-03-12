import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import { polygon } from 'wagmi/chains';

export const config = getDefaultConfig({
  appName: 'Elon Asymmetric Tweet Bets',
  projectId: 'YOUR_PROJECT_ID', // Replace with your WalletConnect Project ID
  chains: [polygon],
  ssr: true,
});