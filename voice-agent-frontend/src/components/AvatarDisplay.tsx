/** Avatar display component */
import React, { useEffect, useState, useRef } from "react";
import {
  Room,
  RoomEvent,
  RemoteParticipant,
  RemoteVideoTrack,
  Track,
} from "livekit-client";
import { User } from "lucide-react";

interface AvatarDisplayProps {
  room: Room | null;
  audioStream?: MediaStream;
  onAvatarReady?: (ready: boolean) => void;
}

export const AvatarDisplay: React.FC<AvatarDisplayProps> = ({
  room,
  audioStream,
  onAvatarReady,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [videoElement, setVideoElement] = useState<HTMLVideoElement | null>(
    null
  );
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const avatarTrackRef = useRef<RemoteVideoTrack | null>(null);

  useEffect(() => {
    if (!room) {
      return;
    }

    setIsLoading(true);
    setError(null);

    // Find avatar participant (Beyond Presence uses "bey-avatar-agent" as default identity)
    const findAvatarParticipant = (): RemoteParticipant | null => {
      const participants = Array.from(room.remoteParticipants.values());
      const avatarParticipant = participants.find(
        (p) =>
          p.identity === "bey-avatar-agent" ||
          p.name === "bey-avatar-agent" ||
          p.identity?.includes("avatar") ||
          p.name?.includes("avatar")
      );
      return avatarParticipant || null;
    };

    // Function to attach video track to video element
    const attachVideoTrack = (track: RemoteVideoTrack) => {
      if (track) {
        avatarTrackRef.current = track;

        // If video element is ready, attach immediately
        if (videoElement) {
          track.attach(videoElement);
          setIsLoading(false);
          setError(null);
          // Notify parent that avatar is ready
          if (onAvatarReady) {
            onAvatarReady(true);
          }
        } else {
          setIsLoading(false);
        }

        // Listen for track unmuted event (in case track was muted initially)
        track.on("unmuted", () => {
          if (videoElement) {
            track.attach(videoElement);
          }
        });
      }
    };

    // Check for existing avatar participant and tracks
    const checkForAvatar = () => {
      const avatarParticipant = findAvatarParticipant();
      if (avatarParticipant) {
        // Look for video track in publications
        let foundTrack = false;
        avatarParticipant.videoTrackPublications.forEach((pub) => {
          if (
            pub.track &&
            pub.track.kind === Track.Kind.Video &&
            pub.isSubscribed
          ) {
            attachVideoTrack(pub.track as RemoteVideoTrack);
            foundTrack = true;
          } else if (pub.trackSid && !pub.isSubscribed) {
            // Track exists but not subscribed yet - try to subscribe
            try {
              pub.setSubscribed(true);
            } catch (err: unknown) {
              console.error("Failed to subscribe to track:", err);
            }
          }
        });

        // If no tracks found, keep loading
        if (
          !foundTrack &&
          avatarParticipant.videoTrackPublications.size === 0
        ) {
          setIsLoading(true);
        } else if (!foundTrack) {
          setIsLoading(true);
        }
      } else {
        setIsLoading(true);
      }
    };

    // Initial check
    if (room.state === "connected") {
      checkForAvatar();
    }

    // Periodic check for avatar (in case it connects after initial check)
    const checkInterval = setInterval(() => {
      if (room.state === "connected" && !avatarTrackRef.current) {
        checkForAvatar();
      }
    }, 2000); // Check every 2 seconds

    // Listen for participant connected (avatar joins)
    const onParticipantConnected = (participant: RemoteParticipant) => {
      if (
        participant.identity === "bey-avatar-agent" ||
        participant.name === "bey-avatar-agent" ||
        participant.identity?.includes("avatar")
      ) {
        setIsLoading(true);
        // Check immediately when avatar connects
        setTimeout(() => checkForAvatar(), 500);
      }
    };

    // Listen for track subscribed (avatar video track)
    const onTrackSubscribed = (
      track: Track,
      publication: any,
      participant: RemoteParticipant
    ) => {
      // Check if this is from avatar participant
      const isAvatarParticipant =
        participant.identity === "bey-avatar-agent" ||
        participant.name === "bey-avatar-agent" ||
        participant.identity?.includes("avatar") ||
        participant.name?.includes("avatar");

      if (isAvatarParticipant && track.kind === Track.Kind.Video) {
        attachVideoTrack(track as RemoteVideoTrack);
      }
    };

    // Listen for track published (avatar publishes video)
    const onTrackPublished = (
      publication: any,
      participant: RemoteParticipant
    ) => {
      const isAvatarParticipant =
        participant.identity === "bey-avatar-agent" ||
        participant.name === "bey-avatar-agent" ||
        participant.identity?.includes("avatar") ||
        participant.name?.includes("avatar");

      if (isAvatarParticipant && publication.kind === Track.Kind.Video) {
        // Track will be automatically subscribed by LiveKit
        // If track is already available and subscribed, attach it
        if (publication.track && publication.isSubscribed) {
          attachVideoTrack(publication.track as RemoteVideoTrack);
        } else if (publication.trackSid) {
          // Track exists but not subscribed yet - ensure subscription
          if (!publication.isSubscribed) {
            try {
              publication.setSubscribed(true);
            } catch (err: unknown) {
              console.error("Failed to subscribe to published track:", err);
            }
          }
        }
      }
    };

    // Register event listeners
    room.on(RoomEvent.ParticipantConnected, onParticipantConnected);
    room.on(RoomEvent.TrackSubscribed, onTrackSubscribed);
    room.on(RoomEvent.TrackPublished, onTrackPublished);

    // Also listen for track unmuted events on individual tracks
    // This is handled via the track's own event system when we get the track

    // Cleanup
    return () => {
      clearInterval(checkInterval);
      room.off(RoomEvent.ParticipantConnected, onParticipantConnected);
      room.off(RoomEvent.TrackSubscribed, onTrackSubscribed);
      room.off(RoomEvent.TrackPublished, onTrackPublished);

      // Detach video track
      if (avatarTrackRef.current && videoRef.current) {
        avatarTrackRef.current.detach();
        avatarTrackRef.current = null;
      }
    };
  }, [room]);

  // Use callback ref to attach track when video element becomes available
  const videoCallbackRef = React.useCallback(
    (node: HTMLVideoElement | null) => {
      if (node) {
        setVideoElement(node);
        videoRef.current = node;
        // If we have a track but it's not attached yet, attach it now
        if (avatarTrackRef.current) {
          avatarTrackRef.current.attach(node);
          setIsLoading(false);
          // Notify parent that avatar is ready
          if (onAvatarReady) {
            onAvatarReady(true);
          }
        }
      } else {
        setVideoElement(null);
      }
    },
    []
  );

  // Effect to attach track when video element becomes ready
  React.useEffect(() => {
    if (videoElement && avatarTrackRef.current && !videoElement.srcObject) {
      avatarTrackRef.current.attach(videoElement);
      setIsLoading(false);
      // Notify parent that avatar is ready
      if (onAvatarReady) {
        onAvatarReady(true);
      }
    }
  }, [videoElement, onAvatarReady]);

  // Notify when avatar becomes unavailable
  React.useEffect(() => {
    if (!room || room.state !== "connected") {
      if (onAvatarReady) {
        onAvatarReady(false);
      }
    }
  }, [room, onAvatarReady]);

  if (error) {
    return (
      <div className="w-full h-full bg-red-50 rounded-lg flex items-center justify-center border-2 border-red-200">
        <div className="text-center">
          <p className="text-red-600 font-semibold">Avatar Error</p>
          <p className="text-sm text-red-500 mt-1">{error}</p>
        </div>
      </div>
    );
  }

  // Always render the video element (hidden if no track)
  // This ensures the ref is always available when tracks arrive
  const hasVideoTrack = avatarTrackRef.current !== null;

  return (
    <div className="w-full h-full bg-black rounded-lg overflow-hidden border-2 border-gray-300 relative">
      <video
        ref={videoCallbackRef}
        autoPlay
        playsInline
        muted={false}
        className="w-full h-full object-cover"
        style={{ transform: "scaleX(-1)" }} // Mirror for natural appearance
      />

      {/* Loading overlay */}
      {isLoading && !hasVideoTrack && (
        <div className="absolute inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-2"></div>
            <p className="text-gray-200">Loading avatar...</p>
          </div>
        </div>
      )}

      {/* Placeholder when no track */}
      {!hasVideoTrack && !isLoading && (
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
          <div className="text-center">
            <div className="bg-white rounded-full p-6 mb-4 inline-block shadow-lg">
              <User className="w-16 h-16 text-gray-400" />
            </div>
            <p className="text-gray-600 font-semibold">Avatar</p>
            <p className="text-sm text-gray-500 mt-1">
              {room?.state === "connected"
                ? "Avatar will appear here"
                : "Connect to start"}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
