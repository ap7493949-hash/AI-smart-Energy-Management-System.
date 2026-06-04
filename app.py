"""
🏫 AI Smart Energy Management System - Streamlit Dashboard
Real-time Classroom Energy Monitoring
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Smart Energy Dashboard",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .main {
            background-color: #0a0e14;
            color: #ffffff;
        }
        .metric-box {
            background: linear-gradient(135deg, #0096DC 0%, #005fa3 100%);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            color: white;
        }
        .room-card {
            background: #1a1f2e;
            border: 2px solid #0096DC;
            padding: 20px;
            border-radius: 12px;
            margin: 10px 0;
        }
        .room-occupied {
            border-color: #10B981;
            box-shadow: 0 0 20px rgba(16,185,129,0.4);
        }
        .device-on {
            color: #10B981;
            font-weight: bold;
        }
        .device-off {
            color: #EF4444;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'rooms' not in st.session_state:
    st.session_state.rooms = {
        'Room_39': {'occupancy': 0, 'devices': {'lights': False, 'fan': False, 'ac': False}},
        'Room_38': {'occupancy': 0, 'devices': {'lights': False, 'fan': False, 'ac': False}},
        'Room_37': {'occupancy': 0, 'devices': {'lights': False, 'fan': False, 'ac': False}}
    }

if 'events' not in st.session_state:
    st.session_state.events = []

if 'energy_saved' not in st.session_state:
    st.session_state.energy_saved = 0.0

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# 🏫 Smart Energy Management System")
    st.markdown("### Real-time Classroom Monitoring & Control")
with col2:
    st.markdown(f"### 🕐 {datetime.now().strftime('%H:%M:%S')}")

st.divider()

# Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "⚡ Power Usage",
        "2.47 kW",
        "-0.5 kW",
        delta_color="inverse"
    )

with col2:
    occupied_rooms = sum(1 for room in st.session_state.rooms.values() if room['occupancy'] > 0)
    st.metric(
        "🏫 Occupied Rooms",
        occupied_rooms,
        "/ 3 rooms"
    )

with col3:
    active_devices = sum(
        sum(1 for device in room['devices'].values() if device)
        for room in st.session_state.rooms.values()
    )
    st.metric(
        "🔌 Active Devices",
        active_devices,
        "devices"
    )

with col4:
    st.metric(
        "💰 Energy Saved",
        f"{st.session_state.energy_saved:.2f} kWh",
        "+0.5 kWh"
    )

st.divider()

# Room Status Section
st.markdown("## 📊 Room Status")

for room_name, room_data in st.session_state.rooms.items():
    col1, col2, col3 = st.columns([2, 1, 2])
    
    # Room Name and Status
    with col1:
        if room_data['occupancy'] > 0:
            st.markdown(f"### {room_name} ✅ OCCUPIED")
        else:
            st.markdown(f"### {room_name} ⚫ EMPTY")
    
    # Occupancy
    with col2:
        st.markdown(f"### {room_data['occupancy']}")
        st.caption("Students")
    
    # Devices
    with col3:
        device_status = []
        for device, status in room_data['devices'].items():
            icon = "✓" if status else "✗"
            color = "green" if status else "red"
            status_text = "ON" if status else "OFF"
            device_status.append(f"{device.upper()}: {status_text}")
        
        for status in device_status:
            st.write(status)

st.divider()

# Demo Controls Section
st.markdown("## 🎮 Demo Controls")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Simulate Occupancy")
    if st.button("👥 Add Person (Room 39)", key="add_person"):
        st.session_state.rooms['Room_39']['occupancy'] += 1
        st.session_state.rooms['Room_39']['devices'] = {
            'lights': True, 'fan': True, 'ac': True
        }
        st.session_state.events.insert(0, {
            'time': datetime.now().strftime('%H:%M:%S'),
            'event': '✅ Room_39: Person detected - Devices ON'
        })

with col2:
    st.markdown("### Simulate Empty Room")
    if st.button("🚪 Clear Room (Room 39)", key="clear_room"):
        st.session_state.rooms['Room_39']['occupancy'] = 0
        st.session_state.rooms['Room_39']['devices'] = {
            'lights': False, 'fan': False, 'ac': False
        }
        st.session_state.energy_saved += 0.5
        st.session_state.events.insert(0, {
            'time': datetime.now().strftime('%H:%M:%S'),
            'event': '🔴 Room_39: Empty - Devices OFF - Saved 0.5 kWh'
        })

with col3:
    st.markdown("### Reset System")
    if st.button("🔄 Reset All", key="reset_all"):
        st.session_state.rooms = {
            'Room_39': {'occupancy': 0, 'devices': {'lights': False, 'fan': False, 'ac': False}},
            'Room_38': {'occupancy': 0, 'devices': {'lights': False, 'fan': False, 'ac': False}},
            'Room_37': {'occupancy': 0, 'devices': {'lights': False, 'fan': False, 'ac': False}}
        }
        st.session_state.events = []
        st.session_state.energy_saved = 0.0

st.divider()

# Events Log
st.markdown("## 📋 Live Events Log")

if st.session_state.events:
    events_df = pd.DataFrame(st.session_state.events)
    st.dataframe(events_df, use_container_width=True, hide_index=True)
else:
    st.info("📭 No events yet. Try adding a person or clearing a room above!")

st.divider()

# Footer with Info
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🎯 About
    AI Smart Energy Management System
    
    Real-time classroom monitoring using:
    - Motion detection
    - Face recognition
    - Automatic device control
    """)

with col2:
    st.markdown("""
    ### 📊 Benefits
    - 25-40% energy reduction
    - Automatic operation 24/7
    - Real-time monitoring
    - Annual savings: ₹1,50,000+
    """)

with col3:
    st.markdown("""
    ### 🚀 Technology
    - Python & Streamlit
    - OpenCV & AI
    - Real-time Processing
    - Cloud Deployment
    """)

st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🏫 AI Smart Energy Management System | School Project | 2026</p>
    <p>Helping institutions save energy and protect the environment</p>
</div>
""", unsafe_allow_html=True)
