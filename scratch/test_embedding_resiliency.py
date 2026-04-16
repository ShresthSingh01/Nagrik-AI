"""Simulates 20 parallel embedding requests to verify semaphore and retry logic."""
import asyncio
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.utils import get_embedding

async def test_high_concurrency():
    print("Spawning 20 parallel embedding requests...")
    labels = [f"Field label {i} for testing rate limits" for i in range(20)]
    
    # We use a semaphore here just like in main.py to protect the API
    sem = asyncio.Semaphore(5)
    
    async def worker(label):
        async with sem:
            # get_embedding is synchronous (blocking), so we run in thread
            return await asyncio.to_thread(get_embedding, label)

    tasks = [worker(l) for l in labels]
    results = await asyncio.gather(*tasks)
    
    success = sum(1 for r in results if r is not None)
    print(f"\nResults: {success}/{len(labels)} successful")
    
    if success == len(labels):
        print("PASS: All requests succeeded (Semaphore + Retry worked)")
    else:
        print(f"FAILED: Only {success} requests succeeded. Check for error logs.")

if __name__ == "__main__":
    asyncio.run(test_high_concurrency())
