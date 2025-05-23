"""
Event interfaces for the Smart Home Automation system.

This module defines the core interfaces for the Observer pattern implementation,
which is used to handle events and notifications throughout the system.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class EventType(Enum):
    """Enumeration of supported event types in the system."""
    DEVICE_STATE_CHANGED = auto()
    MOTION_DETECTED = auto()
    DOOR_OPENED = auto()
    DOOR_CLOSED = auto()
    TEMPERATURE_THRESHOLD_REACHED = auto()
    HUMIDITY_THRESHOLD_REACHED = auto()
    LIGHT_LEVEL_CHANGED = auto()
    SYSTEM_ALERT = auto()
    USER_PRESENCE = auto()
    USER_ABSENCE = auto()
    SCHEDULED_EVENT = auto()


@dataclass
class Event:
    """Data class representing an event in the system."""
    event_type: EventType
    source: str  # ID of the event source (e.g., device_id)
    timestamp: datetime = None
    data: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize default values if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.data is None:
            self.data = {}


class EventSubscriber(ABC):
    """
    Abstract Observer interface for the Observer pattern.

    Objects implementing this interface can subscribe to and receive events.
    """

    @abstractmethod
    def update(self, event: Event) -> None:
        """
        Handle an event notification from a publisher.

        Args:
            event: The event that occurred
        """
        pass

    @abstractmethod
    def get_subscribed_event_types(self) -> List[EventType]:
        """
        Get the types of events this subscriber is interested in.

        Returns:
            List of event types this subscriber wants to be notified about
        """
        pass


class EventPublisher(ABC):
    """
    Abstract Subject interface for the Observer pattern.

    Objects implementing this interface can publish events to subscribers.
    """

    @abstractmethod
    def subscribe(self, subscriber: EventSubscriber) -> None:
        """
        Register a new subscriber for events.

        Args:
            subscriber: The subscriber to register
        """
        pass

    @abstractmethod
    def unsubscribe(self, subscriber: EventSubscriber) -> None:
        """
        Remove a subscriber from the notification list.

        Args:
            subscriber: The subscriber to remove
        """
        pass

    @abstractmethod
    def notify(self, event: Event) -> None:
        """
        Notify all relevant subscribers about an event.

        Args:
            event: The event to notify subscribers about
        """
        pass
