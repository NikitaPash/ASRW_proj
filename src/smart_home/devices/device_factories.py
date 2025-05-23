"""
Device factory implementations for the Smart Home Automation system.

This module implements the Factory Method pattern with concrete factories
for creating different types of smart home devices.
"""
from typing import Dict, Any, Optional

from src.smart_home.interfaces.device import DeviceFactory, Device
from src.smart_home.devices.base_devices import (
    SmartLight, Thermostat, SmartLock, Camera, MotionSensor
)


class LightingDeviceFactory(DeviceFactory):
    """Factory for creating lighting devices."""

    def create_device(self, device_id: str, name: str, config: Optional[Dict[str, Any]] = None) -> Device:
        """
        Create a new smart light device.

        Args:
            device_id: Unique identifier for the device
            name: User-friendly name for the device
            config: Optional configuration with keys like:
                   - dimmable: bool
                   - color_adjustable: bool

        Returns:
            A SmartLight device instance
        """
        config = config or {}
        dimmable = config.get('dimmable', True)
        color_adjustable = config.get('color_adjustable', False)

        return SmartLight(device_id, name, dimmable, color_adjustable)


class ClimateDeviceFactory(DeviceFactory):
    """Factory for creating climate control devices."""

    def create_device(self, device_id: str, name: str, config: Optional[Dict[str, Any]] = None) -> Device:
        """
        Create a new thermostat device.

        Args:
            device_id: Unique identifier for the device
            name: User-friendly name for the device
            config: Optional configuration with keys like:
                   - min_temp: float
                   - max_temp: float

        Returns:
            A Thermostat device instance
        """
        config = config or {}
        min_temp = config.get('min_temp', 10.0)
        max_temp = config.get('max_temp', 32.0)

        return Thermostat(device_id, name, min_temp, max_temp)


class SecurityDeviceFactory(DeviceFactory):
    """Factory for creating security devices."""

    def create_device(self, device_id: str, name: str, config: Optional[Dict[str, Any]] = None) -> Device:
        """
        Create a new security device (lock or camera).

        Args:
            device_id: Unique identifier for the device
            name: User-friendly name for the device
            config: Optional configuration with keys like:
                   - device_subtype: str ("lock" or "camera")
                   - has_motion_detection: bool (for cameras)
                   - has_audio: bool (for cameras)

        Returns:
            A security device instance (SmartLock or Camera)
        """
        config = config or {}
        device_subtype = config.get('device_subtype', 'lock')

        if device_subtype == 'camera':
            has_motion = config.get('has_motion_detection', True)
            has_audio = config.get('has_audio', True)
            return Camera(device_id, name, has_motion, has_audio)
        else:  # Default to lock
            return SmartLock(device_id, name)


class SensorDeviceFactory(DeviceFactory):
    """Factory for creating sensor devices."""

    def create_device(self, device_id: str, name: str, config: Optional[Dict[str, Any]] = None) -> Device:
        """
        Create a new sensor device.

        Args:
            device_id: Unique identifier for the device
            name: User-friendly name for the device
            config: Optional configuration with keys like:
                   - sensor_type: str

        Returns:
            A sensor device instance
        """
        config = config or {}
        sensor_type = config.get('sensor_type', 'motion')

        # Currently we only have motion sensors implemented
        # This could be extended to support other sensor types
        return MotionSensor(device_id, name)
