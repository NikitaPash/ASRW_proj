"""
Tests for the Decorator pattern implementation.

This module tests the device decorators and their ability to add functionality
to base device objects while maintaining the same interface.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from src.smart_home.interfaces.device import Device, DeviceType, DeviceCapability
from src.smart_home.interfaces.event import EventPublisher, Event
from src.smart_home.devices.base_devices import SmartLight, Thermostat
from src.smart_home.devices.device_decorators import (
    TimerDecorator, LoggingDecorator, NotificationDecorator
)


class TestTimerDecorator:
    """Test suite for the TimerDecorator."""

    @pytest.fixture
    def light_device(self):
        """Create a base light device for testing."""
        return SmartLight("test-light", "Test Light", True, False)

    def test_maintains_device_interface(self, light_device):
        """Test that the decorator maintains the Device interface."""
        decorated = TimerDecorator(light_device)

        # Basic identity should be preserved
        assert decorated.get_id() == light_device.get_id()
        assert "Timer" in decorated.get_name()  # Should mention Timer in the name
        assert decorated.get_device_type() == light_device.get_device_type()
        assert decorated.get_capabilities() == light_device.get_capabilities()

        # State manipulation should work
        assert decorated.set_state({"power": True})
        assert decorated.get_state()["power"] is True

    def test_schedule_action(self, light_device):
        """Test scheduling a future state change."""
        decorated = TimerDecorator(light_device)

        # Initial state - no schedules
        state = decorated.get_state()
        assert state["has_schedules"] is False
        assert state["next_scheduled_action"] is None

        # Schedule a future action
        future_time = datetime.now() + timedelta(hours=1)
        result = decorated.schedule_action(future_time, {"power": True, "brightness": 75})
        assert result is True

        # Check state now shows the scheduled action
        state = decorated.get_state()
        assert state["has_schedules"] is True
        assert state["next_scheduled_action"] is not None
        assert "time" in state["next_scheduled_action"]
        assert "state_changes" in state["next_scheduled_action"]
        assert state["next_scheduled_action"]["state_changes"]["power"] is True
        assert state["next_scheduled_action"]["state_changes"]["brightness"] == 75

    def test_cannot_schedule_past_action(self, light_device):
        """Test that scheduling an action in the past fails."""
        decorated = TimerDecorator(light_device)

        # Try to schedule an action in the past
        past_time = datetime.now() - timedelta(minutes=5)
        result = decorated.schedule_action(past_time, {"power": True})
        assert result is False

        # State should show no schedules
        assert decorated.get_state()["has_schedules"] is False

    def test_cancel_schedules(self, light_device):
        """Test cancelling all schedules."""
        decorated = TimerDecorator(light_device)

        # Schedule a future action
        future_time = datetime.now() + timedelta(hours=1)
        decorated.schedule_action(future_time, {"power": True})
        assert decorated.get_state()["has_schedules"] is True

        # Cancel schedules
        decorated.cancel_all_schedules()
        assert decorated.get_state()["has_schedules"] is False
        assert decorated.get_state()["next_scheduled_action"] is None


class TestLoggingDecorator:
    """Test suite for the LoggingDecorator."""

    @pytest.fixture
    def thermostat_device(self):
        """Create a base thermostat device for testing."""
        return Thermostat("test-therm", "Test Thermostat")

    def test_maintains_device_interface(self, thermostat_device):
        """Test that the decorator maintains the Device interface."""
        decorated = LoggingDecorator(thermostat_device)

        # Basic identity should be preserved
        assert decorated.get_id() == thermostat_device.get_id()
        assert "Logging" in decorated.get_name()  # Should mention Logging in the name
        assert decorated.get_device_type() == thermostat_device.get_device_type()
        assert decorated.get_capabilities() == thermostat_device.get_capabilities()

        # State should include logging indicator
        assert decorated.get_state()["has_history"] is True

    def test_state_change_logging(self, thermostat_device):
        """Test that state changes are logged."""
        decorated = LoggingDecorator(thermostat_device)

        # Initial history should be empty
        assert len(decorated.get_history()) == 0

        # Make a state change
        decorated.set_state({"target_temperature": 22.5})

        # Check that the change was logged
        history = decorated.get_history()
        assert len(history) == 1
        assert "timestamp" in history[0]
        assert "changes" in history[0]
        assert "target_temperature" in history[0]["changes"]
        assert history[0]["changes"]["target_temperature"]["from"] == 21.0  # Default value
        assert history[0]["changes"]["target_temperature"]["to"] == 22.5

    def test_unchanged_state_not_logged(self, thermostat_device):
        """Test that setting the same state values doesn't create log entries."""
        decorated = LoggingDecorator(thermostat_device)

        # Set initial state
        decorated.set_state({"target_temperature": 22.5})
        assert len(decorated.get_history()) == 1

        # Set the same state again
        decorated.set_state({"target_temperature": 22.5})
        assert len(decorated.get_history()) == 1  # Should not add another entry

    def test_history_limit(self, thermostat_device):
        """Test that history is limited to max_history entries."""
        # Create decorator with small history limit
        decorated = LoggingDecorator(thermostat_device, max_history=2)

        # Make three state changes
        decorated.set_state({"target_temperature": 22.0})
        decorated.set_state({"target_temperature": 23.0})
        decorated.set_state({"target_temperature": 24.0})

        # History should only have the two most recent changes
        history = decorated.get_history()
        assert len(history) == 2
        assert history[0]["changes"]["target_temperature"]["to"] == 23.0
        assert history[1]["changes"]["target_temperature"]["to"] == 24.0

    def test_clear_history(self, thermostat_device):
        """Test clearing the history."""
        decorated = LoggingDecorator(thermostat_device)

        # Make a state change
        decorated.set_state({"target_temperature": 22.5})
        assert len(decorated.get_history()) == 1

        # Clear history
        decorated.clear_history()
        assert len(decorated.get_history()) == 0


