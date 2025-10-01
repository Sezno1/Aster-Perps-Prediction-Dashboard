"""
Simple test dashboard to verify basic functionality
"""

from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO
import sys
import os
import threading
import time

sys.path.append('.')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'
socketio = SocketIO(app, cors_allowed_origins="*")

# Simple HTML template
SIMPLE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple ASTER Dashboard Test</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body { font-family: Arial; background: #1a1a1a; color: white; padding: 20px; }
        .card { background: #333; padding: 15px; margin: 10px 0; border-radius: 8px; }
        .loading { color: #ffa500; }
        .loaded { color: #00ff00; }
        .error { color: #ff4444; }
    </style>
</head>
<body>
    <h1>🚀 ASTER Dashboard Test</h1>
    
    <div class="card">
        <h3>Connection Status</h3>
        <div id="status" class="loading">Connecting...</div>
    </div>
    
    <div class="card">
        <h3>Live Price Data</h3>
        <div id="price" class="loading">Loading price...</div>
        <div id="timestamp" class="loading">Loading timestamp...</div>
    </div>
    
    <div class="card">
        <h3>🪐 Live Planetary Positions</h3>
        <div id="planetary" class="loading">Loading planetary data...</div>
    </div>
    
    <script>
        const socket = io();
        
        socket.on('connect', () => {
            console.log('✅ WebSocket Connected');
            document.getElementById('status').textContent = '✅ Connected';
            document.getElementById('status').className = 'loaded';
        });
        
        socket.on('disconnect', () => {
            console.log('❌ WebSocket Disconnected');
            document.getElementById('status').textContent = '❌ Disconnected';
            document.getElementById('status').className = 'error';
        });
        
        socket.on('update', (data) => {
            console.log('📡 Data received:', Object.keys(data));
            
            // Update price
            if (data.current_price) {
                document.getElementById('price').textContent = `$${data.current_price.toFixed(6)}`;
                document.getElementById('price').className = 'loaded';
            }
            
            // Update timestamp
            document.getElementById('timestamp').textContent = new Date().toLocaleString();
            document.getElementById('timestamp').className = 'loaded';
            
            // Update planetary data
            if (data.astrological_analysis && data.astrological_analysis.available) {
                const astro = data.astrological_analysis;
                let planetaryText = '';
                
                if (astro.comprehensive_planetary_data && astro.comprehensive_planetary_data.planets) {
                    const planets = astro.comprehensive_planetary_data.planets;
                    planetaryText = Object.keys(planets).map(name => {
                        const planet = planets[name];
                        return `${name}: ${planet.exact_position || 'Loading...'}`;
                    }).join('<br>');
                } else {
                    planetaryText = 'Planetary data structure missing';
                }
                
                document.getElementById('planetary').innerHTML = planetaryText;
                document.getElementById('planetary').className = 'loaded';
            } else {
                document.getElementById('planetary').textContent = 'Astrological data not available';
                document.getElementById('planetary').className = 'error';
            }
        });
        
        // Also try to load initial data via API
        fetch('/api/simple-data')
            .then(r => r.json())
            .then(data => {
                console.log('📊 API data loaded:', Object.keys(data));
                // Trigger the same update logic
                socket.emit('update', data);  // Fake a socket update
            })
            .catch(err => {
                console.error('❌ API load failed:', err);
                document.getElementById('status').textContent = '❌ API Failed';
                document.getElementById('status').className = 'error';
            });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(SIMPLE_TEMPLATE)

@app.route('/api/simple-data')
def get_simple_data():
    """Simple API endpoint with just basic data"""
    try:
        # Import astrological system
        from tentacles.astrological.master_astro_engine import master_astro
        
        # Get basic planetary data
        astro_data = master_astro.get_comprehensive_analysis()
        
        return jsonify({
            'current_price': 0.004567,  # Mock price for now
            'timestamp': time.time(),
            'astrological_analysis': {
                'available': True,
                'comprehensive_planetary_data': {
                    'planets': astro_data.get('planetary_positions', {})
                }
            }
        })
    except Exception as e:
        print(f"Error in simple API: {e}")
        return jsonify({
            'current_price': 0.004567,
            'timestamp': time.time(),
            'astrological_analysis': {
                'available': False,
                'error': str(e)
            }
        })

def simple_background_updates():
    """Simple background thread"""
    print("🔄 Simple background thread started")
    while True:
        time.sleep(5)  # Every 5 seconds
        try:
            data = get_simple_data().get_json()
            socketio.emit('update', data, namespace='/')
            print(f"📡 Simple update sent: ${data['current_price']}")
        except Exception as e:
            print(f"❌ Simple update error: {e}")

if __name__ == '__main__':
    # Start background thread
    update_thread = threading.Thread(target=simple_background_updates, daemon=True)
    update_thread.start()
    
    print("🚀 Starting simple test dashboard on http://localhost:5003")
    socketio.run(app, host='0.0.0.0', port=5003, debug=False, allow_unsafe_werkzeug=True)