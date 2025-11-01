import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit import api
from dotenv import load_dotenv
import uvicorn

# ==========================================================
# Load environment variables
# ==========================================================
load_dotenv()

LIVEKIT_URL = os.getenv("VITE_LIVEKIT_URL", "wss://frontdeskai-fwmdtckr.livekit.cloud")
LIVEKIT_API_KEY = os.getenv("VITE_LIVEKIT_API_KEY", "APIQagyHvniYKoP")
LIVEKIT_API_SECRET = os.getenv("VITE_LIVEKIT_API_SECRET", "enMoVgKxqAdaH9tJN1WveGeSfslsfRgEEluSe7bEuDeS")
ROOM_NAME = "support-room"

# ==========================================================
# FastAPI setup
# ==========================================================
app = FastAPI(title="LiveKit Token Generator")

# Allow local + cloud frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://frontdeskai-fwmdtckr.livekit.cloud",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# Token Generator
# ==========================================================
async def generate_token(identity: str):
    """
    Generate a signed JWT token that allows joining a LiveKit room.
    """
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        raise HTTPException(status_code=500, detail="Missing LiveKit credentials in environment")

    try:
        # Create the access token
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.identity = identity

        # Grant permissions (use VideoGrant, NOT VideoGrants)
        grant = api.VideoGrant(
            room_join=True,
            room=ROOM_NAME,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
        )

        token.add_grant(grant)
        jwt_token = token.to_jwt()

        return jwt_token

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating token: {e}")

# ==========================================================
# API Endpoint
# ==========================================================
@app.get("/get_livekit_token")
async def get_livekit_token(identity: str = Query(...)):
    """
    Frontend calls this endpoint to get a LiveKit access token.
    Example: http://127.0.0.1:8000/get_livekit_token?identity=supervisor
    """
    try:
        jwt_token = await generate_token(identity)
        print(f"[✅ LIVEKIT] Token generated successfully for '{identity}'")
        return {
            "token": jwt_token,
            "livekit_url": LIVEKIT_URL,
            "room": ROOM_NAME,
        }
    except Exception as e:
        print(f"[❌ ERROR] Token generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Token generation failed: {e}")

# ==========================================================
# Root Endpoint
# ==========================================================
@app.get("/")
async def root():
    return {"status": "ok", "message": "LiveKit backend is running."}

# ==========================================================
# Local Run
# ==========================================================
if __name__ == "__main__":
    print("🚀 LiveKit backend running at http://127.0.0.1:8000 ...")
    uvicorn.run("livekit:app", host="127.0.0.1", port=8000, reload=True)
