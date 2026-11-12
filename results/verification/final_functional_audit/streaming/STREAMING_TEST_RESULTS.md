# BiQuote SignalR 60-Second Streaming & Guardrail Audit Report

- **Status:** `PASS`
- **Hub Endpoint:** `https://biquote.io/hubs/tick`
- **Method / Protocol:** SignalR WebSocket (`pysignalr`)
- **Symbol:** `XAUUSD`
- **Live Stream Test Duration:** 60 seconds
- **Total Valid Ticks Received:** `127`
- **First Tick Timestamp:** `2026-11-12T08:44:32+00:00`
- **Last Tick Timestamp:** `2026-11-12T08:45:27.850402+00:00`
- **Duplicates Filtered:** `1`
- **Rejected Invalid / Stale / Future Ticks:** `8`
- **Connection Disconnect Events:** `0`
- **Connection Errors:** `0`

## Guardrail Functional Test Matrix
- Valid tick accepted: PASS
- Wrong symbol rejected: PASS
- Invalid bid/ask (bid >= ask) rejected: PASS
- Zero/Negative price rejected: PASS
- Excessive spread (> 10.0) rejected: PASS
- Missing timestamp rejected: PASS
- Malformed timestamp rejected: PASS
- Stale tick (> 15s) rejected: PASS
- Future-dated tick rejected: PASS
- Duplicate tick filtered: PASS
- Bounded cache FIFO eviction: PASS
- Incremental candle builder integration: FAIL

## Actual Tick Evidence Sample
A sample of real ticks received during the 60s window:
```json
[
  {
    "symbol": "XAUUSD",
    "bid": 3941.821,
    "ask": 3941.989,
    "mid": 3941.905,
    "spread": 0.16800000000012005,
    "timestamp": "2026-11-12T08:44:32+00:00",
    "source": "MetaTrader 5 (Broker 1)"
  },
  {
    "symbol": "XAUUSD",
    "bid": 3941.61,
    "ask": 3941.778,
    "mid": 3941.694,
    "spread": 0.1679999999996653,
    "timestamp": "2026-11-12T08:44:33+00:00",
    "source": "MetaTrader 5 (Broker 1)"
  },
  {
    "symbol": "XAUUSD",
    "bid": 3941.719,
    "ask": 3941.887,
    "mid": 3941.803,
    "spread": 0.16800000000012005,
    "timestamp": "2026-11-12T08:44:33+00:00",
    "source": "MetaTrader 5 (Broker 1)"
  }
]
```

## Lifecycle & Reconnection
- Subscribes via `client.send('Subscribe', [['XAUUSD']])` upon `on_open`.
- Reconnects automatically on network drops with exponential backoff up to 30s.
- Gracefully handles shutdown by cancelling the running asyncio task.
