# backend/app.py
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import time
from typing import Optional
import os
import json
import jwt
import datetime
import requests

app = FastAPI(title="Frontdesk HITL Demo (Persistent)")

# ---------------- CORS SETUP ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DATA PERSISTENCE ----------------
DATA_FILE = "data.json"


def load_data():
    """Load data from JSON file (persistent storage)."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"help_requests": [], "knowledge_base": {}}
    return {"help_requests": [], "knowledge_base": {}}


def save_data():
    """Save help_requests and knowledge_base to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(
            {"help_requests": help_requests, "knowledge_base": knowledge_base}, f, indent=4
        )


data = load_data()
help_requests = data["help_requests"]
knowledge_base = data["knowledge_base"]

# ---------------- SUPERVISOR AUTH ----------------
SUPERVISOR_PASSWORD = os.getenv("SUPERVISOR_PASSWORD", "Abhijeet")
TOKENS = {}
TOKEN_TTL_SECONDS = 60 * 60  # 1 hour
_next_req_id = len(help_requests) + 1


def generate_token():
    tok = str(uuid.uuid4())
    TOKENS[tok] = time.time() + TOKEN_TTL_SECONDS
    return tok


def validate_token(token: Optional[str]) -> bool:
    if not token:
        return False
    expiry = TOKENS.get(token)
    if not expiry:
        return False
    if time.time() > expiry:
        TOKENS.pop(token, None)
        return False
    return True


# ---------------- ROUTES ----------------
@app.post("/login")
async def login(payload: dict):
    password = payload.get("password")
    if not password:
        raise HTTPException(status_code=400, detail="password required")
    if password != SUPERVISOR_PASSWORD:
        raise HTTPException(status_code=401, detail="invalid password")

    token = generate_token()
    return {"token": token, "expires_in": TOKEN_TTL_SECONDS}


@app.post("/logout")
async def logout(x_supervisor_token: Optional[str] = Header(None)):
    if x_supervisor_token:
        TOKENS.pop(x_supervisor_token, None)
    return {"message": "logged out"}


@app.get("/")
def root():
    return {"message": "Frontdesk AI backend is running!"}


@app.post("/ask")
def ask_question(question: str, caller_id: Optional[str] = "anonymous"):
    global _next_req_id
    q = question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="question required")

    known = knowledge_base.get(q.lower())
    if known:
        print(f"[AI] Known answer. Replying to caller {caller_id}: {known}")
        return {"answer": known, "known": True}

    req = {
        "id": _next_req_id,
        "caller_id": caller_id,
        "question": q,
        "status": "pending",
        "answer": None,
        "created_at": time.time(),
    }
    _next_req_id += 1
    help_requests.append(req)
    save_data()

    print(f"[SUPERVISOR ALERT] Need help answering: '{q}' (req_id={req['id']})")
    return {"reply": "Let me check with my supervisor and get back to you.", "known": False}


@app.get("/requests")
def view_requests(x_supervisor_token: Optional[str] = Header(None)):
    if not validate_token(x_supervisor_token):
        raise HTTPException(status_code=401, detail="invalid or missing supervisor token")

    out = sorted(help_requests, key=lambda r: r["created_at"], reverse=True)
    return {"pending_requests": out}


@app.post("/respond")
def supervisor_response(question: str, answer: str, x_supervisor_token: Optional[str] = Header(None)):
    if not validate_token(x_supervisor_token):
        raise HTTPException(status_code=401, detail="invalid or missing supervisor token")

    for req in help_requests:
        if req["question"] == question and req["status"] == "pending":
            req["status"] = "resolved"
            req["answer"] = answer
            req["resolved_at"] = time.time()
            knowledge_base[req["question"].lower()] = answer
            save_data()

            print(f"[SUPERVISOR] Resolved: {req['id']} — {answer}")
            return {"message": "Resolved and saved to knowledge base."}

    return JSONResponse(status_code=404, content={"error": "No pending request found"})


# ---------------- USER AUTH ----------------
USER_SESSIONS = {}


@app.post("/user_login")
async def user_login(payload: dict):
    name = payload.get("name") or payload.get("email")
    if not name:
        raise HTTPException(status_code=400, detail="name or email required")

    user_id = str(uuid.uuid4())
    USER_SESSIONS[user_id] = name
    return {"user_id": user_id, "name": name}


@app.post("/user_ask")
async def user_ask(payload: dict):
    global _next_req_id

    user_id = payload.get("user_id")
    question = payload.get("question", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="question required")

    known = knowledge_base.get(question.lower())
    if known:
        print(f"[AI -> {USER_SESSIONS.get(user_id, 'guest')}] Known answer: {known}")
        return {"answer": known, "known": True}

    req = {
        "id": _next_req_id,
        "caller_id": user_id or "guest",
        "question": question,
        "status": "pending",
        "answer": None,
        "created_at": time.time(),
    }
    _next_req_id += 1
    help_requests.append(req)
    save_data()

    print(f"[SUPERVISOR ALERT] New question from user {USER_SESSIONS.get(user_id, 'guest')}: {question}")
    return {"message": "Forwarding to human supervisor...", "known": False}


# ---------------- LIVEKIT TOKEN ENDPOINT ----------------
LIVEKIT_URL = "wss://frontdeskai-fwmdtckr.livekit.cloud"
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "APIQagyHvniYKoP")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "enMoVgKxqAdaH9tJN1WveGeSfslsfRgEEluSe7bEuDeS")


@app.get("/get_livekit_token")
async def get_livekit_token(identity: str = Query(...)):
    """
    Generate a LiveKit token that allows frontend to join a room securely.
    """
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        exp = now + datetime.timedelta(hours=1)

        payload = {
            "iss": LIVEKIT_API_KEY,
            "sub": identity,
            "exp": exp,
            "video": {
                "room": "*",
                "room_join": True,
                "can_publish": True,
                "can_subscribe": True,
            },
        }

        token = jwt.encode(payload, LIVEKIT_API_SECRET, algorithm="HS256")
        print(f"[TOKEN] Issued LiveKit token for {identity}")
        return {"token": token, "url": LIVEKIT_URL}

    except Exception as e:
        print(f"[ERROR] LiveKit token generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
