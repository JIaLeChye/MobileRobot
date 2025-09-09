# RPi Robot Hat Library

A comprehensive library for controlling Raspberry Pi robot hat with motor control, encoder feedback, sensor integration, and autonomous navigation capabilities.

## Features

- **Motor Control**: Precise 4-wheel mecanum drive control
- **Encoder Feedback**: Real-time position and speed measurement
- **Sensor Integration**: Line sensors, battery monitoring
- **Servo Control**: 2-channel servo control
- **Buzzer Functions**: Sound and tone generation
- **Movement Functions**: Forward, backward, rotation, strafing
- **Distance Measurement**: Calibrated distance tracking
- **RPM Calculation**: Motor speed monitoring

## Installation

```bash
pip install rpi-robot-hat-lib
```

## Quick Start

```python
from RPi_Robot_Hat_Lib import RobotController

# Initialize robot
robot = RobotController()

# Basic movement
robot.Forward(50)        # Move forward at 50% speed
robot.turn_left(30)      # Turn left at 30% speed
robot.Horizontal_Left(40) # Strafe left at 40% speed
robot.stop()             # Stop all motors

# Encoder feedback
encoders = robot.get_all_encoders()
print(f"Encoder values: {encoders}")

# Distance measurement
distance = robot.move_distance(0.5)  # Move 50cm forward
print(f"Actual distance moved: {distance*100:.1f}cm")

# Cleanup
robot.cleanup()
```

## API Reference

### Motor Control
- `Forward(speed)` - Move forward (0-100%)
- `Backward(speed)` - Move backward (0-100%)
- `turn_left(speed)` - Turn left (0-100%)
- `turn_right(speed)` - Turn right (0-100%)
- `Horizontal_Left(speed)` - Strafe left (0-100%)
- `Horizontal_Right(speed)` - Strafe right (0-100%)
- `stop()` - Stop all motors

### Encoder Functions
- `get_encoder(motor)` - Get encoder count for specific motor
- `get_all_encoders()` - Get all encoder values
- `reset_encoders()` - Reset all encoders to zero
- `get_rpm(motor)` - Calculate RPM for specific motor
- `get_distance(motor)` - Get distance traveled by motor

### Movement Functions
- `move_distance(distance, speed)` - Move specific distance with feedback
- `move_distance_simple(distance_cm, speed)` - Simple distance movement

### System Functions
- `reset_system()` - Reset the robot controller
- `get_battery()` - Read battery voltage
- `cleanup()` - Clean up resources

## Requirements

- Python 3.7+
- Raspberry Pi 4/5
- rpi-lgpio
- smbus2

## License

MIT License
