/** Tool call visualizer component */
import React from "react";
import { ToolCall } from "../types";
import {
  CheckCircle2,
  XCircle,
  Loader2,
  Phone,
  Calendar,
  Clock,
  UserX,
  Edit,
  Power,
} from "lucide-react";

interface ToolCallVisualizerProps {
  toolCalls: ToolCall[];
}

const toolIcons: Record<string, React.ReactNode> = {
  identify_user: <Phone className="w-5 h-5" />,
  fetch_slots: <Calendar className="w-5 h-5" />,
  book_appointment: <CheckCircle2 className="w-5 h-5" />,
  retrieve_appointments: <Calendar className="w-5 h-5" />,
  cancel_appointment: <UserX className="w-5 h-5" />,
  modify_appointment: <Edit className="w-5 h-5" />,
  end_conversation: <Power className="w-5 h-5" />,
};

const toolNames: Record<string, string> = {
  identify_user: "Identify User",
  fetch_slots: "Fetch Available Slots",
  book_appointment: "Book Appointment",
  retrieve_appointments: "Retrieve Appointments",
  cancel_appointment: "Cancel Appointment",
  modify_appointment: "Modify Appointment",
  end_conversation: "End Conversation",
};

export const ToolCallVisualizer: React.FC<ToolCallVisualizerProps> = ({
  toolCalls,
}) => {
  if (toolCalls.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 text-center text-gray-500">
        No tool activity yet. Start a conversation to see tool calls.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-gray-800 mb-3">
        Tool Activity
      </h3>
      {toolCalls.map((toolCall, index) => (
        <ToolCallCard key={index} toolCall={toolCall} />
      ))}
    </div>
  );
};

const ToolCallCard: React.FC<{ toolCall: ToolCall }> = ({ toolCall }) => {
  const { tool_name, parameters, status, result } = toolCall;

  const getStatusIcon = () => {
    switch (status) {
      case "success":
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case "error":
        return <XCircle className="w-5 h-5 text-red-500" />;
      case "in_progress":
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <Loader2 className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case "success":
        return "border-green-200 bg-green-50";
      case "error":
        return "border-red-200 bg-red-50";
      case "in_progress":
        return "border-blue-200 bg-blue-50";
      default:
        return "border-gray-200 bg-gray-50";
    }
  };

  return (
    <div className={`border rounded-lg p-4 ${getStatusColor()} transition-all`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="text-gray-600">
            {toolIcons[tool_name] || <Clock className="w-5 h-5" />}
          </div>
          <div>
            <h4 className="font-semibold text-gray-800">
              {toolNames[tool_name] || tool_name}
            </h4>
            <p className="text-xs text-gray-500">
              {new Date(toolCall.timestamp).toLocaleTimeString()}
            </p>
          </div>
        </div>
        {getStatusIcon()}
      </div>

      {Object.keys(parameters).length > 0 && (
        <div className="mt-2 mb-2">
          <p className="text-xs font-medium text-gray-600 mb-1">Parameters:</p>
          <div className="bg-white rounded p-2 text-xs font-mono text-gray-700">
            <pre>{JSON.stringify(parameters, null, 2)}</pre>
          </div>
        </div>
      )}
      {/* 
      {result && (
        <div className="mt-2">
          <p className="text-xs font-medium text-gray-600 mb-1">
            {status === "success" ? "Result:" : "Error:"}
          </p>
          <div
            className={`rounded p-2 text-xs ${
              status === "success" ? "bg-white" : "bg-red-100"
            }`}
          >
            {status === "success" ? (
              <div className="text-gray-700">
                {result.message && <p className="mb-1">{result.message}</p>}
                {result.summary && (
                  <p className="font-semibold">{result.summary}</p>
                )}
                {result.appointment && (
                  <div className="mt-2 p-2 bg-gray-50 rounded">
                    <p className="font-semibold">Appointment Details:</p>
                    <p className="text-xs">
                      {JSON.stringify(result.appointment, null, 2)}
                    </p>
                  </div>
                )}
                {result.slots && (
                  <p className="text-xs text-gray-600">
                    Found {result.count || result.slots.length} available slots
                  </p>
                )}
              </div>
            ) : (
              <p className="text-red-700">{result.error || "Unknown error"}</p>
            )}
          </div>
        </div>
      )} */}
    </div>
  );
};
