/** Conversation summary component */
import React from "react";
import { ConversationSummary as ConversationSummaryType } from "../types";
import { X, Calendar, Clock, User } from "lucide-react";
import { CostBreakdown } from "./CostBreakdown";

interface ConversationSummaryProps {
  summary: ConversationSummaryType;
  onClose: () => void;
}

export const ConversationSummary: React.FC<ConversationSummaryProps> = ({ summary, onClose }) => {
  if (!summary) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full p-6">
          <p className="text-red-600">Error: No summary data available</p>
          <button
            onClick={onClose}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">Conversation Summary</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Summary Text */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Summary</h3>
            <div className="bg-gray-50 rounded-lg p-4 text-gray-700 whitespace-pre-wrap">
              {summary.summary || "No summary available"}
            </div>
          </div>

          {/* Appointments */}
          {summary.appointments && summary.appointments.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Appointments ({summary.appointments.length})
              </h3>
              <div className="space-y-2">
                {summary.appointments.map((apt) => (
                  <div
                    key={apt.id}
                    className="bg-blue-50 border border-blue-200 rounded-lg p-4"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        {apt.user_name && (
                          <p className="font-semibold text-gray-800 mb-1 flex items-center gap-2">
                            <User className="w-4 h-4" />
                            {apt.user_name}
                          </p>
                        )}
                        <p className="text-gray-700 flex items-center gap-2">
                          <Calendar className="w-4 h-4" />
                          {new Date(apt.appointment_date).toLocaleDateString("en-US", {
                            weekday: "long",
                            year: "numeric",
                            month: "long",
                            day: "numeric",
                          })}
                        </p>
                        <p className="text-gray-700 flex items-center gap-2 mt-1">
                          <Clock className="w-4 h-4" />
                          {new Date(`2000-01-01T${apt.appointment_time}`).toLocaleTimeString("en-US", {
                            hour: "numeric",
                            minute: "2-digit",
                          })}
                          {" "}({apt.duration_minutes} minutes)
                        </p>
                        {apt.notes && (
                          <p className="text-sm text-gray-600 mt-2 italic">
                            Notes: {apt.notes}
                          </p>
                        )}
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        apt.status === "confirmed"
                          ? "bg-green-100 text-green-800"
                          : apt.status === "cancelled"
                          ? "bg-red-100 text-red-800"
                          : "bg-gray-100 text-gray-800"
                      }`}>
                        {apt.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Cost Breakdown */}
          {summary.cost_breakdown && (
            <div>
              <CostBreakdown costBreakdown={summary.cost_breakdown} />
            </div>
          )}

          {/* Duration */}
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">
              Conversation Duration: <span className="font-semibold">{summary.duration_minutes.toFixed(1)} minutes</span>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
