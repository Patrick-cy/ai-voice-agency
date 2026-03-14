import OpenAI from "openai";
import { Message } from "../memory/sessionMemory.js";

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export interface IntentResult {
  intent: "policy_enquiry" | "report_claim" | "schedule_appointment" | "fallback";
  extractedName: string | null;
}

export async function detectIntent(text: string, history: Message[]): Promise<IntentResult> {
  const context = history.map(m => `${m.role}: ${m.content}`).join("\n");

  const prompt = `
    You are an intent classifier for an insurance AI.
    Analyze the user message and history.
    
    Intents: policy_enquiry, report_claim, schedule_appointment, fallback.
    Extraction: If the user provides their name, extract it.

    Return JSON: { "intent": "string", "extractedName": "string|null" }

    History: ${context}
    User: ${text}
  `;

  const completion = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "system", content: "Return only JSON." }, { role: "user", content: prompt }],
    response_format: { type: "json_object" }
  });

  const raw = completion?.choices?.[0]?.message?.content ?? "{}";
  let res: any = {};
  try {
    res = JSON.parse(raw);
  } catch (e) {
    
  }

  return {
    intent: res.intent || "fallback",
    extractedName: res.extractedName || null,
  };
}