import RPi.GPIO as GPIO
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import time
import threading

# Motor pins
IN1, IN2, IN3, IN4 = 23, 24, 25, 8
ENA, ENB = 12, 13  # PWM pins for speed control

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup([IN1, IN2, IN3, IN4], GPIO.OUT)
GPIO.setup([ENA, ENB], GPIO.OUT)

# Initialize PWM on enable pins (1000 Hz frequency)
pwm_a = GPIO.PWM(ENA, 1000)
pwm_b = GPIO.PWM(ENB, 1000)
pwm_a.start(0)  # Start with 0% duty cycle
pwm_b.start(0)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Robot state
robot_state = {
    'moving': False,
    'direction': 'stopped',
    'speed': 0,
    'target_speed': 0
}

# Speed settings
MIN_SPEED = 30  # Minimum speed (30%)
MAX_SPEED = 100  # Maximum speed (100%)
ACCELERATION_RATE = 5  # Speed increase per 0.1 second
DECELERATION_RATE = 20  # Speed decrease rate when stopping

# Movement control lock
movement_lock = threading.Lock()
acceleration_thread = None
stop_acceleration = threading.Event()

def set_motor_speed(speed):
    """Set motor speed using PWM (0-100)"""
    speed = max(0, min(100, speed))  # Clamp between 0-100
    pwm_a.ChangeDutyCycle(speed)
    pwm_b.ChangeDutyCycle(speed)
    robot_state['speed'] = speed

def acceleration_control():
    """Gradually increase speed while button is held"""
    global stop_acceleration
    
    while not stop_acceleration.is_set():
        with movement_lock:
            current_speed = robot_state['speed']
            target_speed = robot_state['target_speed']
            
            if current_speed < target_speed:
                # Accelerate
                new_speed = min(current_speed + ACCELERATION_RATE, target_speed)
                set_motor_speed(new_speed)
            elif current_speed > target_speed:
                # Decelerate
                new_speed = max(current_speed - DECELERATION_RATE, target_speed)
                set_motor_speed(new_speed)
        
        time.sleep(0.1)  # Update every 100ms

def start_acceleration():
    """Start the acceleration thread"""
    global acceleration_thread, stop_acceleration
    
    stop_acceleration.clear()
    if acceleration_thread is None or not acceleration_thread.is_alive():
        acceleration_thread = threading.Thread(target=acceleration_control, daemon=True)
        acceleration_thread.start()

def forward():
    """Move robot forward"""
    with movement_lock:
        GPIO.output([IN1, IN3], 1)
        GPIO.output([IN2, IN4], 0)
        robot_state['moving'] = True
        robot_state['direction'] = 'forward'
        robot_state['target_speed'] = MAX_SPEED
    start_acceleration()

def reverse():
    """Move robot backward"""
    with movement_lock:
        GPIO.output([IN1, IN3], 0)
        GPIO.output([IN2, IN4], 1)
        robot_state['moving'] = True
        robot_state['direction'] = 'reverse'
        robot_state['target_speed'] = MAX_SPEED
    start_acceleration()

def left():
    """Turn robot left"""
    with movement_lock:
        GPIO.output(IN1, 0)
        GPIO.output(IN2, 1)
        GPIO.output(IN3, 1)
        GPIO.output(IN4, 0)
        robot_state['moving'] = True
        robot_state['direction'] = 'left'
        robot_state['target_speed'] = MAX_SPEED
    start_acceleration()

def right():
    """Turn robot right"""
    with movement_lock:
        GPIO.output(IN1, 1)
        GPIO.output(IN2, 0)
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 1)
        robot_state['moving'] = True
        robot_state['direction'] = 'right'
        robot_state['target_speed'] = MAX_SPEED
    start_acceleration()

def stop():
    """Stop robot"""
    with movement_lock:
        robot_state['target_speed'] = 0
        robot_state['moving'] = False
        robot_state['direction'] = 'stopped'
    
    # Wait for deceleration to complete
    time.sleep(0.3)
    
    with movement_lock:
        GPIO.output([IN1, IN2, IN3, IN4], 0)
        set_motor_speed(0)

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
    global stop_acceleration
    stop_acceleration.set()
    stop()
    pwm_a.stop()
    pwm_b.stop()
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
