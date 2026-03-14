import 'dotenv/config';
import * as fs from 'fs';
import path from 'path';
import { speechToText } from "./components/speechToText.js";
import { textToSpeech } from "./components/textToSpeech.js";
import { detectIntent } from "./llm/IntentDetector.js";
import { handleIntent } from "./action/actions.js";
import { SessionMemory } from "./memory/sessionMemory.js";
import { info, error } from "./utils/logger.js";

const memory = new SessionMemory();

async function runPipeline() {
  const totalStart = Date.now();
  let inputFile = process.env.INPUT_FILE || process.argv[2] || 'audio.ogg';


  if (!fs.existsSync(inputFile)) {
    const downloadsCandidate = path.join(process.env.HOME || '', 'Downloads', 'WhatsApp Ptt 2026-03-14 at 11.17.18.ogg');
    if (fs.existsSync(downloadsCandidate)) {
      inputFile = downloadsCandidate;
      info(`Input file not found, using Downloads file: ${inputFile}`);
    }
  }

  try {
  
    const text = await speechToText(inputFile);
    info(`User said: ${text}`);

    const intentStart = Date.now();
    const result = await detectIntent(text, memory.getHistory());
    if (result.extractedName) memory.setName(result.extractedName);
    info(`Intent Detection Latency: ${Date.now() - intentStart}ms`);

  
    const response = handleIntent(result.intent, memory);
    memory.addMessage("user", text);
    memory.addMessage("assistant", response);


    await textToSpeech(response);
    
    info(`Total Pipeline Latency: ${Date.now() - totalStart}ms`);
    info(`Final Response: ${response}`);
    
  } catch (err) {
    error("Pipeline Error:", err);
  }
}

runPipeline();