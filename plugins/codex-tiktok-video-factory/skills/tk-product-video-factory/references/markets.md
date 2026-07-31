# TikTok Shop market catalog

Do not infer the available TikTok Shop markets from examples in a user prompt. Read
`scripts/market_catalog.py`, which records the verification date, official source groups, default
language, supported content-language choices, currency, and Edge TTS voices.

TikTok updates regional help pages and launch announcements at different times. Treat the catalog
as versioned data, not permanent truth. When the user asks for a market absent from the catalog:

1. Verify availability using current official TikTok Shop sources.
2. Distinguish TikTok advertising availability from TikTok Shop availability.
3. Add the market only after verification, recording source and date.
4. Ask for the main content language when the market commonly uses several languages.

Market selection and content language are separate. For example, Belgium may use Dutch or French;
Singapore may use English, Chinese, Malay, or Tamil. Use the market default for zero-configuration
onboarding, but preserve an explicit store-level override.
