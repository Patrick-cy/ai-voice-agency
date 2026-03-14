import * as fs from "fs";
import OpenAI from "openai";
import { info } from "../utils/logger.js";

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export async function speechToText(audioFile: string): Promise<string> {
  const start = Date.now();
  
  const transcription = await client.audio.transcriptions.create({
    file: fs.createReadStream(audioFile),
    model: "whisper-1",
  });

  const latency = Date.now() - start;
  info(`STT Latency: ${latency}ms`); // Required by Task 1 
  
  return transcription.text;
}