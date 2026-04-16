# TESTING.md

## Test Environments & Coverage

Currently, formal unit tests (`pytest`) are not fully established in the MVP structure. The codebase relies heavily on experimental scripts within `scratch/`.

## Important Scratch Scripts
- **`scratch/brutal_verify_levels.py`**: Manual verifier to compare simplification levels (1/2/3). Ensuring prompt injections translate appropriately into output formats.
- **`scratch/test_tts.py`**: Manually verify text-to-speech fallback behaviour (ElevenLabs -> gTTS switchover). 
- **`scratch/test_mp_rag.py`**: STALE. Currently broken. Tries to query missing functions (`query_guidelines`); provides a warning representation of an outdated interface.

## System Diagnostics
- Health is determined via the `GET /api/health` endpoint which explicitly flags if critical integration credentials (`MISTRAL_API_KEY`) are active within the system instance.
