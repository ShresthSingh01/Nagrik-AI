# INTEGRATIONS.md

## 1. Mistral API
- **Document Processing (OCR):** The system uploads documents to Mistral's file API and queries the OCR endpoint using a model defined in `MISTRAL_OCR_MODEL` (default: `mistral-ocr-latest`). This turns PDFs and images into markdown blocks.
- **Simplification / Generation (LLM):** Uses the `MISTRAL_CHAT_MODEL` to summarize pages, classify content into 7 page types, simplify text based on user profiles and levels, and power the “Ask AI” functionality.
- **Embeddings:** Mistral embeddings are used to index `data/civic_guidelines.json` for grounded context retrieval.

## 2. Text-to-Speech (TTS)
- **ElevenLabs:** Primary provider for high-quality TTS audio (if `ELEVENLABS_API_KEY` is provided). Used for document summaries and specific field audio reading.
- **gTTS (Google TTS):** A built-in programmatic fallback when ElevenLabs fails or is unconfigured. Generated `.mp3` files are saved locally.

## Environment Variables Needed
- `MISTRAL_API_KEY` (Required)
- `MISTRAL_CHAT_MODEL` (Required)
- `MISTRAL_OCR_MODEL`, `MISTRAL_BASE_URL`, `ELEVENLABS_API_KEY` (Optional)
