from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
from datetime import datetime
import time

# CONFIG
ROOMS = ['Room_39', 'Room_38', 'Room_37']
SERVER_PORT = 5000
SHUTDOWN_THRESHOLD = 5

class Dashboard:
    def __init__(self):
        self.rooms = {
            room: {
                'occupancy': 0,
                'motion': False,
                'devices': {'lights': False, 'fan': False, 'ac': False},
                'empty_start': 0,
                'energy': 0
            }
            for room in ROOMS
        }
        self.events = []
        self.total_saved = 0
    
    def update_room(self, room_id, occupancy, motion):
        if room_id not in self.rooms:
            return
        
        room = self.rooms[room_id]
        current_time = time.time()
        
        if motion and occupancy > 0:
            room['occupancy'] = occupancy
            room['motion'] = True
            room['empty_start'] = 0
            
            for device in room['devices']:
                if not room['devices'][device]:
                    room['devices'][device] = True
                    self.add_event(f"✅ {room_id}: {occupancy} people - 💡ON 🌀ON ❄️ON")
            
            room['energy'] += 2.5
        else:
            room['motion'] = False
            room['occupancy'] = occupancy
            
            if occupancy == 0:
                if room['empty_start'] == 0:
                    room['empty_start'] = current_time
                    self.add_event(f"⏰ {room_id}: Empty - Shutdown in {SHUTDOWN_THRESHOLD}s")
                
                elapsed = current_time - room['empty_start']
                if elapsed >= SHUTDOWN_THRESHOLD:
                    for device in room['devices']:
                        room['devices'][device] = False
                    
                    self.total_saved += room['energy']
                    self.add_event(f"🔴 {room_id}: OFF - Saved {self.total_saved:.2f} kWh")
                    room['energy'] = 0
    
    def add_event(self, message):
        event = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': message
        }
        self.events.insert(0, event)
        if len(self.events) > 25:
            self.events.pop()
    
    def get_data(self):
        rooms_occupied = sum(1 for r in self.rooms.values() if r['occupancy'] > 0)
        devices_on = sum(sum(1 for d in r['devices'].values() if d) for r in self.rooms.values())
        total_power = 2.47 + (devices_on * 0.8)
        
        return {
            'rooms': self.rooms,
            'summary': {
                'total_power': round(total_power, 2),
                'rooms_occupied': rooms_occupied,
                'devices_on': devices_on,
                'energy_saved': round(self.total_saved, 2)
            },
            'events': self.events,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }

dashboard = Dashboard()
app = Flask(__name__)
CORS(app)

@app.route('/api/data')
def get_data():
    return jsonify(dashboard.get_data())

@app.route('/api/update/<room_id>', methods=['POST'])
def update_room(room_id):
    data = request.json
    dashboard.update_room(room_id, data.get('occupancy', 0), data.get('motion', False))
    return jsonify({'status': 'updated'})

