const resumeKnowledgeBase = `
You are chatting on Anand Prince Purty's portfolio website.

Profile:
- Name: Anand Prince Purty
- Location: Buffalo, New York
- Portfolio: andydoes.tech
- GitHub: github.com/z-anxprincex1
- LinkedIn: linkedin.com/in/anandprince1
- Email: anandprincepurty@gmail.com

Education:
- Master of Science in Computer Science, University at Buffalo SUNY, Jan 2024 - May 2025
- Bachelor of Engineering in Computer Science, Rajalakshmi Engineering College, Aug 2020 - May 2024

Experience:
- Community Dreams Foundation, Software Engineer (Backend & AI Systems), Sep 2025 - Present
- Built scalable backend data pipelines using Python and GCP.
- Used PostgreSQL, Supabase, Firebase, XGBoost, Next.js, Cloud Build, and Cloud Run.

Projects:
- UPASS DETECT [OBB]
- Multi-Modal Deep Learning for VQA
- VirtualEye - Drowning Detection
- Signease - Sign Language Detection
- Skin Disease Classification CNN
- Smart Door Lock with Face Detection
- Colabify
- PeekersNest
- Dental AI Matching API
- LLM-based Text-to-SQL

Behavior rules:
- Answer as Anand's portfolio assistant.
- Use only the information in this knowledge base and the user's question.
- Be warm, casual, concise, and helpful.
- Keep replies short by default.
- Speak in first person when describing Anand's work.
- If the answer is not in the knowledge base, say that briefly and suggest LinkedIn or email for more detail.
- Avoid inventing facts.
`.trim();

const allowedOrigins = new Set([
  "https://andydoes.tech",
  "http://localhost:8080",
  "https://lovable.dev/"
]);

type ChatHistoryItem = {
  role: "user" | "assistant";
  text: string;
};

type ChatRequestBody = {
  message?: unknown;
  history?: unknown;
};

function getCorsHeaders(origin?: string) {
  const allowOrigin =
    origin && allowedOrigins.has(origin) ? origin : "https://andydoes.tech";

  return {
    "Access-Control-Allow-Origin": allowOrigin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
  };
}

function normalizeHistory(history: unknown): ChatHistoryItem[] {
  if (!Array.isArray(history)) {
    return [];
  }

  return history
    .filter((item): item is ChatHistoryItem => {
      return Boolean(
        item &&
          typeof item === "object" &&
          (item as ChatHistoryItem).role &&
          ((item as ChatHistoryItem).role === "user" ||
            (item as ChatHistoryItem).role === "assistant") &&
          typeof (item as ChatHistoryItem).text === "string",
      );
    })
    .slice(-6);
}

export default async function handler(req: any, res: any) {
  const origin = req.headers?.origin;
  const corsHeaders = getCorsHeaders(origin);

  Object.entries(corsHeaders).forEach(([key, value]) => {
    res.setHeader(key, value);
  });

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed." });
  }

  try {
    const body = (req.body || {}) as ChatRequestBody;
    const message =
      typeof body.message === "string" ? body.message.trim() : "";
    const history = normalizeHistory(body.history);

    if (!message) {
      return res.status(400).json({ error: "Message is required." });
    }

    const apiKey = process.env.OPENAI_API_KEY;
    const model = process.env.OPENAI_MODEL || "gpt-5.4-mini";

    if (!apiKey) {
      return res.status(500).json({ error: "Missing OPENAI_API_KEY." });
    }

    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model,
        max_completion_tokens: 220,
        messages: [
          {
            role: "system",
            content: resumeKnowledgeBase,
          },
          ...history.map((item) => ({
            role: item.role,
            content: item.text,
          })),
          {
            role: "user",
            content: message,
          },
        ],
      }),
    });

    if (!response.ok) {
      const text = await response.text();
      return res.status(500).json({ error: text || "OpenAI request failed." });
    }

    const data = await response.json();
    const content = data?.choices?.[0]?.message?.content;

    const reply =
      typeof content === "string"
        ? content.trim()
        : Array.isArray(content)
          ? content
              .map((part: { text?: string }) => part?.text || "")
              .join("\n\n")
              .trim()
          : "";

    if (!reply) {
      return res
        .status(500)
        .json({ error: "Assistant returned empty response." });
    }

    return res.status(200).json({ reply });
  } catch (error: any) {
    return res.status(500).json({
      error: error?.message || "Something went wrong.",
    });
  }
}
