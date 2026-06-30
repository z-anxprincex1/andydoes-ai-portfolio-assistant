# andydoes-chat-api

Minimal Vercel chat API for `andydoes.tech`.

## Knowledge base
The assistant's portfolio facts and behavior rules live in `knowledge-base/portfolio.md`.
Vercel includes this file with the serverless function through `vercel.json`.

## Env vars
- `OPENAI_API_KEY`
- `OPENAI_MODEL` optional, defaults to `gpt-5.4-mini`

## Prompt evaluation
See `PROMPT_EVALS.md` for manual prompt-engineering checks covering groundedness, hallucination resistance, tone, fallback behavior, and follow-up handling.

## Local
Use `vercel dev`

## Deploy
Import repo into Vercel and add env vars in project settings.
