"""
Debug dashboard to see exactly what's happening
"""

from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO
import sys
import os
import threading
import time
import json

sys.path.append('.')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'
socketio = SocketIO(app, cors_allowed_origins="*")

# Debug HTML template
DEBUG_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🔍 Debug Dashboard</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body { font-family: Arial; background: #1a1a1a; color: white; padding: 20px; }
        .section { background: #333; padding: 15px; margin: 10px 0; border-radius: 8px; }
        .success { color: #00ff00; }
        .error { color: #ff4444; }
        .info { color: #ffa500; }
        .small { font-size: 12px; opacity: 0.7; }
        #log { height: 300px; overflow-y: scroll; background: #222; padding: 10px; }
    </style>
</head>
<body>
    <h1>🔍 Dashboard Debug Mode</h1>
    
    <div class="section">
        <h3>🔗 Connection Status</h3>
        <div id="connectionStatus">Initializing...</div>
    </div>
    
    <div class="section">
        <h3>📊 Data Status</h3>
        <div id="dataStatus">No data yet...</div>
        <div id="dataFields" class="small"></div>
    </div>
    
    <div class="section">
        <h3>🪐 Astrological Status</h3>
        <div id="astroStatus">No astro data yet...</div>
        <div id="astroDetails" class="small"></div>
    </div>
    
    <div class="section">
        <h3>📝 Debug Log</h3>
        <div id="log"></div>
        <button onclick="clearLog()">Clear Log</button>
    </div>
    
    <script>
        let logCount = 0;
        
        function log(message, type = 'info') {
            logCount++;
            const timestamp = new Date().toLocaleTimeString();
            const logDiv = document.getElementById('log');
            const color = type === 'success' ? '#00ff00' : type === 'error' ? '#ff4444' : '#ffa500';
            logDiv.innerHTML += `<div style="color: ${color}">[${timestamp}] ${message}</div>`;
            logDiv.scrollTop = logDiv.scrollHeight;
            console.log(`[${timestamp}] ${message}`);
        }
        
        function clearLog() {
            document.getElementById('log').innerHTML = '';
            logCount = 0;
        }
        
        // Test basic functionality
        log("🚀 Debug dashboard starting...", "info");
        
        // Test WebSocket
        const socket = io();
        
        socket.on('connect', () => {
            log("✅ WebSocket connected!", "success");
            document.getElementById('connectionStatus').innerHTML = '<span class="success">✅ Connected</span>';
        });
        
        socket.on('disconnect', () => {
            log("❌ WebSocket disconnected!", "error");
            document.getElementById('connectionStatus').innerHTML = '<span class="error">❌ Disconnected</span>';
        });
        
        socket.on('update', (data) => {
            log(`📡 WebSocket data received: ${Object.keys(data).length} keys`, "success");
            
            // Update data status
            document.getElementById('dataStatus').innerHTML = `<span class="success">✅ Data received (${Object.keys(data).length} fields)</span>`;
            document.getElementById('dataFields').innerHTML = Object.keys(data).slice(0, 10).join(', ') + (Object.keys(data).length > 10 ? '...' : '');
            
            // Check astrological data
            if (data.astrological_analysis) {
                const astro = data.astrological_analysis;
                if (astro.available) {
                    const planets = astro.comprehensive_planetary_data?.planets || {};
                    log(`🪐 Astrological data: ${Object.keys(planets).length} planets`, "success");
                    document.getElementById('astroStatus').innerHTML = `<span class="success">✅ ${Object.keys(planets).length} planets loaded</span>`;
                    document.getElementById('astroDetails').innerHTML = Object.keys(planets).join(', ');
                } else {
                    log(`❌ Astrological data not available: ${astro.error || 'Unknown error'}`, "error");
                    document.getElementById('astroStatus').innerHTML = `<span class="error">❌ Error: ${astro.error || 'Unknown'}</span>`;
                }
            } else {
                log("❌ No astrological_analysis field in data", "error");
                document.getElementById('astroStatus').innerHTML = '<span class="error">❌ No astro field</span>';
            }
        });
        
        // Test API
        log("📊 Testing API endpoint...", "info");
        fetch('/api/debug-data')
            .then(r => {
                log(`📊 API response status: ${r.status}`, r.status === 200 ? "success" : "error");
                return r.json();
            })
            .then(data => {
                log(`📊 API data loaded: ${Object.keys(data).length} fields`, "success");
                
                // Simulate socket update for testing
                const fakeEvent = { target: { emit: () => {} } };
                socket.emit('update', data);
            })
            .catch(err => {
                log(`❌ API error: ${err.message}`, "error");
                document.getElementById('dataStatus').innerHTML = `<span class="error">❌ API Error: ${err.message}</span>`;
            });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(DEBUG_TEMPLATE)

@app.route('/api/debug-data')
def get_debug_data():
    """Debug API endpoint"""
    try:
        # Import the actual scanner data function
        from core.app import get_scanner_data
        
        with app.app_context():
            data = get_scanner_data()
            return jsonify(data) if data else jsonify({"error": "No data from get_scanner_data"})
            
    except Exception as e:
        return jsonify({"error": str(e)})

def debug_background_updates():
    """Simple background thread for debugging"""
    count = 0
    while True:
        time.sleep(15)  # Every 15 seconds
        count += 1
        try:
            with app.app_context():
                print(f"🔄 Debug update #{count}")
                data = get_debug_data().get_json()
                socketio.emit('update', data, namespace='/')
                print(f"📡 Debug update #{count} sent")
        except Exception as e:
            print(f"❌ Debug update error: {e}")

if __name__ == '__main__':
    # Start background thread
    update_thread = threading.Thread(target=debug_background_updates, daemon=True)
    update_thread.start()
    
    print("🔍 Starting debug dashboard on http://localhost:5004")
    socketio.run(app, host='0.0.0.0', port=5004, debug=False, allow_unsafe_werkzeug=True)