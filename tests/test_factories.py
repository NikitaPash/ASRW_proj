"""
Tests for the Factory Method pattern implementation.

This module tests the concrete device factories and their ability
to create appropriate device instances.
"""
import pytest

from src.smart_home.interfaces.device import DeviceType, DeviceCapability
from src.smart_home.devices.device_factories import (
    LightingDeviceFactory, ClimateDeviceFactory,
    SecurityDeviceFactory, SensorDeviceFactory
)


class TestLightingDeviceFactory:
    """Test suite for the LightingDeviceFactory."""

    def test_create_basic_light(self):
        """Test creating a basic light device."""
        factory = LightingDeviceFactory()
        device = factory.create_device("test-light-1", "Test Light")

        assert device is not None
        assert device.get_id() == "test-light-1"
        assert device.get_name() == "Test Light"
        assert device.get_device_type() == DeviceType.LIGHT
        assert DeviceCapability.POWER in device.get_capabilities()
        assert DeviceCapability.BRIGHTNESS in device.get_capabilities()
        assert not device.get_state()["power"]  # Default is off

    def test_create_non_dimmable_light(self):
        """Test creating a non-dimmable light."""
        factory = LightingDeviceFactory()
        device = factory.create_device(
            "test-light-2",
            "Non-dimmable Light",
            {"dimmable": False}
        )

        assert device is not None
        assert DeviceCapability.POWER in device.get_capabilities()
        assert DeviceCapability.BRIGHTNESS not in device.get_capabilities()

    def test_create_color_light(self):
        """Test creating a color-adjustable light."""
        factory = LightingDeviceFactory()
        device = factory.create_device(
            "test-light-3",
            "Color Light",
            {"dimmable": True, "color_adjustable": True}
        )

        assert device is not None
        assert DeviceCapability.POWER in device.get_capabilities()
        assert DeviceCapability.BRIGHTNESS in device.get_capabilities()
        assert DeviceCapability.COLOR in device.get_capabilities()

        # Check that color-related state variables exist
        state = device.get_state()
        assert "color" in state
        assert "color_temperature" in state


class TestClimateDeviceFactory:
    """Test suite for the ClimateDeviceFactory."""

    def test_create_thermostat(self):
        """Test creating a thermostat device."""
        factory = ClimateDeviceFactory()
        device = factory.create_device("test-therm-1", "Test Thermostat")

        assert device is not None
        assert device.get_id() == "test-therm-1"
        assert device.get_name() == "Test Thermostat"
        assert device.get_device_type() == DeviceType.THERMOSTAT
        assert DeviceCapability.TEMPERATURE in device.get_capabilities()

        # Check default thermostat state
        state = device.get_state()
        assert "current_temperature" in state
        assert "target_temperature" in state
        assert "mode" in state
        assert state["mode"] == "off"  # Default mode should be off

    def test_thermostat_custom_temperature_range(self):
        """Test creating a thermostat with custom temperature range."""
        factory = ClimateDeviceFactory()
        device = factory.create_device(
            "test-therm-2",
            "Custom Range Thermostat",
            {"min_temp": 5.0, "max_temp": 40.0}
        )

        assert device is not None

        # Test temperature validation by attempting to set an out-of-range value
        # Setting below minimum should fail
        result = device.set_state({"target_temperature": 4.0})
        assert not result

        # Setting within range should succeed
        result = device.set_state({"target_temperature": 25.0})
        assert result
        assert device.get_state()["target_temperature"] == 25.0

        # Setting above maximum should fail
        result = device.set_state({"target_temperature": 41.0})
        assert not result
        assert device.get_state()["target_temperature"] == 25.0  # Value shouldn't change


class TestSecurityDeviceFactory:
    """Test suite for the SecurityDeviceFactory."""

    def test_create_lock(self):
        """Test creating a smart lock device."""
        factory = SecurityDeviceFactory()
        device = factory.create_device("test-lock-1", "Test Lock")

        assert device is not None
        assert device.get_id() == "test-lock-1"
        assert device.get_name() == "Test Lock"
        assert device.get_device_type() == DeviceType.LOCK
        assert DeviceCapability.LOCK_UNLOCK in device.get_capabilities()

        # Check default lock state (should be locked)
        state = device.get_state()
        assert "locked" in state
        assert state["locked"] is True

    def test_create_camera(self):
        """Test creating a camera device."""
        factory = SecurityDeviceFactory()
        device = factory.create_device(
            "test-cam-1",
            "Test Camera",
            {"device_subtype": "camera"}
        )

        assert device is not None
        assert device.get_id() == "test-cam-1"
        assert device.get_name() == "Test Camera"
        assert device.get_device_type() == DeviceType.CAMERA
        assert DeviceCapability.VIDEO in device.get_capabilities()

        # Check camera capabilities
        assert DeviceCapability.MOTION in device.get_capabilities()  # Default has motion detection
        assert DeviceCapability.AUDIO in device.get_capabilities()   # Default has audio

    def test_create_camera_no_motion_no_audio(self):
        """Test creating a camera without motion detection or audio."""
        factory = SecurityDeviceFactory()
        device = factory.create_device(
            "test-cam-2",
            "Basic Camera",
            {
                "device_subtype": "camera",
                "has_motion_detection": False,
                "has_audio": False
            }
        )

        assert device is not None
        assert device.get_device_type() == DeviceType.CAMERA
        assert DeviceCapability.VIDEO in device.get_capabilities()
        assert DeviceCapability.MOTION not in device.get_capabilities()
        assert DeviceCapability.AUDIO not in device.get_capabilities()


class TestSensorDeviceFactory:
    """Test suite for the SensorDeviceFactory."""

    def test_create_motion_sensor(self):
        """Test creating a motion sensor device."""
        factory = SensorDeviceFactory()
        device = factory.create_device("test-sensor-1", "Test Sensor")

        assert device is not None
        assert device.get_id() == "test-sensor-1"
        assert device.get_name() == "Test Sensor"
        assert device.get_device_type() == DeviceType.SENSOR
        assert DeviceCapability.MOTION in device.get_capabilities()

        # Check default sensor state
        state = device.get_state()
        assert "motion_detected" in state
        assert not state["motion_detected"]  # Default is no motion
