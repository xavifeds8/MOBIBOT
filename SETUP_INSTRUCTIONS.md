# WiFi Robot Controller - Setup Instructions

## Overview
This WiFi-controlled robot system replaces the ultrasonic sensor with a web-based controller that you can access from your phone. The robot connects to your WiFi network and provides a mobile-friendly interface for controlling movement.

## Features
- ✅ WiFi-based control (no ultrasonic sensor needed)
- ✅ Mobile-friendly touch interface
- ✅ Real-time status updates
- ✅ Directional controls: Forward, Reverse, Left, Right, Stop
- ✅ Auto-stop when releasing buttons
- ✅ Works on any device with a web browser

## Hardware Requirements
- Raspberry Pi (any model with GPIO pins)
- Motor driver (L298N or similar)
- DC motors (2x)
- Power supply for motors
- WiFi connection

## Motor Connections
The code uses the following GPIO pins (BCM numbering):
- **IN1**: GPIO 23 (Motor 1 forward)
- **IN2**: GPIO 24 (Motor 1 reverse)
- **IN3**: GPIO 25 (Motor 2 forward)
- **IN4**: GPIO 8 (Motor 2 reverse)

**Note**: The ultrasonic sensor pins (GPIO 17 and 27) are no longer used.

## Installation Steps

### 1. Install Python Dependencies
```bash
cd /Users/xfernand/code/os/MOBIBOT
pip3 install -r requirements.txt
```

Or install individually:
```bash
pip3 install Flask==3.0.0
pip3 install flask-cors==4.0.0
pip3 install RPi.GPIO==0.7.1
```

### 2. Connect to WiFi
Ensure your Raspberry Pi is connected to your WiFi network. You can check your IP address with:
```bash
hostname -I
```

### 3. Run the Robot Controller
```bash
python3 wifi_robot.py
```

The server will start on port 5000. You should see:
```
Starting WiFi Robot Controller...
Access the controller at: http://<your-pi-ip>:5000
```

### 4. Access from Your Phone
1. Make sure your phone is on the same WiFi network as the Raspberry Pi
2. Open a web browser on your phone
3. Navigate to: `http://<your-pi-ip>:5000`
   - Replace `<your-pi-ip>` with your Raspberry Pi's IP address
   - Example: `http://192.168.1.100:5000`

## Usage

### Control Interface
The web interface provides a grid of control buttons:

```
        ▲
        (Forward)
    
◄       STOP      ►
(Left)           (Right)

        ▼
      (Reverse)
```

### How to Control
1. **Press and hold** any direction button to move the robot
2. **Release** the button to automatically stop
3. Use the **STOP** button for emergency stop
4. The status bar shows the current movement state

### Button Functions
- **▲ (Forward)**: Move robot forward
- **▼ (Reverse)**: Move robot backward
- **◄ (Left)**: Turn robot left
- **► (Right)**: Turn robot right
- **STOP**: Emergency stop (red button in center)

## Running on Startup (Optional)

To automatically start the robot controller when the Raspberry Pi boots:

### Method 1: Using systemd service
1. Create a service file:
```bash
sudo nano /etc/systemd/system/wifi-robot.service
```

2. Add the following content:
```ini
[Unit]
Description=WiFi Robot Controller
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/Users/xfernand/code/os/MOBIBOT
ExecStart=/usr/bin/python3 /Users/xfernand/code/os/MOBIBOT/wifi_robot.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl enable wifi-robot.service
sudo systemctl start wifi-robot.service
```

4. Check status:
```bash
sudo systemctl status wifi-robot.service
```

### Method 2: Using crontab
```bash
crontab -e
```

Add this line:
```
@reboot sleep 30 && cd /Users/xfernand/code/os/MOBIBOT && python3 wifi_robot.py &
```

## Troubleshooting

### Cannot Access Web Interface
- Verify Raspberry Pi IP address: `hostname -I`
- Check if server is running: `ps aux | grep wifi_robot`
- Ensure phone and Pi are on same WiFi network
- Try accessing from Pi browser first: `http://localhost:5000`

### Motors Not Working
- Check GPIO connections match the pin configuration
- Verify motor driver power supply
- Test GPIO pins: `gpio readall` (if wiringPi installed)
- Check for GPIO permission issues

### Connection Errors
- Restart the Flask server
- Check firewall settings: `sudo ufw status`
- Verify port 5000 is not blocked

### GPIO Cleanup Issues
If you get GPIO warnings, clean up manually:
```bash
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.cleanup()"
```

## API Endpoints

The server provides the following REST API endpoints:

### GET /
Returns the web interface (HTML page)

### POST /control
Control the robot movement
```json
{
  "command": "forward|reverse|left|right|stop"
}
```

Response:
```json
{
  "status": "success",
  "message": "Moving forward"
}
```

### GET /status
Get current robot status
```json
{
  "moving": true,
  "direction": "forward"
}
```

## Security Considerations

⚠️ **Important**: This is a basic implementation for local network use.

For production or public networks, consider:
- Adding authentication (username/password)
- Using HTTPS instead of HTTP
- Implementing rate limiting
- Adding IP whitelisting
- Using a VPN for remote access

## Customization

### Change Port
Edit `wifi_robot.py`, line with `app.run()`:
```python
app.run(host='0.0.0.0', port=8080, debug=False)  # Change 5000 to 8080
```

### Adjust Motor Pins
Edit the pin definitions at the top of `wifi_robot.py`:
```python
IN1, IN2, IN3, IN4 = 23, 24, 25, 8  # Change to your pins
```

### Modify UI Colors
Edit `templates/index.html` CSS section to change colors, sizes, or layout.

## Differences from Original Setup

### Removed
- ❌ Ultrasonic sensor (GPIO 17, 27)
- ❌ Autonomous obstacle avoidance
- ❌ Distance measurement
- ❌ Automatic navigation logic

### Added
- ✅ WiFi web server (Flask)
- ✅ Mobile-friendly web interface
- ✅ Manual control via phone/tablet
- ✅ Real-time status display
- ✅ REST API for control
- ✅ Touch-optimized buttons

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all connections and dependencies
3. Review the Flask server logs for errors
4. Test with a desktop browser first before mobile

## License
This project is open source and available for educational purposes.
