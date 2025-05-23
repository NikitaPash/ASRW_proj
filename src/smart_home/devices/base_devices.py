"""
Base device implementations for the Smart Home Automation system.

This module provides concrete implementations of common smart home devices.
These serve as the ConcreteComponent classes in the Decorator pattern and
as the ConcreteProduct classes in the Factory Method pattern.
"""
from abc import ABC
from typing import Dict, Any, Optional, List

from src.smart_home.interfaces.device import Device, DeviceType, DeviceCapability
from src.smart_home.interfaces.event import Event, EventType, EventPublisher, EventSubscriber


class BaseDevice(Device, ABC):
    """Base implementation for all smart home devices."""

    def __init__(self, device_id: str, name: str):
        """
        Initialize a base device with essential properties.

        Args:
            device_id: Unique identifier for the device
            name: User-friendly name for the device
        """
        self._id = device_id
        self._name = name
        self._state = {"power": False}  # Default state - powered off

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self._name

    def get_state(self) -> Dict[str, Any]:
        return self._state.copy()  # Return a copy to prevent direct state manipulation

    def set_state(self, new_state: Dict[str, Any]) -> bool:
        """Update device state with new values."""
        try:
            # Only update keys that already exist in the state
            for key, value in new_state.items():
                if key in self._state:
                    self._state[key] = value
            return True
        except Exception:
            return False

    def supports_capability(self, capability: DeviceCapability) -> bool:
        """Check if this device has the specified capability."""
        return capability in self.get_capabilities()


class SmartLight(BaseDevice):
    """Smart light device implementation."""

    def __init__(self, device_id: str, name: str, dimmable: bool = True, color_adjustable: bool = False):
        """
        Initialize a smart light device.

        Args:
            device_id: Unique identifier for the device
            name: User-friendly name for the device
            dimmable: Whether the light supports brightness adjustment
            color_adjustable: Whether the light supports color adjustment
        """
        super().__init__(device_id, name)
        self._dimmable = dimmable
        self._color_adjustable = color_adjustable

        # Initialize state with appropriate properties
        self._state.update({
            "brightness": 100 if dimmable else None,
        })

        if color_adjustable:
            self._state.update({
                "color": "#FFFFFF",  # Default to white
                "color_temperature": 2700,  # Warm white in Kelvin
            })

    def get_device_type(self) -> DeviceType:
        return DeviceType.LIGHT

    def get_capabilities(self) -> List[DeviceCapability]:
        capabilities = [DeviceCapability.POWER]

        if self._dimmable:
            capabilities.append(DeviceCapability.BRIGHTNESS)

        if self._color_adjustable:
            capabilities.append(DeviceCapability.COLOR)

        return capabilities


class Thermostat(BaseDevice):
    """Smart thermostat device implementation."""

    def __init__(self, device_id: str, name: str,
                 min_temp: float = 10.0, max_temp: float = 32.0):
        """
        Initialize a smart thermostat device.

        Args:
            device_id: Unique identifier for the device
            name: User-friendly name for the device
            min_temp: Minimum supported temperature in Celsius
            max_temp: Maximum supported temperature in Celsius
        """
        super().__init__(device_id, name)
        self._min_temp = min_temp
        self._max_temp = max_temp

        # Initialize state with appropriate properties
        self._state.update({
            "current_temperature": 21.0,  # Default room temperature
            "target_temperature": 21.0,
            "mode": "off",  # off, heat, cool, auto
            "humidity": 50.0,  # Current humidity percentage
        })

    def get_device_type(self) -> DeviceType:
        return DeviceType.THERMOSTAT

    def get_capabilities(self) -> List[DeviceCapability]:
        return [DeviceCapability.POWER, DeviceCapability.TEMPERATURE]

    def set_state(self, new_state: Dict[str, Any]) -> bool:
        """Override to ensure temperature constraints."""
        if "target_temperature" in new_state:
            temp = new_state["target_temperature"]
            if not (self._min_temp <= temp <= self._max_temp):
                return False  # Temperature out of range

        return super().set_state(new_state)


class SmartLock(BaseDevice):
    """Smart lock device implementation."""

    def __init__(self, device_id: str, name: str):
        """
        Initialize a smart lock device.

        Args:
            device_id: Unique identifier for the device
            name: User-friendly name for the device
        """
        super().__init__(device_id, name)

        # Initialize state with appropriate properties
        self._state.update({
            "locked": True,  # Default to locked
            "battery_level": 100,  # Battery percentage
            "last_user": None,  # ID of last user to operate the lock
        })

    def get_device_type(self) -> DeviceType:
        return DeviceType.LOCK

    def get_capabilities(self) -> List[DeviceCapability]:
        return [DeviceCapability.LOCK_UNLOCK]


class Camera(BaseDevice):
    """Smart camera device implementation."""

    def __init__(self, device_id: str, name: str, has_motion_detection: bool = True,
                 has_audio: bool = True):
        """
        Initialize a smart camera device.

        Args:
            device_id: Unique identifier for the device
            name: User-friendly name for the device
            has_motion_detection: Whether the camera has motion detection
            has_audio: Whether the camera has audio capabilities
        """
        super().__init__(device_id, name)
        self._has_motion_detection = has_motion_detection
        self._has_audio = has_audio

        # Initialize state with appropriate properties
        self._state.update({
            "recording": False,
            "motion_detected": False,
            "resolution": "1080p",
        })

    def get_device_type(self) -> DeviceType:
        return DeviceType.CAMERA

    def get_capabilities(self) -> List[DeviceCapability]:
        capabilities = [DeviceCapability.POWER, DeviceCapability.VIDEO]

        if self._has_motion_detection:
            capabilities.append(DeviceCapability.MOTION)

        if self._has_audio:
            capabilities.append(DeviceCapability.AUDIO)

        return capabilities


class MotionSensor(BaseDevice):
    """Motion sensor device implementation."""

    def __init__(self, device_id: str, name: str):
        """
        Initialize a motion sensor device.

        Args:
            device_id: Unique identifier for the device
            name: User-friendly name for the device
        """
        super().__init__(device_id, name)

        # Initialize state with appropriate properties
        self._state.update({
            "motion_detected": False,
            "sensitivity": 5,  # 1-10 scale
            "battery_level": 100,  # Battery percentage
        })

    def get_device_type(self) -> DeviceType:
        return DeviceType.SENSOR

    def get_capabilities(self) -> List[DeviceCapability]:
        return [DeviceCapability.POWER, DeviceCapability.MOTION]
