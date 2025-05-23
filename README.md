# Smart Home Automation System

A Python-based smart home automation system that demonstrates the implementation of three Gang-of-Four design patterns.

## Project Purpose & Scope

This project simulates a smart home automation system that allows users to:
- Control various smart devices (lights, thermostats, security cameras, etc.)
- Create and manage automation rules
- Monitor and respond to events in the home environment

The system is designed to demonstrate key software design patterns and principles while providing a realistic implementation scenario.

## Design Patterns Implemented

### 1. Factory Method (Creational Pattern)

**Intent**: Define an interface for creating an object, but let subclasses decide which class to instantiate. Factory Method lets a class defer instantiation to subclasses.

**Implementation**:
- `DeviceFactory`: Abstract factory interface for creating smart home devices
- Concrete factories: `LightingDeviceFactory`, `ClimateDeviceFactory`, etc.
- Each factory creates specific device types while following a common interface

**When to use**: When a class cannot anticipate the type of objects it must create, or when a class wants its subclasses to specify the objects it creates.

### 2. Decorator (Structural Pattern)

**Intent**: Attach additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing for extending functionality.

**Implementation**:
- Base `Device` component interface
- Concrete components: `SmartLight`, `Thermostat`, etc.
- Decorators: `TimerDecorator`, `SecurityDecorator`, `EnergyMonitorDecorator`, etc.
- Each decorator adds specific functionality to base devices (scheduling, security features, energy monitoring)

**When to use**: When you need to add responsibilities to objects dynamically without affecting other objects, or when extension by subclassing is impractical.

### 3. Observer (Behavioral Pattern)

**Intent**: Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically.

**Implementation**:
- `EventPublisher` subject interface
- Concrete subjects: `HomeSecuritySystem`, `EnvironmentalMonitor`
- `EventSubscriber` observer interface
- Concrete observers: `NotificationService`, `AutomationEngine`, `LoggingService`
- When events occur in the home, relevant services respond appropriately

**When to use**: When a change to one object requires changing others, and you don't know how many objects need to change or when.

## Design Principles Applied

### SOLID Principles

1. **Single Responsibility Principle**: Each class has one reason to change (e.g., device classes handle device operations, automation rules handle conditions and actions).

2. **Open/Closed Principle**: System is open for extension but closed for modification (new device types can be added without changing existing code).

3. **Liskov Substitution Principle**: Any derived class can be substituted for its base class (e.g., any device implementation can be used where Device interface is expected).

4. **Interface Segregation Principle**: Clients are not forced to depend on interfaces they don't use (separate interfaces for different device capabilities).

5. **Dependency Inversion Principle**: High-level modules depend on abstractions, not concrete implementations (automation engine works with device interfaces, not specific device classes).

### Other Design Principles

- **Composition over Inheritance**: Using composition (especially in the Decorator pattern) to achieve flexible designs.
- **Program to Interfaces**: System components interact through well-defined interfaces.
- **Favor Immutability**: State changes are handled through clear transactions rather than direct mutation where possible.

## Setup and Usage

### Requirements
- Python 3.8 or higher
- pytest (for running tests)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/smart-home-automation.git

# Navigate to project directory
cd smart-home-automation

# Install dependencies (if any)
pip install -r requirements.txt
```

### Running the Application
```bash
python -m src.main
```

### Running Tests
```bash
pytest
```

## Project Structure

```
smart-home-automation/
├── src/                   # Source code
│   ├── smart_home/        # Core package
│   │   ├── devices/       # Smart device implementations
│   │   ├── automation/    # Automation rules and engine
│   │   └── interfaces/    # Core interfaces and abstract classes
│   └── main.py            # Application entry point
├── tests/                 # Test suite
├── docs/                  # Additional documentation
│   └── class_diagram.png  # UML diagrams
└── README.md              # This file
```

## Extensibility & Scalability

The system is designed to be easily extended:
- New device types can be added by implementing the Device interface and creating a corresponding factory
- Additional decorators can be created to add new behaviors to devices
- New event types and observers can be added to respond to different scenarios

## Testing

The project includes over 20 unit tests covering:
- Device creation and operations
- Decorator functionality
- Observer pattern notifications
- Integration tests for automation scenarios

Each test verifies a specific aspect of functionality while ensuring the design patterns are implemented correctly.


