import React, { useMemo, useState } from 'react';
import { toast } from 'react-hot-toast';
import { parseEther } from 'viem';
import { useAccount, useChainId, useSendTransaction, useSwitchChain, useWaitForTransactionReceipt } from 'wagmi';
import { polygon } from 'wagmi/chains';
import { normalizeWalletError } from '../utils/walletErrors';

// Small demo component used as a reference implementation for robust wallet error handling.
// It never auto-sends; user must click.

const TX_STUCK_AFTER_MS = 60_000;

export default function SendNativeTokenButton() {
  const { address, isConnected } = useAccount();
  const chainId = useChainId();
  const { switchChainAsync, isPending: isSwitching } = useSwitchChain();

  const [lastHash, setLastHash] = useState(null);
  const [stuck, setStuck] = useState(false);

  const to = useMemo(() => address, [address]);

  const {
    sendTransactionAsync,
    isPending: isSending,
    reset,
  } = useSendTransaction();

  const {
    isLoading: isConfirming,
    isSuccess,
    isError: isReceiptError,
    error: receiptError,
  } = useWaitForTransactionReceipt({
    hash: lastHash,
    confirmations: 1,
    // only run when we have a hash
    query: { enabled: Boolean(lastHash) },
  });

  async function ensurePolygon() {
    if (chainId === polygon.id) return true;
    try {
      await switchChainAsync({ chainId: polygon.id });
      return true;
    } catch (err) {
      const n = normalizeWalletError(err);
      toast.error(`${n.title}: ${n.description}`);
      return false;
    }
  }

  async function onClick() {
    setStuck(false);

    if (!isConnected) {
      toast.error('Connect your wallet first.');
      return;
    }
    if (!to) {
      toast.error('No wallet address found.');
      return;
    }

    const ok = await ensurePolygon();
    if (!ok) return;

    try {
      reset?.();
      const hash = await sendTransactionAsync({
        to,
        value: parseEther('0'),
      });
      setLastHash(hash);
      toast.success('Transaction sent. Waiting for confirmation…');

      // Guard against infinite spinners: if it takes too long, prompt user to check wallet / retry.
      setTimeout(() => {
        setStuck(prev => {
          if (prev) return prev;
          // only mark stuck if still confirming
          return true;
        });
      }, TX_STUCK_AFTER_MS);
    } catch (err) {
      const n = normalizeWalletError(err);
      toast.error(`${n.title}: ${n.description}`);
    }
  }

  const disabled = isSending || isConfirming || isSwitching;

  return (
    <div style={{ marginTop: 16 }}>
      <button onClick={onClick} disabled={disabled}>
        {isSwitching
          ? 'Switching network…'
          : isSending
            ? 'Confirm in wallet…'
            : isConfirming
              ? 'Confirming…'
              : 'Send 0 (demo tx)'}
      </button>

      {lastHash && (
        <div style={{ marginTop: 8, fontSize: 12, opacity: 0.85 }}>
          <div>
            Tx hash: <code>{lastHash}</code>
          </div>
          {isSuccess && <div>Status: confirmed</div>}
          {stuck && !isSuccess && <div>Status: pending for a while — check your wallet or try again.</div>}
          {isReceiptError && (
            <div>
              Status: error — {normalizeWalletError(receiptError).description}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
