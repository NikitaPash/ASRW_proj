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
        self._subscribers: Dict[EventType, Set[EventSubscriber]] = {}

        for event_type in EventType:
            self._subscribers[event_type] = set()

    def subscribe(self, subscriber: EventSubscriber) -> None:
        for event_type in subscriber.get_subscribed_event_types():
            self._subscribers[event_type].add(subscriber)

    def unsubscribe(self, subscriber: EventSubscriber) -> None:
        for subscribers_set in self._subscribers.values():
            if subscriber in subscribers_set:
                subscribers_set.remove(subscriber)

    def notify(self, event: Event) -> None:
        subscribers = self._subscribers.get(event.event_type, set())

        for subscriber in subscribers:
            subscriber.update(event)

    def get_subscriber_count(self) -> Dict[EventType, int]:
        return {event_type: len(subscribers)
                for event_type, subscribers in self._subscribers.items()}


class LoggingEventSubscriber(EventSubscriber):
    """
    Event subscriber that logs all received events.

    This is a concrete Observer in the Observer pattern.
    """

    def __init__(self, event_types: List[EventType] = None, max_log_size: int = 1000):
        self._event_types = event_types or list(EventType)
        self._max_log_size = max_log_size
        self._event_log = []

    def update(self, event: Event) -> None:
        log_entry = {
            'timestamp': event.timestamp.isoformat() if event.timestamp else None,
            'type': str(event.event_type),
            'source': event.source,
            'data': event.data
        }

        self._event_log.append(log_entry)

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
        if event_types is None:
            event_types = [
                EventType.MOTION_DETECTED,
                EventType.DOOR_OPENED,
                EventType.SYSTEM_ALERT
            ]

        self._event_types = event_types
        self._notification_history = []

    def update(self, event: Event) -> None:
        message = self._create_message_for_event(event)

        notification = {
            'timestamp': event.timestamp.isoformat() if event.timestamp else None,
            'message': message,
            'event_type': str(event.event_type),
            'source': event.source
        }

        self._notification_history.append(notification)

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
            return f"Event occurred: {event.event_type} from {event.source}"
