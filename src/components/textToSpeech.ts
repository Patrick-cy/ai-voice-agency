import * as fs from "fs";
import OpenAI from "openai";
import { info } from "../utils/logger.js";

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function textToSpeech(text: string): Promise<void> {
  const start = Date.now();

  const mp3 = await client.audio.speech.create({
    model: "tts-1",
    voice: "alloy",
    input: text,
  });

  const buffer = Buffer.from(await mp3.arrayBuffer());
  fs.writeFileSync("response.mp3", buffer);

  const latency = Date.now() - start;
  info(`TTS Latency: ${latency}ms`); // Required by Task 1 
}