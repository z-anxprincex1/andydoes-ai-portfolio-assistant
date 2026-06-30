# AndyDoes AI Portfolio Assistant

An LLM-powered portfolio chat API for [andydoes.tech](https://andydoes.tech). It answers visitor questions about Anand Prince Purty's background, projects, skills, and experience using a curated Markdown knowledge base.

The project is intentionally small, but it demonstrates practical prompt engineering: grounded context, assistant behavior rules, bounded chat history, fallback behavior, and manual prompt evaluation cases.

## How it works

1. A frontend sends a `POST` request to the Vercel API route at `api/chat.ts`.
2. The API validates the user message and keeps only the last 6 chat history items.
3. The assistant loads `knowledge-base/portfolio.md` from disk.
4. That Markdown file is sent as the system message to OpenAI's Chat Completions API.
5. The user message and recent history are appended after the system context.
6. OpenAI returns a response, and the API sends back a clean JSON reply.

The assistant is designed to answer only from the knowledge base. If a visitor asks about something that is not included, it should briefly say that information is unavailable and suggest LinkedIn or email for more detail.

## Prompt and knowledge base

The assistant's facts and behavior rules live in:

```text
knowledge-base/portfolio.md
```

This file includes:

- profile and contact details
- education
- technical skills
- work experience
- hackathons and achievements
- project summaries
- prompt-engineering relevance
- tone, grounding, and safety rules

Keeping this content separate from `api/chat.ts` makes the project easier to maintain. Portfolio facts can be updated without changing the API logic.

## API behavior

The API route:

- supports `POST` and `OPTIONS`
- applies CORS for allowed origins
- requires a non-empty `message`
- accepts optional chat `history`
- limits history to the 6 most recent items
- uses `OPENAI_MODEL` when provided
- defaults to `gpt-5.4-mini`
- limits responses with `max_completion_tokens: 220`

Example request body:

```json
{
  "message": "Tell me about Anand's prompt engineering experience.",
  "history": [
    {
      "role": "user",
      "text": "What AI projects has Anand built?"
    },
    {
      "role": "assistant",
      "text": "I've worked on Quizzly, a Text-to-SQL engine, PeekersNest, and this portfolio assistant."
    }
  ]
}
```

Example response:

```json
{
  "reply": "I've worked with OpenAI API, Google GenAI/Gemini, schema-aware prompts, response formats, prompt security, and eval-style iteration. A few relevant projects are my Text-to-SQL engine, Quizzly, PeekersNest, and this portfolio assistant."
}
```

## Prompt evaluation

Manual prompt checks are documented in:

```text
PROMPT_EVALS.md
```

The eval cases cover:

- groundedness
- hallucination resistance
- casual and friendly tone
- fallback behavior
- follow-up handling
- project-specific retrieval
- prompt-injection resistance

## Project structure

```text
api/
  chat.ts                 # Vercel serverless chat endpoint
knowledge-base/
  portfolio.md            # Assistant context and behavior rules
PROMPT_EVALS.md           # Manual prompt evaluation cases
vercel.json               # Includes knowledge-base files in the function bundle
```

## Environment variables

Create a local `.env` file or configure these in Vercel:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5.4-mini
```

`OPENAI_MODEL` is optional. The API defaults to `gpt-5.4-mini` if it is not set.

## Local development

Install dependencies:

```bash
npm install
```

Run locally with Vercel:

```bash
vercel dev
```

## Deployment

Deploy through Vercel and add the environment variables in Project Settings.

`vercel.json` includes the Markdown knowledge base with the serverless function:

```json
{
  "functions": {
    "api/chat.ts": {
      "includeFiles": "knowledge-base/**"
    }
  }
}
```

## Security notes

- Keep real API keys in Vercel environment variables.
- Do not commit `.env`.
- Use `.env.example` for placeholder values if sharing setup instructions.
- The assistant prompt tells the model not to reveal secrets or unsupported internal details.
