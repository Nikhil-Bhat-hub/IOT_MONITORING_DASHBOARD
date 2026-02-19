#Enterprise Real Time IoT Monitoring System

A full-stack Enterprise IoT Monitoring Dashboard built using:

- 🖥 Streamlit (Frontend Dashboard)
- ⚡ FastAPI (Backend API)
- 🗄 SQLite (Database)
- 🌍 Real-time GPS tracking
- 📊 Live analytics & historical data visualization

This system allows multiple users to log in and monitor their devices in real-time with automatic offline detection.



##Features

### 🔐 Enterprise Login System
- Secure user login
- Session tracking
- Active users counter

### 📡 Real-Time Device Monitoring
- Live GPS tracking
- Automatic device status updates
- Signal strength monitoring
- Data usage tracking

### 📉 Offline Detection
- Devices automatically marked **Offline**
- If no update received for 15 seconds

### 📊 Historical Analytics
- Signal strength trend graph
- Data usage trend graph
- Last 50 log entries per device

### 📈 KPI Dashboard
- Total Devices
- Online Devices
- Offline Devices
- Average Signal Strength
- Active Users



## 🏗 Project Architecture
iot_project/
│
├── backend.py
├── database.py
├── app.py
├── requirements.txt
└── README.md

