"""
Device decorator implementations for the Smart Home Automation system.

This module implements the Decorator pattern with concrete decorators
that add functionality to smart home devices.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable

from src.smart_home.interfaces.device import Device, DeviceCapability
from src.smart_home.interfaces.event import Event, EventType, EventPublisher


class TimerDecorator(Device):
    """
    Decorator that adds timing capabilities to devices.

    This decorator allows devices to be scheduled to change state at specific times.
    """

    def __init__(self, device: Device):
        """
        Initialize the timer decorator.

        Args:
            device: The device to decorate with timing functionality
        """
        self._device = device
        self._schedules = []  # List of scheduled actions

    def get_id(self) -> str:
        return self._device.get_id()

    def get_name(self) -> str:
        return f"{self._device.get_name()} (with Timer)"

    def get_device_type(self) -> Any:
        return self._device.get_device_type()

    def get_capabilities(self) -> List[DeviceCapability]:
        return self._device.get_capabilities()

    def get_state(self) -> Dict[str, Any]:
        # Add schedule information to the device state
        state = self._device.get_state()
        state['has_schedules'] = len(self._schedules) > 0
        state['next_scheduled_action'] = self._get_next_scheduled_action()
        return state

    def set_state(self, new_state: Dict[str, Any]) -> bool:
        return self._device.set_state(new_state)

    def supports_capability(self, capability: DeviceCapability) -> bool:
        return self._device.supports_capability(capability)

    def schedule_action(self, time: datetime, new_state: Dict[str, Any]) -> bool:
        """
        Schedule a state change to occur at a specific time.

        Args:
            time: When the state change should occur
            new_state: The state to apply at the scheduled time

        Returns:
            bool: True if the schedule was added successfully
        """
        if time <= datetime.now():
            return False  # Can't schedule in the past

        self._schedules.append({
            'time': time,
            'state': new_state
        })
        return True

    def cancel_all_schedules(self) -> None:
        """Cancel all scheduled actions for this device."""
        self._schedules = []

    def _get_next_scheduled_action(self) -> Optional[Dict[str, Any]]:
        """Get the next scheduled action, if any."""
        if not self._schedules:
            return None

        # Find the schedule with the closest time in the future
        now = datetime.now()
        future_schedules = [s for s in self._schedules if s['time'] > now]

        if not future_schedules:
            return None

        next_schedule = min(future_schedules, key=lambda s: s['time'])
        return {
            'time': next_schedule['time'].isoformat(),
            'state_changes': next_schedule['state']
        }


class LoggingDecorator(Device):
    """
    Decorator that adds logging capabilities to devices.

    This decorator records state changes to track device usage and history.
    """

    def __init__(self, device: Device, max_history: int = 100):
        """
        Initialize the logging decorator.

        Args:
            device: The device to decorate with logging functionality
            max_history: Maximum number of state changes to keep in history
        """
        self._device = device
        self._max_history = max_history
        self._history = []  # List of historical state changes

    def get_id(self) -> str:
        return self._device.get_id()

    def get_name(self) -> str:
        return f"{self._device.get_name()} (with Logging)"

    def get_device_type(self) -> Any:
        return self._device.get_device_type()

    def get_capabilities(self) -> List[DeviceCapability]:
        return self._device.get_capabilities()

    def get_state(self) -> Dict[str, Any]:
        state = self._device.get_state()
        state['has_history'] = True
        return state

    def set_state(self, new_state: Dict[str, Any]) -> bool:
        # Get the previous state for comparison
        old_state = self._device.get_state()

        # Try to update the device state
        success = self._device.set_state(new_state)

        if success:
            # Record the state change in history
            self._add_history_entry(old_state, new_state)

        return success

    def supports_capability(self, capability: DeviceCapability) -> bool:
        return self._device.supports_capability(capability)

    def get_history(self) -> List[Dict[str, Any]]:
        """Get the state change history for this device."""
        return self._history.copy()

    def clear_history(self) -> None:
        """Clear the state change history."""
        self._history = []

    def _add_history_entry(self, old_state: Dict[str, Any],
                          new_state: Dict[str, Any]) -> None:
        """Add a state change entry to the history."""
        # Only record changes, not the complete state
        changes = {}
        for key, new_value in new_state.items():
            if key in old_state and old_state[key] != new_value:
                changes[key] = {
                    'from': old_state[key],
                    'to': new_value
                }

        if changes:  # Only record if something actually changed
            entry = {
                'timestamp': datetime.now().isoformat(),
                'changes': changes
            }

            self._history.append(entry)

            # Maintain history size limit
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]


class NotificationDecorator(Device):
    """
    Decorator that adds notification capabilities to devices.

    This decorator publishes events when device state changes occur.
    It integrates with the Observer pattern.
    """

    def __init__(self, device: Device, event_publisher: EventPublisher,
                notification_criteria: Optional[Callable[[Dict[str, Any], Dict[str, Any]], bool]] = None):
        """
        Initialize the notification decorator.

        Args:
            device: The device to decorate with notification functionality
            event_publisher: Publisher to send events through
            notification_criteria: Optional function that determines when to send notifications
                                  Takes old_state and new_state as parameters
        """
        self._device = device
        self._publisher = event_publisher
        self._criteria = notification_criteria

    def get_id(self) -> str:
        return self._device.get_id()

    def get_name(self) -> str:
        return f"{self._device.get_name()} (with Notifications)"

    def get_device_type(self) -> Any:
        return self._device.get_device_type()

    def get_capabilities(self) -> List[DeviceCapability]:
        return self._device.get_capabilities()

    def get_state(self) -> Dict[str, Any]:
        state = self._device.get_state()
        state['notifications_enabled'] = True
        return state

    def set_state(self, new_state: Dict[str, Any]) -> bool:
        # Get the previous state for comparison
        old_state = self._device.get_state()

        # Try to update the device state
        success = self._device.set_state(new_state)

        if success:
            # Check if we should notify based on this state change
            should_notify = True
            if self._criteria:
                should_notify = self._criteria(old_state, self._device.get_state())

            if should_notify:
                self._publish_state_change_event(old_state, self._device.get_state())

        return success

    def supports_capability(self, capability: DeviceCapability) -> bool:
        return self._device.supports_capability(capability)

    def _publish_state_change_event(self, old_state: Dict[str, Any],
                                   new_state: Dict[str, Any]) -> None:
        """Publish an event for the state change."""
        event = Event(
            event_type=EventType.DEVICE_STATE_CHANGED,
            source=self.get_id(),
            data={
                'device_name': self.get_name(),
                'device_type': str(self.get_device_type()),
                'old_state': old_state,
                'new_state': new_state
            }
        )
        self._publisher.notify(event)
