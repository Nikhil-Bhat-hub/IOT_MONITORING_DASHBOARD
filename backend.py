from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import get_connection, init_db
from pydantic import BaseModel
import uuid

app = FastAPI()
init_db()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- LOGIN ----------------
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login/")
def login(data: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (data.username, data.password)
    )
    user = cursor.fetchone()

    if user:
        session_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO active_sessions (session_id, username) VALUES (%s, %s)",
            (session_id, data.username)
        )
        conn.commit()
        conn.close()
        return {"success": True, "session_id": session_id}

    conn.close()
    return {"success": False}

# ---------------- ACTIVE USERS ----------------
@app.get("/active_users/")
def active_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM active_sessions")
    count = cursor.fetchone()[0]

    conn.close()
    return {"active_users": count}

# ---------------- UPDATE DEVICE ----------------
@app.post("/update_device/")
def update_device(device_id: str,
                  latitude: float,
                  longitude: float,
                  signal: int,
                  data_usage: float,
                  active_duration: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO devices (device_id, latitude, longitude, status,
                         signal, data_usage, active_duration)
    VALUES (%s, %s, %s, 'Online', %s, %s, %s)
    ON CONFLICT (device_id)
    DO UPDATE SET
        latitude=EXCLUDED.latitude,
        longitude=EXCLUDED.longitude,
        status='Online',
        signal=EXCLUDED.signal,
        data_usage=EXCLUDED.data_usage,
        active_duration=EXCLUDED.active_duration,
        last_seen=CURRENT_TIMESTAMP;
    """, (device_id, latitude, longitude,
          signal, data_usage, active_duration))

    cursor.execute("""
    INSERT INTO device_logs (device_id, signal, data_usage)
    VALUES (%s, %s, %s);
    """, (device_id, signal, data_usage))

    conn.commit()
    conn.close()

    return {"message": "Device updated"}

# ---------------- GET DEVICES ----------------
@app.get("/get_devices/")
def get_devices():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE devices
    SET status='Offline'
    WHERE last_seen < NOW() - INTERVAL '15 seconds';
    """)

    cursor.execute("SELECT * FROM devices;")
    rows = cursor.fetchall()

    conn.commit()
    conn.close()

    columns = [
        "device_id", "latitude", "longitude",
        "status", "signal", "data_usage",
        "active_duration", "last_seen"
    ]

    return [dict(zip(columns, row)) for row in rows]

# ---------------- ANALYTICS ----------------
@app.get("/analytics/")
def analytics():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM devices")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM devices WHERE status='Online'")
    online = cursor.fetchone()[0]

    offline = total - online

    cursor.execute("SELECT AVG(signal) FROM devices")
    avg_signal = cursor.fetchone()[0] or 0

    conn.close()

    return {
        "total_devices": total,
        "online_devices": online,
        "offline_devices": offline,
        "average_signal_strength": round(avg_signal, 2)
    }

# ---------------- HISTORY ----------------
@app.get("/history/{device_id}")
def history(device_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT signal, data_usage, timestamp
    FROM device_logs
    WHERE device_id=%s
    ORDER BY timestamp ASC
    LIMIT 50;
    """, (device_id,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {"signal": r[0], "data_usage": r[1], "timestamp": r[2]}
        for r in rows
    ]
@app.post("/create_user/")
def create_user(username: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (username, password)
    )

    conn.commit()
    conn.close()

    return {"message": "User created successfully"}

