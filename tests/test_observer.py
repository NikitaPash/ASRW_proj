"""
Tests for the Observer pattern implementation.

This module tests the event system components and their ability to
properly handle event publication and subscription.
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock

from src.smart_home.interfaces.event import (
    Event, EventType, EventSubscriber
)
from src.smart_home.automation.event_system import (
    EventManager, LoggingEventSubscriber, NotificationService
)


class TestEventManager:
    """Test suite for the EventManager class."""

    @pytest.fixture
    def event_manager(self):
        """Create an event manager for testing."""
        return EventManager()

    @pytest.fixture
    def mock_subscriber(self):
        """Create a mock event subscriber for testing."""
        subscriber = MagicMock(spec=EventSubscriber)
        subscriber.get_subscribed_event_types.return_value = [
            EventType.MOTION_DETECTED,
            EventType.DOOR_OPENED
        ]
        return subscriber

    def test_subscribe(self, event_manager, mock_subscriber):
        """Test subscribing to events."""
        counts = event_manager.get_subscriber_count()
        assert counts[EventType.MOTION_DETECTED] == 0
        assert counts[EventType.DOOR_OPENED] == 0

        event_manager.subscribe(mock_subscriber)

        counts = event_manager.get_subscriber_count()
        assert counts[EventType.MOTION_DETECTED] == 1
        assert counts[EventType.DOOR_OPENED] == 1
        assert counts[EventType.LIGHT_LEVEL_CHANGED] == 0

    def test_unsubscribe(self, event_manager, mock_subscriber):
        """Test unsubscribing from events."""
        event_manager.subscribe(mock_subscriber)
        assert event_manager.get_subscriber_count()[EventType.MOTION_DETECTED] == 1

        event_manager.unsubscribe(mock_subscriber)

        counts = event_manager.get_subscriber_count()
        assert counts[EventType.MOTION_DETECTED] == 0
        assert counts[EventType.DOOR_OPENED] == 0

    def test_notify(self, event_manager, mock_subscriber):
        """Test notifying subscribers about events."""
        event_manager.subscribe(mock_subscriber)

        event = Event(
            event_type=EventType.MOTION_DETECTED,
            source="test-sensor",
            data={"location": "living_room"}
        )

        event_manager.notify(event)

        mock_subscriber.update.assert_called_once_with(event)

    def test_notify_filtered_by_type(self, event_manager):
        """Test that subscribers only receive events of types they're interested in."""
        motion_subscriber = MagicMock(spec=EventSubscriber)
        motion_subscriber.get_subscribed_event_types.return_value = [EventType.MOTION_DETECTED]

        door_subscriber = MagicMock(spec=EventSubscriber)
        door_subscriber.get_subscribed_event_types.return_value = [EventType.DOOR_OPENED]

        event_manager.subscribe(motion_subscriber)
        event_manager.subscribe(door_subscriber)

        motion_event = Event(
            event_type=EventType.MOTION_DETECTED,
            source="test-sensor"
        )

        event_manager.notify(motion_event)

        motion_subscriber.update.assert_called_once_with(motion_event)
        door_subscriber.update.assert_not_called()


