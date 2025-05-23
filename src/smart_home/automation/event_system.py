"""
Event system implementation for the Smart Home Automation system.

This module provides concrete implementations of the Observer pattern
components for handling events in the smart home system.
"""
from typing import Dict, List, Set

from src.smart_home.interfaces.event import (
    Event, EventType, EventPublisher, EventSubscriber
)


class EventManager(EventPublisher):
    """
    Central event manager for the smart home system.

    This class implements the Subject role in the Observer pattern.
    It manages subscriptions and distributes events to interested subscribers.
    """

    def __init__(self):
        """Initialize the event manager with empty subscribers."""
        # Maps event types to sets of subscribers
        self._subscribers: Dict[EventType, Set[EventSubscriber]] = {}

        # Initialize with empty subscriber sets for each event type
        for event_type in EventType:
            self._subscribers[event_type] = set()

    def subscribe(self, subscriber: EventSubscriber) -> None:
        """
        Register a subscriber for events.

        The subscriber will be registered only for event types it's interested in.

        Args:
            subscriber: The subscriber to register
        """
        for event_type in subscriber.get_subscribed_event_types():
            self._subscribers[event_type].add(subscriber)

    def unsubscribe(self, subscriber: EventSubscriber) -> None:
        """
        Remove a subscriber from all event notifications.

        Args:
            subscriber: The subscriber to remove
        """
        for subscribers_set in self._subscribers.values():
            if subscriber in subscribers_set:
                subscribers_set.remove(subscriber)

    def notify(self, event: Event) -> None:
        """
        Notify all relevant subscribers about an event.

        Args:
            event: The event to notify subscribers about
        """
        # Get all subscribers for this event type
        subscribers = self._subscribers.get(event.event_type, set())

        # Notify each subscriber
        for subscriber in subscribers:
            subscriber.update(event)

    def get_subscriber_count(self) -> Dict[EventType, int]:
        """
        Get the count of subscribers for each event type.

        Returns:
            Dict mapping event types to subscriber counts
        """
        return {event_type: len(subscribers)
                for event_type, subscribers in self._subscribers.items()}


class LoggingEventSubscriber(EventSubscriber):
    """
    Event subscriber that logs all received events.

    This is a concrete Observer in the Observer pattern.
    """

    def __init__(self, event_types: List[EventType] = None, max_log_size: int = 1000):
        """
        Initialize the logging subscriber.

        Args:
            event_types: Types of events to subscribe to (default: all)
            max_log_size: Maximum number of events to keep in the log
        """
        self._event_types = event_types or list(EventType)
        self._max_log_size = max_log_size
        self._event_log = []

    def update(self, event: Event) -> None:
        """
        Handle an event notification by logging it.

        Args:
            event: The event that occurred
        """
        # Add event to the log
        log_entry = {
            'timestamp': event.timestamp.isoformat() if event.timestamp else None,
            'type': str(event.event_type),
            'source': event.source,
            'data': event.data
        }

        self._event_log.append(log_entry)

        # Maintain log size limit
        if len(self._event_log) > self._max_log_size:
            self._event_log = self._event_log[-self._max_log_size:]

    def get_subscribed_event_types(self) -> List[EventType]:
        """Get the types of events this subscriber is interested in."""
        return self._event_types

    def get_log(self) -> List[Dict]:
        """Get the current event log."""
        return self._event_log.copy()

    def clear_log(self) -> None:
        """Clear the event log."""
        self._event_log = []


class NotificationService(EventSubscriber):
    """
    Event subscriber that sends notifications based on events.

    This is a concrete Observer in the Observer pattern that demonstrates
    how the system could integrate with external notification services.
    """

    def __init__(self, event_types: List[EventType] = None):
        """
        Initialize the notification service.

        Args:
            event_types: Types of events to subscribe to (default: critical events)
        """
        # Default to important events if none specified
        if event_types is None:
            event_types = [
                EventType.MOTION_DETECTED,
                EventType.DOOR_OPENED,
                EventType.SYSTEM_ALERT
            ]

        self._event_types = event_types
        self._notification_history = []

    def update(self, event: Event) -> None:
        """
        Handle an event notification by sending a notification.

        Args:
            event: The event that occurred
        """
        # Create a user-friendly message based on the event
        message = self._create_message_for_event(event)

        # In a real system, this would send the notification via SMS, email, etc.
        # For this example, we just record that we would have sent a notification
        notification = {
            'timestamp': event.timestamp.isoformat() if event.timestamp else None,
            'message': message,
            'event_type': str(event.event_type),
            'source': event.source
        }

        self._notification_history.append(notification)

        # For demonstration, print that a notification would be sent
        print(f"NOTIFICATION: {message}")

    def get_subscribed_event_types(self) -> List[EventType]:
        """Get the types of events this subscriber is interested in."""
        return self._event_types

    def get_notification_history(self) -> List[Dict]:
        """Get the history of sent notifications."""
        return self._notification_history.copy()

    def _create_message_for_event(self, event: Event) -> str:
        """Create a user-friendly notification message for the given event."""
        if event.event_type == EventType.MOTION_DETECTED:
            return f"Motion detected by {event.source}!"

        elif event.event_type == EventType.DOOR_OPENED:
            return f"Door opened: {event.source}"

        elif event.event_type == EventType.SYSTEM_ALERT:
            severity = event.data.get('severity', 'unknown')
            return f"{severity.upper()} ALERT: {event.data.get('message', 'System alert')}"

        elif event.event_type == EventType.DEVICE_STATE_CHANGED:
            device_name = event.data.get('device_name', event.source)
            return f"Device state changed: {device_name}"

        else:
            # Generic message for other event types
            return f"Event occurred: {event.event_type} from {event.source}"
