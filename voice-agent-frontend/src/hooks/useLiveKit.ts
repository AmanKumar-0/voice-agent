/** Custom hook for LiveKit room management */
import React, { useState, useEffect, useCallback } from "react";
import {
  Room,
  RoomEvent,
  RemoteParticipant,
  DataPacket_Kind,
  RemoteAudioTrack,
  Track,
  TrackEventCallbacks,
} from "livekit-client";
import { ToolCall, WebSocketEvent, ConversationSummary } from "../types";
import { generateToken, fetchTokenFromBackend } from "../services/livekit";

export interface UseLiveKitReturn {
  room: Room | null;
  isConnected: boolean;
  isConnecting: boolean;
  transcript: string[];
  toolCalls: ToolCall[];
  conversationSummary: ConversationSummary | null;
  error: string | null;
  connect: (roomName?: string, participantName?: string) => Promise<void>;
  disconnect: () => Promise<void>;
  toggleMute: () => void;
  isMuted: boolean;
}

export function useLiveKit(): UseLiveKitReturn {
  const [room, setRoom] = useState<Room | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [transcript, setTranscript] = useState<string[]>([]);
  const [toolCalls, setToolCalls] = useState<ToolCall[]>([]);
  const [conversationSummary, setConversationSummary] =
    useState<ConversationSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isMuted, setIsMuted] = useState(false);

  // Track processed messages to prevent duplicates
  const processedMessagesRef = React.useRef<Set<string>>(new Set());

  const connect = useCallback(
    async (roomName = "appointment-room", participantName = "user") => {
      if (isConnecting || isConnected) {
        return;
      }

      setIsConnecting(true);
      setError(null);

      try {
        // Generate or fetch token
        const tokenData = await fetchTokenFromBackend(
          roomName,
          participantName
        );

        // Create room with options to auto-subscribe to video tracks
        const newRoom = new Room({
          // Auto-subscribe to video tracks by default
          adaptiveStream: false,
          dynacast: false,
        });

        // Set up event listeners before connecting
        // Note: These listeners are automatically cleaned up when room disconnects
        const onConnected = () => {
          setIsConnected(true);
          setIsConnecting(false);
        };

        const onDisconnected = () => {
          setIsConnected(false);
          setRoom(null);
        };

        const onDataReceived = (
          payload: Uint8Array,
          participant?: RemoteParticipant,
          kind?: DataPacket_Kind
        ) => {
          try {
            const decoder = new TextDecoder();
            const text = decoder.decode(payload);
            const data: WebSocketEvent = JSON.parse(text);

            if (data.type === "tool_call") {
              const toolCall: ToolCall = {
                tool_name: data.tool_name,
                parameters: data.parameters || {},
                status: data.status,
                result: data.result,
                timestamp: data.timestamp,
              };

              setToolCalls((prev) => {
                // Update existing tool call or add new one
                const existingIndex = prev.findIndex(
                  (tc) =>
                    tc.tool_name === toolCall.tool_name &&
                    tc.timestamp === toolCall.timestamp
                );

                if (existingIndex >= 0) {
                  const updated = [...prev];
                  updated[existingIndex] = toolCall;
                  return updated;
                }

                return [...prev, toolCall];
              });
            } else if (data.type === "transcript") {
              // Handle transcript updates with deduplication
              const role = (data as any).role;
              const text = (data as any).text;
              const timestamp = (data as any).timestamp;

              if (role && text) {
                // Create unique message ID using timestamp and text
                const messageId = `${timestamp || Date.now()}-${role}-${text}`;

                // Check if we've already processed this exact message
                if (processedMessagesRef.current.has(messageId)) {
                  console.debug(
                    "Skipping duplicate transcript (already processed):",
                    text
                  );
                  return;
                }

                // Mark as processed
                processedMessagesRef.current.add(messageId);

                const transcriptLine = `${
                  role === "user" ? "User" : "Agent"
                }: ${text}`;

                setTranscript((prev) => {
                  // Double-check: also check if this exact line already exists in transcript
                  if (prev.includes(transcriptLine)) {
                    console.debug(
                      "Skipping duplicate transcript (in array):",
                      transcriptLine
                    );
                    return prev;
                  }
                  return [...prev, transcriptLine];
                });
              }
            } else if (data.type === "conversation_summary") {
              // Type guard to ensure data has all required ConversationSummary fields
              if (
                "summary" in data &&
                "appointments" in data &&
                "tool_calls" in data &&
                "cost_breakdown" in data &&
                "duration_minutes" in data &&
                "transcript" in data
              ) {
                setConversationSummary(data as unknown as ConversationSummary);
              } else {
                console.warn(
                  "Received conversation_summary event but data is incomplete:",
                  data
                );
              }
            }
          } catch (err) {
            console.error("Error parsing WebSocket data:", err);
          }
        };

        // Register event listeners
        newRoom.on(RoomEvent.Connected, onConnected);
        newRoom.on(RoomEvent.Disconnected, onDisconnected);
        newRoom.on(RoomEvent.DataReceived, onDataReceived);

        // Listen for remote track subscriptions (agent audio)
        const onTrackSubscribed = (
          track: Track,
          publication: any,
          participant: RemoteParticipant
        ) => {
          // If it's an audio track, attach it to an audio element to play it
          if (track.kind === Track.Kind.Audio) {
            // Create audio element for playback
            const audioElement = document.createElement("audio");
            audioElement.autoplay = true;
            // @ts-expect-error: playsInline is not officially defined on HTMLAudioElement, but is supported by browsers
            audioElement.playsInline = true;
            audioElement.style.display = "none"; // Hide the audio element
            audioElement.setAttribute("data-livekit-agent-audio", "true");
            document.body.appendChild(audioElement);

            // Attach the track to the audio element
            (track as RemoteAudioTrack).attach(audioElement);

            // Try to play (some browsers require user interaction first)
            audioElement.play().catch((err) => {
              console.warn(
                "Could not autoplay audio (browser restriction):",
                err
              );
            });

            // Clean up when track is unsubscribed
            track.on("unsubscribed" as keyof TrackEventCallbacks, () => {
              (track as RemoteAudioTrack).detach();
              if (audioElement.parentNode) {
                audioElement.parentNode.removeChild(audioElement);
              }
            });
          }
        };

        newRoom.on(RoomEvent.TrackSubscribed, onTrackSubscribed);

        // Listen for track published by remote participants (agent)
        const onTrackPublished = (
          publication: any,
          participant: RemoteParticipant
        ) => {
          // Track subscriptions are handled automatically by LiveKit
        };
        newRoom.on(RoomEvent.TrackPublished, onTrackPublished);

        // Connect to room
        await newRoom.connect(tokenData.url, tokenData.token);

        // Don't enable microphone immediately - wait for avatar to be ready
        // Microphone will be enabled when avatar is ready (handled by CallInterface)
        // await newRoom.localParticipant.setMicrophoneEnabled(!isMuted);

        setRoom(newRoom);
      } catch (err: any) {
        console.error("Error connecting to LiveKit:", err);
        setError(err.message || "Failed to connect");
        setIsConnecting(false);
      }
    },
    [isConnecting, isConnected, isMuted]
  );

  const disconnect = useCallback(async () => {
    if (room) {
      // Clean up any audio elements we created
      const audioElements = document.querySelectorAll(
        "audio[data-livekit-agent-audio]"
      );
      audioElements.forEach((el) => el.remove());

      await room.disconnect();
      setRoom(null);
      setIsConnected(false);
      setTranscript([]);
      setToolCalls([]);
      setConversationSummary(null);
      // Clear processed messages tracking
      processedMessagesRef.current.clear();
    }
  }, [room]);

  const toggleMute = useCallback(async () => {
    if (room) {
      const newMutedState = !isMuted;
      await room.localParticipant.setMicrophoneEnabled(!newMutedState);
      setIsMuted(newMutedState);
    }
  }, [room, isMuted]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (room) {
        room.disconnect();
      }
    };
  }, [room]);

  return {
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
  };
}
