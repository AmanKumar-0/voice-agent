# Voice Agent Frontend

A modern React + TypeScript web application for interacting with the AI voice agent for appointment booking. Features real-time voice conversation, avatar display, tool call visualization, and conversation summaries.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Configuration](#configuration)
- [Components](#components)
- [Hooks](#hooks)
- [Services](#services)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Features

- ✅ **Real-time voice conversation** via LiveKit WebSocket
- ✅ **Avatar display** with Beyond Presence integration
- ✅ **Tool call visualization** with real-time updates
- ✅ **Conversation summary** displayed at call end
- ✅ **Cost breakdown** showing usage and costs per service
- ✅ **Modern UI** with TailwindCSS
- ✅ **Responsive design** for desktop and mobile
- ✅ **Microphone controls** with mute/unmute
- ✅ **Connection status** indicators
- ✅ **Loading states** for better UX

## Project Structure

```
voice-agent-frontend/
├── src/
│   ├── components/
│   │   ├── AvatarDisplay.tsx          # Avatar video display
│   │   ├── CallInterface.tsx          # Main call UI
│   │   ├── ConversationSummary.tsx    # End-of-call summary modal
│   │   ├── CostBreakdown.tsx          # Cost analysis component
│   │   └── ToolCallVisualizer.tsx     # Tool call visualization
│   ├── hooks/
│   │   └── useLiveKit.ts              # LiveKit connection hook
│   ├── services/
│   │   ├── avatar.ts                  # Avatar service utilities
│   │   └── livekit.ts                 # LiveKit token generation
│   ├── types/
│   │   └── index.ts                   # TypeScript type definitions
│   ├── App.tsx                        # Main app component
│   └── index.tsx                      # Entry point
├── public/
│   └── index.html                     # HTML template
├── package.json                       # Dependencies
├── tailwind.config.js                 # TailwindCSS configuration
└── tsconfig.json                      # TypeScript configuration
```

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. **Install dependencies:**

   ```bash
   npm install
   ```

2. **Configure environment variables:**

   Create `.env.local` in the root directory:

   ```env
   REACT_APP_BACKEND_URL=http://localhost:8080
   REACT_APP_LIVEKIT_URL=wss://your-livekit-server.com
   REACT_APP_LIVEKIT_API_KEY=your-api-key
   REACT_APP_LIVEKIT_API_SECRET=your-api-secret
   REACT_APP_BEYOND_PRESENCE_KEY=your-beyond-presence-key
   ```

3. **Start development server:**

   ```bash
   npm start
   ```

   The app will open at `http://localhost:3000`

4. **Build for production:**

   ```bash
   npm run build
   ```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `REACT_APP_BACKEND_URL` | Backend API URL | Yes |
| `REACT_APP_LIVEKIT_URL` | LiveKit WebSocket URL | Yes |
| `REACT_APP_LIVEKIT_API_KEY` | LiveKit API key | Yes |
| `REACT_APP_LIVEKIT_API_SECRET` | LiveKit API secret | Yes |
| `REACT_APP_BEYOND_PRESENCE_KEY` | Beyond Presence API key (for avatar) | Optional |

### Backend Integration

The frontend communicates with the backend API for:
- **Token generation**: `POST /api/token` - Get LiveKit access token
- **Health check**: `GET /health` - Verify backend is running

## Components

### CallInterface

Main component that orchestrates the call experience.

**Features:**
- Start/End call buttons
- Connection status display
- Microphone controls (mute/unmute)
- Layout management for avatar and controls
- Agent setup state ("Setting up agent...")

**Props:** None (uses hooks for state management)

### AvatarDisplay

Displays the avatar video stream from Beyond Presence.

**Features:**
- Real-time video track subscription
- Loading states while avatar connects
- Error handling with fallback UI
- Placeholder when avatar is inactive
- Automatic track attachment/detachment

**Props:**
- `room`: LiveKit Room instance
- `onAvatarReady`: Callback when avatar is ready

### ToolCallVisualizer

Real-time visualization of tool calls made by the agent.

**Features:**
- Shows tool name, parameters, and status
- Visual indicators (loading, success, error)
- Result preview
- Timestamps
- Auto-scroll to latest tool call

**Props:**
- `toolCalls`: Array of tool call objects

### ConversationSummary

Modal displayed at call end with full conversation details.

**Features:**
- Full conversation summary text
- List of appointments created/modified
- Cost breakdown per service
- Duration information
- Transcript display
- Close button to dismiss

**Props:**
- `summary`: Summary object with all conversation data
- `onClose`: Callback to close modal

### CostBreakdown

Detailed cost analysis component.

**Features:**
- Per-service breakdown (STT, LLM, TTS, Avatar)
- Total cost calculation
- Usage metrics (minutes, tokens, characters)
- Visual cost indicators

**Props:**
- `costBreakdown`: Cost breakdown object

## Hooks

### useLiveKit

Custom hook managing LiveKit connection and state.

**Features:**
- Room connection/disconnection
- WebSocket event handling
- Transcript tracking (user and assistant messages)
- Tool call state management
- Microphone control
- Connection status tracking

**Returns:**
```typescript
{
  room: Room | null,
  isConnected: boolean,
  isMuted: boolean,
  transcript: Array<{role: string, text: string, timestamp: string}>,
  toolCalls: Array<ToolCall>,
  conversationSummary: ConversationSummary | null,
  connect: (roomName: string, participantName: string) => Promise<void>,
  disconnect: () => Promise<void>,
  toggleMute: () => Promise<void>
}
```

## Services

### livekit.ts

Token generation and room utilities.

**Functions:**
- `generateToken(roomName, participantName)`: Generate LiveKit access token from backend
- `getLiveKitUrl()`: Get LiveKit WebSocket URL from environment

### avatar.ts

Avatar service integration utilities.

**Functions:**
- `initializeBeyondPresence()`: Initialize Beyond Presence SDK (if needed)
- Service detection and configuration

## Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **LiveKit Client SDK** - Real-time communication
- **TailwindCSS** - Utility-first CSS framework
- **Lucide React** - Icon library

## Deployment

### Netlify

1. Connect GitHub repository
2. Set build command: `npm run build`
3. Set publish directory: `build`
4. Add environment variables in dashboard:
   - `REACT_APP_BACKEND_URL`
   - `REACT_APP_LIVEKIT_URL`
   - `REACT_APP_LIVEKIT_API_KEY`
   - `REACT_APP_LIVEKIT_API_SECRET`
   - `REACT_APP_BEYOND_PRESENCE_KEY`
5. Deploy

### Vercel

1. Connect GitHub repository
2. Framework preset: Create React App
3. Add environment variables in dashboard
4. Deploy

### Environment Variables

Make sure to set all required environment variables in your deployment platform's dashboard. These are prefixed with `REACT_APP_` for Create React App.

## Development

### Adding New Features

1. **Create component** in `src/components/`
2. **Add types** in `src/types/index.ts`
3. **Update hooks** if needed in `src/hooks/`
4. **Integrate** into `CallInterface.tsx` or `App.tsx`

### Code Style

- Use TypeScript for all new files
- Follow React functional component patterns
- Use hooks for state management
- Use TailwindCSS for styling
- Follow existing naming conventions

## Troubleshooting

### Connection Issues

**Connection fails:**
- Check LiveKit URL and credentials in `.env.local`
- Verify backend API is running and accessible
- Check browser console for WebSocket errors
- Verify CORS settings on backend

**No audio:**
- Check microphone permissions in browser
- Verify microphone is not muted in system settings
- Check browser console for audio track errors
- Try different browser (Chrome recommended)

### Avatar Issues

**Avatar not loading:**
- Verify Beyond Presence API key is set
- Check backend logs for avatar session errors
- Verify avatar participant joins room (check LiveKit dashboard)
- Check browser console for track subscription errors

**Video not displaying:**
- Check that video track is subscribed
- Verify video element is attached to DOM
- Check browser console for video playback errors
- Try refreshing the page

### Tool Calls Not Showing

**Tool calls not appearing:**
- Check WebSocket connection is active
- Verify data channel events are being received
- Check browser console for parsing errors
- Verify backend is sending tool call events

### Performance Issues

**Slow rendering:**
- Check for unnecessary re-renders
- Use React.memo for expensive components
- Optimize transcript rendering (virtual scrolling if needed)
- Check network tab for slow API calls

## Known Limitations

1. **Mobile Support**: Basic responsive design, may need optimization for mobile devices
2. **Error Recovery**: Limited error recovery mechanisms. Users may need to refresh on connection failures
3. **Browser Compatibility**: Best experience in Chrome/Edge. Safari may have audio limitations
4. **Avatar**: Requires Beyond Presence API key and active avatar session

## License

MIT
