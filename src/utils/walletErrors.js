// Normalize common wallet/viem/wagmi errors into actionable messages.

export function normalizeWalletError(err) {
  const message = (err?.shortMessage || err?.message || '').toString();
  const code = err?.code;

  // EIP-1193 user rejected request
  if (code === 4001 || /user rejected|rejected the request|denied transaction/i.test(message)) {
    return {
      title: 'Transaction cancelled',
      description: 'You rejected the request in your wallet.',
      canRetry: true,
    };
  }

  // Insufficient funds / gas
  if (
    code === -32000 ||
    /insufficient funds|gas required exceeds allowance|funds for gas/i.test(message)
  ) {
    return {
      title: 'Insufficient funds',
      description: 'You do not have enough balance to pay for the transaction (including gas).',
      canRetry: true,
    };
  }

  // Wrong network / chain mismatch
  if (/chain mismatch|wrong network|unsupported chain|chainid|switch/i.test(message)) {
    return {
      title: 'Wrong network',
      description: 'Please switch to the required network in your wallet and try again.',
      canRetry: true,
    };
  }

  // Dropped/replaced/underpriced
  if (/dropped|replaced|nonce too low|underpriced|already known/i.test(message)) {
    return {
      title: 'Transaction not accepted',
      description: 'The transaction was dropped or replaced. Try again or speed up in your wallet.',
      canRetry: true,
    };
  }

  return {
    title: 'Wallet error',
    description: message || 'Something went wrong while interacting with the wallet.',
    canRetry: true,
  };
}
