const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface TranscribeResponse {
  transcript: string;
  language: string;
  duration?: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface ChatResponse {
  session_id: string;
  response: string;
  product_detected: string;
  intent_detected?: string;
  language_detected: string;
  suggest_ticket: boolean;
  conversation_history: ChatMessage[];
}

export interface CreateTicketPayload {
  session_id?: string;
  customer_name: string;
  phone_number: string;
  product: string;
  issue_description: string;
  intent?: string;
}

export interface TicketResponse {
  id: string;
  ticket_number: string;
  customer_name: string;
  phone_number: string;
  product: string;
  issue_description: string;
  intent?: string;
  status: string;
  created_at: string;
}

// ── Transcribe Audio ────────────────────────────
export async function transcribeAudio(blob: Blob): Promise<TranscribeResponse> {
  const form = new FormData();
  form.append("audio", blob, "audio.webm");
  const res = await fetch(`${API_URL}/api/transcribe`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Transcription failed");
  }
  return res.json();
}

// ── Chat ────────────────────────────────────────
export async function sendChat(
  sessionId: string,
  message: string,
  customerName?: string,
  phoneNumber?: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      customer_name: customerName,
      phone_number: phoneNumber,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Chat request failed");
  }
  return res.json();
}

// ── Create Service Ticket ────────────────────────
export async function createTicket(
  payload: CreateTicketPayload
): Promise<TicketResponse> {
  const res = await fetch(`${API_URL}/api/tickets`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to create ticket");
  }
  return res.json();
}

// ── List Tickets ────────────────────────────────
export async function listTickets(): Promise<TicketResponse[]> {
  const res = await fetch(`${API_URL}/api/tickets`);
  if (!res.ok) throw new Error("Failed to fetch tickets");
  return res.json();
}

// ── Helpers ─────────────────────────────────────
export function generateSessionId(): string {
  return `sess-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export const PRODUCT_LABELS: Record<string, string> = {
  ac: "Air Conditioner",
  washing_machine: "Washing Machine",
  microwave: "Microwave Oven",
  unknown: "Unknown",
};

export const PRODUCT_ICONS: Record<string, string> = {
  ac: "❄️",
  washing_machine: "🫧",
  microwave: "📡",
  unknown: "🔧",
};