class TestLoggingEventSubscriber:
    """Test suite for the LoggingEventSubscriber class."""

    def test_subscribes_to_all_events_by_default(self):
        """Test that LoggingEventSubscriber defaults to subscribing to all event types."""
        subscriber = LoggingEventSubscriber()
        subscribed_types = subscriber.get_subscribed_event_types()

        assert len(subscribed_types) == len(list(EventType))
        for event_type in EventType:
            assert event_type in subscribed_types

    def test_subscribes_to_specified_events(self):
        """Test that LoggingEventSubscriber can subscribe to specific event types."""
        specific_types = [EventType.MOTION_DETECTED, EventType.SYSTEM_ALERT]
        subscriber = LoggingEventSubscriber(event_types=specific_types)

        subscribed_types = subscriber.get_subscribed_event_types()
        assert len(subscribed_types) == len(specific_types)
        for event_type in specific_types:
            assert event_type in subscribed_types

    def test_logs_events(self):
        """Test that events are properly logged."""
        subscriber = LoggingEventSubscriber()

        test_event = Event(
            event_type=EventType.MOTION_DETECTED,
            source="test-sensor",
            timestamp=datetime.now(),
            data={"location": "living_room", "confidence": 0.95}
        )

        subscriber.update(test_event)

        log = subscriber.get_log()
        assert len(log) == 1
        assert log[0]["type"] == "EventType.MOTION_DETECTED"
        assert log[0]["source"] == "test-sensor"
        assert log[0]["data"]["location"] == "living_room"
        assert log[0]["data"]["confidence"] == 0.95

    def test_respects_log_size_limit(self):
        """Test that the log size limit is respected."""
        subscriber = LoggingEventSubscriber(max_log_size=2)

        events = [
            Event(event_type=EventType.MOTION_DETECTED, source=f"sensor-{i}")
            for i in range(3)
        ]

        for event in events:
            subscriber.update(event)

        log = subscriber.get_log()
        assert len(log) == 2

        assert log[0]["source"] == "sensor-1"
        assert log[1]["source"] == "sensor-2"

    def test_clear_log(self):
        """Test clearing the log."""
        subscriber = LoggingEventSubscriber()

        subscriber.update(Event(event_type=EventType.MOTION_DETECTED, source="test"))
        assert len(subscriber.get_log()) == 1

        subscriber.clear_log()
        assert len(subscriber.get_log()) == 0


class TestNotificationService:
    """Test suite for the NotificationService class."""

    def test_default_event_subscriptions(self):
        """Test that NotificationService subscribes to appropriate default events."""
        service = NotificationService()
        subscribed_types = service.get_subscribed_event_types()

        assert EventType.MOTION_DETECTED in subscribed_types
        assert EventType.DOOR_OPENED in subscribed_types
        assert EventType.SYSTEM_ALERT in subscribed_types

    def test_custom_event_subscriptions(self):
        """Test that NotificationService can subscribe to custom event types."""
        custom_types = [EventType.TEMPERATURE_THRESHOLD_REACHED, EventType.LIGHT_LEVEL_CHANGED]
        service = NotificationService(event_types=custom_types)

        subscribed_types = service.get_subscribed_event_types()
        assert len(subscribed_types) == len(custom_types)
        for event_type in custom_types:
            assert event_type in subscribed_types

    def test_notification_creation(self, monkeypatch):
        """Test that notifications are properly created and tracked."""
        printed_messages = []
        monkeypatch.setattr('builtins.print', lambda msg: printed_messages.append(msg))

        service = NotificationService()

        test_event = Event(
            event_type=EventType.MOTION_DETECTED,
            source="front-camera",
            data={"location": "Front Door"}
        )

        service.update(test_event)

        history = service.get_notification_history()
        assert len(history) == 1
        assert history[0]["event_type"] == "EventType.MOTION_DETECTED"
        assert history[0]["source"] == "front-camera"
        assert "Motion detected" in history[0]["message"]

        assert len(printed_messages) == 1
        assert "NOTIFICATION" in printed_messages[0]
        assert "Motion detected" in printed_messages[0]

    def test_message_formatting_for_different_events(self, monkeypatch):
        """Test that different event types get appropriate message formats."""
        printed_messages = []
        monkeypatch.setattr('builtins.print', lambda msg: printed_messages.append(msg))

        service = NotificationService(event_types=[
            EventType.MOTION_DETECTED,
            EventType.DOOR_OPENED,
            EventType.SYSTEM_ALERT
        ])

        events = [
            Event(
                event_type=EventType.MOTION_DETECTED,
                source="hallway-sensor"
            ),
            Event(
                event_type=EventType.DOOR_OPENED,
                source="front-door"
            ),
            Event(
                event_type=EventType.SYSTEM_ALERT,
                source="system",
                data={"severity": "critical", "message": "Power outage detected"}
            )
        ]

        for event in events:
            service.update(event)

        history = service.get_notification_history()
        assert len(history) == 3

        assert "Motion detected by hallway-sensor" in history[0]["message"]
        assert "Door opened: front-door" in history[1]["message"]
        assert "CRITICAL ALERT" in history[2]["message"]
        assert "Power outage" in history[2]["message"]
