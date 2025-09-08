# Contributing to MobileRobot

Thank you for your interest in contributing to the MobileRobot project! This document provides guidelines for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)

## Code of Conduct

This project adheres to a code of conduct that we expect all contributors to follow:
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/MobileRobot.git
   cd MobileRobot
   ```
3. **Set up the development environment** (see Development Setup below)

## Development Setup

### Prerequisites
- Raspberry Pi 4 or 5
- Python 3.8+
- Git

### Setup Instructions
1. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Making Changes

### Branching Strategy
- `master` - Stable release branch
- `develop` - Development branch for new features
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Critical fixes for production

### Creating a Feature Branch
```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### Making Commits
- Write clear, descriptive commit messages
- Keep commits focused on a single change
- Use conventional commit format when possible:
  ```
  type(scope): description
  
  Examples:
  feat(motor): add encoder calibration function
  fix(camera): resolve picamera2 initialization issue
  docs(readme): update installation instructions
  ```

## Submitting Changes

### Pull Request Process
1. **Update your branch** with the latest changes:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout feature/your-feature-name
   git rebase develop
   ```

2. **Test your changes** thoroughly:
   ```bash
   python robot_self_check.py
   ```

3. **Create a Pull Request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots/videos if applicable
   - Test results

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Tested on hardware
- [ ] Self-check script passes
- [ ] No breaking changes

## Screenshots/Videos
(if applicable)

## Related Issues
Closes #issue_number
```

## Coding Standards

### Python Style Guide
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep lines under 88 characters
- Use type hints where appropriate

### Example Function:
```python
def get_distance(self, motor: str, debug: bool = False) -> float:
    """
    Calculate distance traveled by a specific motor.
    
    Args:
        motor: Motor identifier ('LF', 'RF', 'LB', 'RB')
        debug: Enable debug output
        
    Returns:
        Distance traveled in meters
        
    Raises:
        ValueError: If motor identifier is invalid
    """
    # Implementation here
```

### Hardware Code Guidelines
- Always include proper error handling for hardware operations
- Implement cleanup functions for GPIO resources
- Use try-except blocks for I2C/SPI communications
- Add timeout mechanisms for sensor readings

## Testing

### Running Tests
```bash
# Hardware self-test
python robot_self_check.py

# Library tests (if available)
python -m pytest tests/

# Manual testing checklist
# - Motor movement
# - Encoder readings
# - Sensor functionality
# - Camera operation
```

### Test Requirements
- All new features must include tests
- Hardware-dependent code should have mock tests
- Performance-critical code needs benchmarks
- Document any hardware setup requirements

### Creating Tests
```python
def test_encoder_reading():
    """Test encoder reading functionality."""
    robot = RobotController()
    initial_count = robot.get_encoder('LF')
    robot.Forward(50)
    time.sleep(1)
    robot.Brake()
    final_count = robot.get_encoder('LF')
    assert final_count != initial_count
    robot.cleanup()
```

## Documentation

### Adding Documentation
- Update README.md for new features
- Add inline comments for complex logic
- Include usage examples
- Update CHANGELOG.md for all changes

### Documentation Format
- Use Markdown for all documentation
- Include code examples
- Add diagrams for hardware connections
- Keep language clear and beginner-friendly

## Questions and Support

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: Contact maintainers for sensitive issues

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to MobileRobot! 🤖