@app.route('/')
def index():
    html = '''<!DOCTYPE html>
<html>
<head>
    <title>🏫 Smart Energy Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            background: linear-gradient(135deg, #0a0e14 0%, #0f1419 100%); 
            color: #fff; 
            font-family: 'Segoe UI', Arial; 
            padding: 20px; 
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header { 
            text-align: center; 
            margin-bottom: 30px; 
            padding: 20px; 
            border: 3px solid #0096DC; 
            border-radius: 12px;
            background: rgba(0, 150, 220, 0.1);
        }
        h1 { font-size: 2.5em; color: #00D4FF; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric { background: #1a1f2e; border: 2px solid #0096DC; padding: 20px; border-radius: 12px; text-align: center; }
        .metric-value { font-size: 2.5em; color: #00D4FF; margin: 10px 0; font-weight: 700; }
        .metric-label { color: #a0aec0; font-size: 0.9em; }
        .rooms { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .room { background: #1a1f2e; border: 2px solid #0096DC; padding: 20px; border-radius: 12px; }
        .room.occupied { border-color: #10B981; box-shadow: 0 0 20px rgba(16,185,129,0.4); }
        .room-name { font-size: 1.3em; color: #00D4FF; margin-bottom: 10px; font-weight: 700; }
        .occupancy { font-size: 2em; color: #00D4FF; margin: 15px 0; }
        .devices { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 15px; }
        .device { background: rgba(0,150,220,0.1); border: 1px solid rgba(0,150,220,0.2); padding: 12px; border-radius: 8px; text-align: center; }
        .device.on { background: rgba(16,185,129,0.2); border-color: #10B981; box-shadow: 0 0 15px rgba(16,185,129,0.3); animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
        .device-icon { font-size: 2em; margin-bottom: 5px; }
        .device-name { font-size: 0.8em; color: #a0aec0; }
        .device-status { font-size: 0.9em; margin-top: 5px; font-weight: 600; }
        .device.on .device-status { color: #10B981; }
        .device.off .device-status { color: #EF4444; }
        .events { background: #1a1f2e; border: 2px solid #0096DC; border-radius: 12px; padding: 20px; }
        .events h2 { color: #00D4FF; margin-bottom: 15px; }
        .event-log { max-height: 300px; overflow-y: auto; background: rgba(0,0,0,0.3); border-radius: 8px; padding: 15px; }
        .event { padding: 10px; margin-bottom: 8px; background: rgba(0,150,220,0.1); border-left: 3px solid #0096DC; border-radius: 4px; display: flex; gap: 10px; }
        .event-time { color: #a0aec0; min-width: 70px; font-weight: 600; }
        .event-msg { color: #00D4FF; flex: 1; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏫 AI Smart Energy Management System</h1>
            <p style="color: #a0aec0; margin-top: 10px;">Real-time Classroom Monitoring</p>
        </header>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">⚡ Power</div>
                <div class="metric-value" id="power">0.0</div>
                <div class="metric-label">kW</div>
            </div>
            <div class="metric">
                <div class="metric-label">🏫 Occupied</div>
                <div class="metric-value" id="occupied">0</div>
                <div class="metric-label">rooms</div>
            </div>
            <div class="metric">
                <div class="metric-label">🔌 Active</div>
                <div class="metric-value" id="devices">0</div>
                <div class="metric-label">devices</div>
            </div>
            <div class="metric">
                <div class="metric-label">💰 Saved</div>
                <div class="metric-value" id="saved">0</div>
                <div class="metric-label">kWh</div>
            </div>
        </div>
        
        <div class="rooms" id="rooms"></div>
        
        <div class="events">
            <h2>📋 Live Events</h2>
            <div class="event-log" id="eventLog"></div>
        </div>
    </div>
    
    <script>
        async function update() {
            try {
                const res = await fetch('/api/data');
                const data = await res.json();
                
                document.getElementById('power').textContent = data.summary.total_power.toFixed(2);
                document.getElementById('occupied').textContent = data.summary.rooms_occupied;
                document.getElementById('devices').textContent = data.summary.devices_on;
                document.getElementById('saved').textContent = data.summary.energy_saved.toFixed(2);
                
                const roomsDiv = document.getElementById('rooms');
                roomsDiv.innerHTML = '';
                
                for (const [roomId, room] of Object.entries(data.rooms)) {
                    const isOccupied = room.occupancy > 0;
                    const div = document.createElement('div');
                    div.className = 'room' + (isOccupied ? ' occupied' : '');
                    
                    const devicesHtml = [
                        {name: 'Lights', icon: '💡', key: 'lights'},
                        {name: 'Fan', icon: '🌀', key: 'fan'},
                        {name: 'AC', icon: '❄️', key: 'ac'}
                    ].map(d => `
                        <div class="device ${room.devices[d.key] ? 'on' : 'off'}">
                            <div class="device-icon">${d.icon}</div>
                            <div class="device-name">${d.name}</div>
                            <div class="device-status">${room.devices[d.key] ? '✓ ON' : '✗ OFF'}</div>
                        </div>
                    `).join('');
                    
                    div.innerHTML = `
                        <div class="room-name">${roomId}</div>
                        <div class="occupancy">${room.occupancy}</div>
                        <div class="devices">${devicesHtml}</div>
                    `;
                    roomsDiv.appendChild(div);
                }
                
                const eventLog = document.getElementById('eventLog');
                eventLog.innerHTML = data.events.map(e => 
                    `<div class="event"><span class="event-time">${e.timestamp}</span><span class="event-msg">${e.message}</span></div>`
                ).join('');
            } catch (e) {
                console.error(e);
            }
        }
        
        update();
        setInterval(update, 1000);
    </script>
</body>
</html>'''
    return render_template_string(html)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏫 DASHBOARD SERVER STARTED")
    print("="*60)
    print(f"\n✅ Open Browser: http://localhost:{SERVER_PORT}")
    print("✅ Press Ctrl+C to stop\n")
    print("="*60 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=SERVER_PORT)