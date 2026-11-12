import asyncio
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path("src").resolve()))
from realtime_data_engine import RealtimeDataEngine

logging.basicConfig(level=logging.INFO)

async def main():
    engine = RealtimeDataEngine(symbol="XAUUSD")
    print("Testing SignalR connection for 3 seconds...")
    try:
        await engine.start_streaming(duration=3.0)
        print(f"Streaming test completed. Status: {engine.connection_status}, Ticks received: {engine.tick_count}")
    except Exception as e:
        print(f"Streaming test encountered exception/blocker: {e}")
        engine.connection_status = "BLOCKED"

if __name__ == "__main__":
    asyncio.run(main())
