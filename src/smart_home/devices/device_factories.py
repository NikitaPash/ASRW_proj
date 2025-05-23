from typing import Dict, Any, Optional

from src.smart_home.devices.base_devices import (
    SmartLight, Thermostat, SmartLock, Camera, MotionSensor
)
from src.smart_home.interfaces.device import DeviceFactory, Device


class LightingDeviceFactory(DeviceFactory):
    """Factory for creating lighting devices."""

    def create_device(self, device_id: str, name: str, config: Optional[Dict[str, Any]] = None) -> Device:
        config = config or {}
        dimmable = config.get('dimmable', True)
        color_adjustable = config.get('color_adjustable', False)

        return SmartLight(device_id, name, dimmable, color_adjustable)


class ClimateDeviceFactory(DeviceFactory):
    """Factory for creating climate control devices."""

    def create_device(self, device_id: str, name: str, config: Optional[Dict[str, Any]] = None) -> Device:
        config = config or {}
        min_temp = config.get('min_temp', 10.0)
        max_temp = config.get('max_temp', 32.0)

        return Thermostat(device_id, name, min_temp, max_temp)


class SecurityDeviceFactory(DeviceFactory):
    """Factory for creating security devices."""

    def create_device(self, device_id: str, name: str, config: Optional[Dict[str, Any]] = None) -> Device:
        config = config or {}
        device_subtype = config.get('device_subtype', 'lock')

        if device_subtype == 'camera':
            has_motion = config.get('has_motion_detection', True)
            has_audio = config.get('has_audio', True)
            return Camera(device_id, name, has_motion, has_audio)
        else:
            return SmartLock(device_id, name)


class SensorDeviceFactory(DeviceFactory):
    """Factory for creating sensor devices."""

    def create_device(self, device_id: str, name: str, config: Optional[Dict[str, Any]] = None) -> Device:
        config = config or {}
        config.get('sensor_type', 'motion')

        return MotionSensor(device_id, name)
