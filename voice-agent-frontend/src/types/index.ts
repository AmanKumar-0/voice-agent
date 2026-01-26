/** Type definitions for the voice agent frontend */

export interface ToolCall {
  tool_name: string;
  parameters: Record<string, any>;
  status: "in_progress" | "success" | "error";
  result?: any;
  timestamp: string;
}

export interface ConversationSummary {
  summary: string;
  appointments: Appointment[];
  tool_calls: ToolCall[];
  cost_breakdown: CostBreakdown;
  duration_minutes: number;
  transcript: string[];
}

export interface Appointment {
  id: string;
  contact_number: string;
  user_name?: string;
  appointment_date: string;
  appointment_time: string;
  duration_minutes: number;
  status: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CostBreakdown {
  deepgram_stt: {
    minutes: number;
    rate_per_minute: number;
    cost: number;
  };
  llm: {
    estimated_tokens: number;
    rate_per_1k_tokens: number;
    cost: number;
  };
  cartesia_tts: {
    estimated_characters: number;
    rate_per_char: number;
    cost: number;
  };
  avatar: {
    minutes: number;
    rate_per_minute: number;
    cost: number;
  };
  total: number;
}

export interface WebSocketEvent {
  type: "tool_call" | "conversation_summary" | "transcript" | "conversation_ended";
  timestamp: string;
  [key: string]: any;
}
