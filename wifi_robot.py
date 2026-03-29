import RPi.GPIO as GPIO
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import time
import threading

# Motor pins
IN1, IN2, IN3, IN4 = 23, 24, 25, 8

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup([IN1, IN2, IN3, IN4], GPIO.OUT)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Robot state
robot_state = {
    'moving': False,
    'direction': 'stopped'
}

# Movement control lock
movement_lock = threading.Lock()

def forward():
    """Move robot forward"""
    with movement_lock:
        GPIO.output([IN1, IN3], 1)
        GPIO.output([IN2, IN4], 0)
        robot_state['moving'] = True
        robot_state['direction'] = 'forward'

def reverse():
    """Move robot backward"""
    with movement_lock:
        GPIO.output([IN1, IN3], 0)
        GPIO.output([IN2, IN4], 1)
        robot_state['moving'] = True
        robot_state['direction'] = 'reverse'

def left():
    """Turn robot left"""
    with movement_lock:
        GPIO.output(IN1, 0)
        GPIO.output(IN2, 1)
        GPIO.output(IN3, 1)
        GPIO.output(IN4, 0)
        robot_state['moving'] = True
        robot_state['direction'] = 'left'

def right():
    """Turn robot right"""
    with movement_lock:
        GPIO.output(IN1, 1)
        GPIO.output(IN2, 0)
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 1)
        robot_state['moving'] = True
        robot_state['direction'] = 'right'

def stop():
    """Stop robot"""
    with movement_lock:
        GPIO.output([IN1, IN2, IN3, IN4], 0)
        robot_state['moving'] = False
        robot_state['direction'] = 'stopped'

@app.route('/')
def index():
    """Serve the main control page"""
    return render_template('index.html')

@app.route('/control', methods=['POST'])
def control():
    """Handle movement control commands"""
    try:
        data = request.get_json()
        command = data.get('command', '').lower()
        
        if command == 'forward':
            forward()
            return jsonify({'status': 'success', 'message': 'Moving forward'})
        elif command == 'reverse':
            reverse()
            return jsonify({'status': 'success', 'message': 'Moving backward'})
        elif command == 'left':
            left()
            return jsonify({'status': 'success', 'message': 'Turning left'})
        elif command == 'right':
            right()
            return jsonify({'status': 'success', 'message': 'Turning right'})
        elif command == 'stop':
            stop()
            return jsonify({'status': 'success', 'message': 'Stopped'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid command'}), 400
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Get current robot status"""
    return jsonify(robot_state)

def cleanup():
    """Cleanup GPIO on exit"""
    stop()
    GPIO.cleanup()

if __name__ == '__main__':
    try:
        print("Starting WiFi Robot Controller...")
        print("Access the controller at: http://<your-pi-ip>:5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        cleanup()
