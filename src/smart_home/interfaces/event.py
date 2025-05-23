from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List


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
    source: str
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
        pass

    @abstractmethod
    def get_subscribed_event_types(self) -> List[EventType]:
        pass


class EventPublisher(ABC):
    """
    Abstract Subject interface for the Observer pattern.

    Objects implementing this interface can publish events to subscribers.
    """

    @abstractmethod
    def subscribe(self, subscriber: EventSubscriber) -> None:
        pass

    @abstractmethod
    def unsubscribe(self, subscriber: EventSubscriber) -> None:
        pass

    @abstractmethod
    def notify(self, event: Event) -> None:
        pass