class TestNotificationDecorator:
    """Test suite for the NotificationDecorator."""

    @pytest.fixture
    def lock_device(self):
        """Create a mock lock device for testing."""
        mock_device = MagicMock(spec=Device)
        mock_device.get_id.return_value = "test-lock"
        mock_device.get_name.return_value = "Test Lock"
        mock_device.get_device_type.return_value = DeviceType.LOCK
        mock_device.get_capabilities.return_value = [DeviceCapability.LOCK_UNLOCK]
        mock_device.get_state.return_value = {"locked": True, "battery_level": 90}

        # Track state changes
        self.device_state = {"locked": True, "battery_level": 90}

        def mock_set_state(state):
            self.device_state.update(state)
            mock_device.get_state.return_value = self.device_state.copy()
            return True

        mock_device.set_state.side_effect = mock_set_state

        return mock_device

    @pytest.fixture
    def event_publisher(self):
        """Create a mock event publisher."""
        publisher = MagicMock(spec=EventPublisher)
        return publisher

    def test_maintains_device_interface(self, lock_device, event_publisher):
        """Test that the decorator maintains the Device interface."""
        decorated = NotificationDecorator(lock_device, event_publisher)

        # Basic identity should be preserved
        assert decorated.get_id() == lock_device.get_id()
        assert "Notifications" in decorated.get_name()
        assert decorated.get_capabilities() == lock_device.get_capabilities()

        # State should include notifications indicator
        assert decorated.get_state()["notifications_enabled"] is True

    def test_publishes_event_on_state_change(self, lock_device, event_publisher):
        """Test that state changes generate events."""
        decorated = NotificationDecorator(lock_device, event_publisher)

        # Change the state
        decorated.set_state({"locked": False})

        # Verify an event was published
        event_publisher.notify.assert_called_once()

        # Check the event data
        event = event_publisher.notify.call_args[0][0]  # Get the first positional arg
        assert event.event_type.name == "DEVICE_STATE_CHANGED"
        assert event.source == lock_device.get_id()
        assert event.data["device_name"] == decorated.get_name()
        assert "old_state" in event.data
        assert "new_state" in event.data
        assert event.data["old_state"]["locked"] is True
        assert event.data["new_state"]["locked"] is False

    def test_custom_notification_criteria(self, lock_device, event_publisher):
        """Test using custom criteria for when to send notifications."""
        # Create a criteria function that only notifies on lock state changes
        def only_notify_lock_changes(old_state, new_state):
            return ("locked" in old_state and "locked" in new_state and
                    old_state["locked"] != new_state["locked"])

        decorated = NotificationDecorator(
            lock_device, event_publisher,
            notification_criteria=only_notify_lock_changes
        )

        # Change something that doesn't match criteria
        decorated.set_state({"battery_level": 85})
        assert event_publisher.notify.call_count == 0

        # Change something that does match criteria
        decorated.set_state({"locked": False})
        assert event_publisher.notify.call_count == 1
