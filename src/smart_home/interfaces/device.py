"""
Device interfaces for the Smart Home Automation system.

This module defines the core interfaces for all devices in the system,
supporting both the Factory Method and Decorator design patterns.
"""
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, Any, Optional


class DeviceType(Enum):
    """Enumeration of supported device types in the system."""
    LIGHT = auto()
    THERMOSTAT = auto()
    LOCK = auto()
    CAMERA = auto()
    SPEAKER = auto()
    SENSOR = auto()


class DeviceCapability(Enum):
    """Enumeration of capabilities that devices can support."""
    POWER = auto()  # Can be turned on/off
    BRIGHTNESS = auto()  # Has adjustable brightness
    COLOR = auto()  # Has adjustable color
    TEMPERATURE = auto()  # Can sense or set temperature
    MOTION = auto()  # Can detect motion
    AUDIO = auto()  # Can play or record audio
    VIDEO = auto()  # Can capture or display video
    LOCK_UNLOCK = auto()  # Can lock/unlock


class Device(ABC):
    """
    Base interface for all smart home devices.

    This interface serves as:
    1. The Component in the Decorator pattern
    2. The Product in the Factory Method pattern
    """

    @abstractmethod
    def get_id(self) -> str:
        """Get the unique identifier for this device."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the friendly name of this device."""
        pass

    @abstractmethod
    def get_device_type(self) -> DeviceType:
        """Get the type of this device."""
        pass

    @abstractmethod
    def get_capabilities(self) -> list[DeviceCapability]:
        """Get the list of capabilities this device supports."""
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the device as a dictionary."""
        pass

    @abstractmethod
    def set_state(self, new_state: Dict[str, Any]) -> bool:
        """
        Update the device state with the provided values.

        Args:
            new_state: Dictionary of state values to update

        Returns:
            bool: True if state was updated successfully, False otherwise
        """
        pass

    @abstractmethod
    def supports_capability(self, capability: DeviceCapability) -> bool:
        """Check if this device supports the specified capability."""
        pass


class DeviceDecorator(Device):
    """
    Base decorator for adding functionality to devices.

    This is the Decorator base class in the Decorator pattern.
    """

    def __init__(self, device: Device):
        """
        Initialize the decorator with the device to wrap.

        Args:
            device: The device to decorate with additional functionality
        """
        self._device = device

    def get_id(self) -> str:
        return self._device.get_id()

    def get_name(self) -> str:
        return self._device.get_name()

    def get_device_type(self) -> DeviceType:
        return self._device.get_device_type()

    def get_capabilities(self) -> list[DeviceCapability]:
        return self._device.get_capabilities()

    def get_state(self) -> Dict[str, Any]:
        return self._device.get_state()

    def set_state(self, new_state: Dict[str, Any]) -> bool:
        return self._device.set_state(new_state)

    def supports_capability(self, capability: DeviceCapability) -> bool:
        return self._device.supports_capability(capability)


class DeviceFactory(ABC):
    """
    Abstract Factory for creating smart home devices.

    This is the Creator in the Factory Method pattern.
    """

    @abstractmethod
    def create_device(self, device_id: str, name: str, config: Optional[Dict[str, Any]] = None) -> Device:
        """
        Create a new device with the given parameters.

        Args:
            device_id: Unique identifier for the device
            name: User-friendly name for the device
            config: Optional configuration parameters for the device

        Returns:
            A concrete Device instance
        """
        pass
