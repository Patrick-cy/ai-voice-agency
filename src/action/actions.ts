import { SessionMemory } from "../memory/sessionMemory.js";

export function handleIntent(intent: string, memory: SessionMemory): string {
  const name = memory.getName() ? `, ${memory.getName()}` : "";

  switch (intent) {
    case "policy_enquiry":
      return `Hello${name}, your insurance policy is currently active.`;
    case "report_claim":
      return `Okay${name}, I will create a claim report. Please describe the damage.`;
    case "schedule_appointment":
      return `Your appointment has been scheduled${name}.`;
    default:
      return `I'm sorry${name}, I didn't understand your request.`;
  }
}