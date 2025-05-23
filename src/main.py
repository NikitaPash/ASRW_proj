"""
Main application for the Smart Home Automation System.

This module demonstrates the integration of the three design patterns:
- Factory Method (Creational)
- Decorator (Structural)
- Observer (Behavioral)
"""
from src.smart_home.interfaces.device import DeviceCapability
from src.smart_home.interfaces.event import EventType, Event
from src.smart_home.devices.device_factories import (
    LightingDeviceFactory, ClimateDeviceFactory,
    SecurityDeviceFactory, SensorDeviceFactory
)
from src.smart_home.devices.device_decorators import (
    TimerDecorator, LoggingDecorator, NotificationDecorator
)
from src.smart_home.automation.event_system import (
    EventManager, LoggingEventSubscriber, NotificationService
)

def main():
    """Run a demonstration of the Smart Home Automation System."""
    print("Smart Home Automation System Demo")
    print("=================================")

    # Initialize the event system (Observer pattern)
    print("\nInitializing event system...")
    event_manager = EventManager()

    # Create event subscribers
    logger = LoggingEventSubscriber()
    notifier = NotificationService()

    # Register subscribers with the event manager
    event_manager.subscribe(logger)
    event_manager.subscribe(notifier)
    print(f"Event system initialized with {len(logger.get_subscribed_event_types())} event types.")

    # Create device factories (Factory Method pattern)
    print("\nCreating device factories...")
    light_factory = LightingDeviceFactory()
    climate_factory = ClimateDeviceFactory()
    security_factory = SecurityDeviceFactory()
    sensor_factory = SensorDeviceFactory()
    print("Device factories created.")

    # Create devices using factories
    print("\nCreating devices using factories...")
    living_room_light = light_factory.create_device(
        "light-living-1", "Living Room Light",
        {"dimmable": True, "color_adjustable": True}
    )

    bedroom_thermostat = climate_factory.create_device(
        "therm-bed-1", "Bedroom Thermostat",
        {"min_temp": 15.0, "max_temp": 28.0}
    )

    front_door_lock = security_factory.create_device(
        "lock-front-1", "Front Door Lock"
    )

    front_door_camera = security_factory.create_device(
        "cam-front-1", "Front Door Camera",
        {"device_subtype": "camera", "has_motion_detection": True}
    )

    motion_sensor = sensor_factory.create_device(
        "sensor-hall-1", "Hallway Motion Sensor"
    )
    print("Base devices created.")

    # Enhance devices with decorators (Decorator pattern)
    print("\nEnhancing devices with decorators...")

    # Add timing capabilities to the living room light
    scheduled_light = TimerDecorator(living_room_light)

    # Add logging to the thermostat
    logged_thermostat = LoggingDecorator(bedroom_thermostat)

    # Add notifications to the front door lock
    # Note how we integrate the Observer pattern with the Decorator pattern here
    notifying_lock = NotificationDecorator(front_door_lock, event_manager)

    # Stack multiple decorators - add both logging and notifications to the camera
    logged_camera = LoggingDecorator(front_door_camera)
    notifying_camera = NotificationDecorator(logged_camera, event_manager)

    print("Devices enhanced with decorators.")

    # Demonstrate using the enhanced devices
    print("\nDemonstrating enhanced device functionality...")

    # Using the scheduled light
    print("\n1. Scheduled Light Demonstration:")
    print(f"Initial state: {scheduled_light.get_state()}")
    scheduled_light.set_state({"power": True, "brightness": 80})
    print(f"After turning on: {scheduled_light.get_state()}")

    from datetime import datetime, timedelta
    future_time = datetime.now() + timedelta(hours=2)
    scheduled_light.schedule_action(future_time, {"power": False})
    print(f"After scheduling: {scheduled_light.get_state()}")

    # Using the logged thermostat
    print("\n2. Logged Thermostat Demonstration:")
    print(f"Initial state: {logged_thermostat.get_state()}")
    logged_thermostat.set_state({"target_temperature": 22.5, "mode": "heat"})
    print(f"After setting temperature: {logged_thermostat.get_state()}")
    print("History:")
    for entry in logged_thermostat.get_history():
        print(f"  - {entry['timestamp']}: {entry['changes']}")

    # Using the notifying lock
    print("\n3. Notifying Lock Demonstration:")
    print(f"Initial state: {notifying_lock.get_state()}")
    print("Unlocking the door (this will generate a notification)...")
    notifying_lock.set_state({"locked": False, "last_user": "user_123"})
    print(f"After unlocking: {notifying_lock.get_state()}")

    # Using the motion sensor to demonstrate the event system directly
    print("\n4. Motion Sensor & Event System Demonstration:")
    print("Simulating motion detection...")
    # Create and publish an event
    motion_event = Event(
        event_type=EventType.MOTION_DETECTED,
        source=motion_sensor.get_id(),
        data={"location": "Hallway", "confidence": 0.95}
    )
    event_manager.notify(motion_event)

    # Check the logged events
    print("\nEvent Log:")
    for entry in logger.get_log()[-2:]:  # Just show the last 2 events
        print(f"  - {entry['timestamp']}: {entry['type']} from {entry['source']}")

    print("\nSmart Home Automation System Demo completed.")


if __name__ == "__main__":
    main()
