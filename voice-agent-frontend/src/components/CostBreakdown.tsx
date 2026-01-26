/** Cost breakdown component */
import React from "react";
import { CostBreakdown as CostBreakdownType } from "../types";
import { DollarSign } from "lucide-react";

interface CostBreakdownProps {
  costBreakdown: CostBreakdownType;
}

export const CostBreakdown: React.FC<CostBreakdownProps> = ({ costBreakdown }) => {
  const lineItems = [
    {
      label: "Deepgram STT",
      value: costBreakdown.deepgram_stt,
      unit: "minutes",
    },
    {
      label: "OpenAI LLM",
      value: costBreakdown.llm,
      unit: "tokens",
    },
    {
      label: "Cartesia TTS",
      value: costBreakdown.cartesia_tts,
      unit: "characters",
    },
    {
      label: "Avatar",
      value: costBreakdown.avatar,
      unit: "minutes",
    },
  ];

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-4">
        <DollarSign className="w-5 h-5 text-gray-600" />
        <h3 className="text-lg font-semibold text-gray-800">Cost Breakdown</h3>
      </div>
      
      <div className="space-y-3 mb-4">
        {lineItems.map((item, index) => (
          <div key={index} className="flex justify-between items-center py-2 border-b border-gray-100">
            <div>
              <p className="text-sm font-medium text-gray-700">{item.label}</p>
              <p className="text-xs text-gray-500">
                {item.value[item.unit as keyof typeof item.value]?.toFixed(2) || 0} {item.unit} × 
                ${item.value[`rate_per_${item.unit === "minutes" ? "minute" : item.unit === "tokens" ? "1k_tokens" : "char"}` as keyof typeof item.value]?.toFixed(5) || 0}
              </p>
            </div>
            <p className="text-sm font-semibold text-gray-800">
              ${item.value.cost.toFixed(4)}
            </p>
          </div>
        ))}
      </div>
      
      <div className="pt-3 border-t-2 border-gray-300">
        <div className="flex justify-between items-center">
          <p className="text-lg font-bold text-gray-900">Total</p>
          <p className="text-xl font-bold text-blue-600">
            ${costBreakdown.total.toFixed(4)}
          </p>
        </div>
      </div>
    </div>
  );
};
