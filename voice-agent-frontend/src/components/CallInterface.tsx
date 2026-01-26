/** Main call interface component */
import React, { useState } from "react";
import { useLiveKit } from "../hooks/useLiveKit";
import { AvatarDisplay } from "./AvatarDisplay";
import { ToolCallVisualizer } from "./ToolCallVisualizer";
import { ConversationSummary } from "./ConversationSummary";
import {
  Phone,
  PhoneOff,
  Mic,
  MicOff,
  Loader2,
  AlertCircle,
} from "lucide-react";

export const CallInterface: React.FC = () => {
  const {
    room,
    isConnected,
    isConnecting,
    transcript,
    toolCalls,
    conversationSummary,
    error,
    connect,
    disconnect,
    toggleMute,
    isMuted,
  } = useLiveKit();

  const [showSummary, setShowSummary] = useState(false);
  const [isAvatarReady, setIsAvatarReady] = useState(false);

  const handleStartCall = async () => {
    setIsAvatarReady(false); // Reset avatar ready state
    await connect();
  };

  const handleEndCall = async () => {
    await disconnect();
    if (conversationSummary) {
      setShowSummary(true);
    }
  };

  // Show summary when it's received
  React.useEffect(() => {
    if (conversationSummary) {
      setShowSummary(true);
    }
  }, [conversationSummary]);

  // Enable microphone when avatar is ready
  React.useEffect(() => {
    if (isConnected && isAvatarReady && room) {
      room.localParticipant.setMicrophoneEnabled(!isMuted).catch((err) => {
        console.error("Failed to enable microphone:", err);
      });
    } else if (isConnected && !isAvatarReady && room) {
      // Disable microphone while setting up
      room.localParticipant.setMicrophoneEnabled(false).catch((err) => {
        console.error("Failed to disable microphone:", err);
      });
    }
  }, [isConnected, isAvatarReady, room, isMuted]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Phone className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">
                Appointment Booking Agent
              </h1>
              <p className="text-sm text-gray-500">
                {isConnected && isAvatarReady ? (
                  <span className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                    Ready
                  </span>
                ) : isConnected && !isAvatarReady ? (
                  <span className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Setting up agent...
                  </span>
                ) : isConnecting ? (
                  <span className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Connecting...
                  </span>
                ) : (
                  "Ready to connect"
                )}
              </p>
            </div>
          </div>

          {isConnected && (
            <button
              onClick={handleEndCall}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2 font-semibold"
            >
              <PhoneOff className="w-5 h-5" />
              End Call
            </button>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Avatar Display - Left Column */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-4">
              <div className="aspect-video rounded-lg overflow-hidden">
                <AvatarDisplay 
                  room={room} 
                  onAvatarReady={setIsAvatarReady}
                />
              </div>
            </div>
          </div>

          {/* Controls and Status - Right Column */}
          <div className="space-y-4">
            {/* Call Controls */}
            {!isConnected && !isConnecting && (
              <div className="bg-white rounded-lg shadow-md p-6 text-center">
                <button
                  onClick={handleStartCall}
                  className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2 font-semibold text-lg"
                >
                  <Phone className="w-6 h-6" />
                  Start Call
                </button>
              </div>
            )}

            {/* Setting Up Agent Message */}
            {isConnected && !isAvatarReady && (
              <div className="bg-white rounded-lg shadow-md p-6 text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p className="text-gray-700 font-semibold mb-2">Setting up agent...</p>
                <p className="text-sm text-gray-500">Please wait while we prepare your avatar</p>
              </div>
            )}

            {/* Microphone Control */}
            {isConnected && isAvatarReady && (
              <div className="bg-white rounded-lg shadow-md p-4">
                <button
                  onClick={toggleMute}
                  disabled={!isAvatarReady}
                  className={`w-full px-4 py-3 rounded-lg transition-colors flex items-center justify-center gap-2 font-semibold ${
                    isMuted
                      ? "bg-red-100 text-red-700 hover:bg-red-200"
                      : "bg-green-100 text-green-700 hover:bg-green-200"
                  } ${!isAvatarReady ? "opacity-50 cursor-not-allowed" : ""}`}
                >
                  {isMuted ? (
                    <>
                      <MicOff className="w-5 h-5" />
                      Unmute
                    </>
                  ) : (
                    <>
                      <Mic className="w-5 h-5" />
                      Mute
                    </>
                  )}
                </button>
              </div>
            )}

            {/* Connection Status */}
            <div className="bg-white rounded-lg shadow-md p-4">
              <h3 className="text-sm font-semibold text-gray-600 mb-2">
                Status
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Connection:</span>
                  <span
                    className={
                      isConnected
                        ? "text-green-600 font-semibold"
                        : "text-gray-400"
                    }
                  >
                    {isConnected ? "Active" : "Inactive"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Agent:</span>
                  <span
                    className={
                      isAvatarReady
                        ? "text-green-600 font-semibold"
                        : isConnected
                        ? "text-yellow-600 font-semibold"
                        : "text-gray-400"
                    }
                  >
                    {isAvatarReady
                      ? "Ready"
                      : isConnected
                      ? "Setting up..."
                      : "Inactive"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Microphone:</span>
                  <span
                    className={
                      !isMuted && isAvatarReady
                        ? "text-green-600 font-semibold"
                        : "text-gray-400"
                    }
                  >
                    {!isAvatarReady
                      ? "Waiting..."
                      : isMuted
                      ? "Muted"
                      : "Active"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Tool Calls:</span>
                  <span className="text-gray-800 font-semibold">
                    {toolCalls.length}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Transcript */}
        {transcript.length > 0 && (
          <div className="mt-4 bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">
              Transcript
            </h3>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {transcript.map((line, index) => (
                <p key={index} className="text-sm text-gray-700">
                  {line}
                </p>
              ))}
            </div>
          </div>
        )}

        {/* Tool Activity */}
        <div className="mt-4 bg-white rounded-lg shadow-md p-6">
          <ToolCallVisualizer toolCalls={toolCalls} />
        </div>

        {/* Conversation Summary Modal */}
        {showSummary && conversationSummary && (
          <ConversationSummary
            summary={conversationSummary}
            onClose={() => setShowSummary(false)}
          />
        )}
      </div>
    </div>
  );
};
