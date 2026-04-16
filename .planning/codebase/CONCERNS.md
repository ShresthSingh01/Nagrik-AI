# CONCERNS.md

## Bypassed Systems and Deprecations
- **`updated_at` timestamps**: Job artifacts save `updated_at` as a random hex string (UUID), rather than actual clock timing.
- **Document Memory**: `backend/memory.py` is implemented but omitted from live orchestrator logic in `main.py`.
- **Hallucination Checking**: Built-in verification logic `verify_output()` designed to reduce LLM hallucinations isn't being run. 

## Storage and Persistence Scaffolding
- **Lack of Remote Storage Database**: Data persistence only exists temporarily on the local server container logic (`output/` files). In production deployments across multiple containers, data will be lost or unshared.
- **Client History Limitations**: Frontend history operates purely off local browser `localStorage`. A clear roadmap is needed for cloud synching user sessions.

## Scaling
- **Heavy CPU/Memory Operations**: Progressive image chunking, text string evaluation limits, and heavy RAG arrays currently sit unoptimized. 
- **Timeouts**: The standard processing timeout `PROCESSING_TIMEOUT_MS` sits firmly at 3 minutes due to multi-chain API processing (Mistral -> Embeddings -> ElevenLabs). Any API lag can cascade into hard user-facing failures.
