/** LiveKit service for token generation and room management */
const LIVEKIT_URL = process.env.REACT_APP_LIVEKIT_URL || "";

export interface TokenResponse {
  token: string;
  url: string;
}

/**
 * Generate a LiveKit access token for a user
 * NOTE: Token generation should ALWAYS be done on the backend for security.
 * This function is a fallback and should not be used in production.
 */
export async function generateToken(
  roomName: string,
  participantName: string
): Promise<TokenResponse> {
  // Token generation requires server-side SDK (livekit-server-sdk)
  // This should never be done client-side in production
  // Always use fetchTokenFromBackend instead
  console.warn(
    "generateToken: Client-side token generation is not secure. Use fetchTokenFromBackend instead."
  );

  // Fallback: try to get from backend
  return fetchTokenFromBackend(roomName, participantName);
}

/**
 * Alternative: Fetch token from backend
 */
export async function fetchTokenFromBackend(
  roomName: string,
  participantName: string
): Promise<TokenResponse> {
  const backendUrl =
    process.env.REACT_APP_BACKEND_URL || "http://localhost:8080";

  try {
    const response = await fetch(`${backendUrl}/api/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        room_name: roomName,
        participant_name: participantName,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Token API error (${response.status}):`, errorText);
      throw new Error(`Failed to fetch token: ${response.status} ${errorText}`);
    }

    const data = await response.json();
    return {
      token: data.token,
      url: data.url || LIVEKIT_URL,
    };
  } catch (error) {
    console.error("Error fetching token from backend:", error);
    throw error; // Re-throw so caller can handle it
  }
}
