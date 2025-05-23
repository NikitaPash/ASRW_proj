import pytest
from unittest.mock import MagicMock, patch

from src.smart_home.interfaces.event import EventType, Event
from src.smart_home.automation.event_system import (
    EventManager, LoggingEventSubscriber, NotificationService
)
from src.smart_home.devices.device_factories import (
    LightingDeviceFactory, ClimateDeviceFactory, SecurityDeviceFactory
)

with patch('tkinter.Tk'):
    with patch('tkinter.ttk.Notebook'):
        with patch('tkinter.StringVar') as mock_string_var:
            with patch('tkinter.BooleanVar') as mock_bool_var:
                with patch('tkinter.IntVar') as mock_int_var:
                    with patch('tkinter.DoubleVar') as mock_double_var:
                        mock_instance = MagicMock()
                        mock_instance.get.side_effect = lambda: mock_instance.value
                        mock_string_var.return_value = mock_instance
                        mock_bool_var.return_value = mock_instance
                        mock_int_var.return_value = mock_instance
                        mock_double_var.return_value = mock_instance

                        from src.smart_home.gui.main_gui import SmartHomeGUI, launch_gui


class TestSmartHomeGUI:
    """Test the Smart Home GUI implementation."""

    @pytest.fixture
    def event_manager(self):
        """Create an event manager fixture."""
        manager = EventManager()
        logger = LoggingEventSubscriber()
        notifier = NotificationService()
        manager.subscribe(logger)
        manager.subscribe(notifier)
        return manager

    @pytest.fixture
    def mock_root(self):
        """Create a mock tkinter root window."""
        with patch('tkinter.Tk', autospec=True) as mock_tk:
            mock_root = mock_tk.return_value

            mock_root.title = MagicMock()
            mock_root.geometry = MagicMock()
            mock_root.protocol = MagicMock()

            mock_notebook = MagicMock()

            def mock_widget_create(*args, **kwargs):
                widget = MagicMock()
                widget.grid = MagicMock()
                widget.pack = MagicMock()
                widget.config = MagicMock()
                widget.winfo_children = MagicMock(return_value=[])
                return widget

            mock_frame = mock_widget_create()

            with patch('tkinter.ttk.Notebook', return_value=mock_notebook):
                with patch('tkinter.ttk.Frame', return_value=mock_frame):
                    with patch('tkinter.ttk.LabelFrame', return_value=mock_frame):
                        with patch('tkinter.scrolledtext.ScrolledText', return_value=MagicMock()):
                            yield mock_root

    @pytest.fixture
    def mock_tk_vars(self):
        """Create mock tkinter variables."""
        with patch('tkinter.StringVar') as mock_string_var:
            with patch('tkinter.BooleanVar') as mock_bool_var:
                with patch('tkinter.IntVar') as mock_int_var:
                    with patch('tkinter.DoubleVar') as mock_double_var:
                        string_var = MagicMock()
                        string_var.get = MagicMock(return_value="test_value")
                        string_var.set = MagicMock()
                        string_var.trace_add = MagicMock()

                        bool_var = MagicMock()
                        bool_var.get = MagicMock(return_value=True)
                        bool_var.set = MagicMock()
                        bool_var.trace_add = MagicMock()

                        int_var = MagicMock()
                        int_var.get = MagicMock(return_value=50)
                        int_var.set = MagicMock()
                        int_var.trace_add = MagicMock()

                        double_var = MagicMock()
                        double_var.get = MagicMock(return_value=22.5)
                        double_var.set = MagicMock()
                        double_var.trace_add = MagicMock()

                        mock_string_var.return_value = string_var
                        mock_bool_var.return_value = bool_var
                        mock_int_var.return_value = int_var
                        mock_double_var.return_value = double_var

                        yield {
                            'StringVar': mock_string_var,
                            'BooleanVar': mock_bool_var,
                            'IntVar': mock_int_var,
                            'DoubleVar': mock_double_var,
                            'string_instance': string_var,
                            'bool_instance': bool_var,
                            'int_instance': int_var,
                            'double_instance': double_var
                        }

    @pytest.fixture
    def gui(self, mock_root, event_manager, mock_tk_vars):
        """Create a GUI instance for testing."""
        with patch('threading.Thread') as mock_thread:
            with patch('tkinter.ttk.Button'):
                with patch('tkinter.ttk.Label'):
                    with patch('tkinter.ttk.Entry'):
                        with patch('tkinter.ttk.Combobox'):
                            with patch('tkinter.ttk.Treeview'):
                                with patch('tkinter.ttk.Checkbutton'):
                                    with patch('tkinter.ttk.Scrollbar'):
                                        with patch('tkinter.ttk.Scale'):
                                            mock_thread_instance = MagicMock()
                                            mock_thread.return_value = mock_thread_instance

                                            gui = SmartHomeGUI(mock_root, event_manager)

                                            gui.sim_event_type = mock_tk_vars['string_instance']
                                            gui.sim_source = mock_tk_vars['string_instance']
                                            gui.sim_data = mock_tk_vars['string_instance']
                                            gui.notify_motion = mock_tk_vars['bool_instance']
                                            gui.notify_door = mock_tk_vars['bool_instance']
                                            gui.notify_system = mock_tk_vars['bool_instance']

                                            return gui

    def test_gui_initialization(self, gui, mock_root):
        """Test that the GUI initializes correctly."""
        mock_root.title.assert_called_once_with("Smart Home Automation System")

        mock_root.geometry.assert_called_once_with("900x600")

        assert len(gui.device_factories) > 0
        assert gui.devices is not None

    @patch('src.smart_home.gui.main_gui.SmartHomeGUI._refresh_device_list')
    def test_create_demo_devices(self, mock_refresh, gui):
        """Test that demo devices are created correctly."""
        gui.devices = {}

        with patch.object(LightingDeviceFactory, 'create_device') as mock_light_factory:
            with patch.object(ClimateDeviceFactory, 'create_device') as mock_climate_factory:
                with patch.object(SecurityDeviceFactory, 'create_device') as mock_security_factory:
                    mock_light = MagicMock()
                    mock_light.get_id.return_value = "light-living-1"
                    mock_light.get_state.return_value = {"power": True, "brightness": 80}

                    mock_therm = MagicMock()
                    mock_therm.get_id.return_value = "therm-bed-1"
                    mock_therm.get_state.return_value = {"target_temperature": 22.5}

                    mock_lock = MagicMock()
                    mock_lock.get_id.return_value = "lock-front-1"
                    mock_lock.get_state.return_value = {"locked": True}

                    mock_light_factory.return_value = mock_light
                    mock_climate_factory.return_value = mock_therm
                    mock_security_factory.return_value = mock_lock

                    gui._create_demo_devices()

                    mock_light_factory.assert_called_with(
                        "light-living-1", "Living Room Light",
                        {"dimmable": True, "color_adjustable": True}
                    )

                    mock_climate_factory.assert_called_with(
                        "therm-bed-1", "Bedroom Thermostat",
                        {"min_temp": 15.0, "max_temp": 28.0}
                    )

                    mock_security_factory.assert_called_with(
                        "lock-front-1", "Front Door Lock"
                    )

                    mock_refresh.assert_called_once()

    @patch('tkinter.messagebox.showinfo')
    def test_generate_test_event(self, mock_showinfo, gui, event_manager):
        """Test generating a test event from the GUI."""
        mock_logger = MagicMock()
        mock_logger.get_subscribed_event_types = MagicMock(return_value=[EventType.SYSTEM_ALERT])
        mock_logger.update = MagicMock()
        event_manager.subscribe(mock_logger)

        gui._generate_test_event()

        mock_logger.update.assert_called_once()
        args, _ = mock_logger.update.call_args
        event = args[0]

        assert event.event_type == EventType.SYSTEM_ALERT
        assert event.source == "system"
        assert "message" in event.data
        assert event.data["severity"] == "info"

        mock_showinfo.assert_called_once()

    def test_update_device_state(self, gui):
        """Test updating a device state through the GUI."""
        mock_device = MagicMock()
        mock_device.set_state = MagicMock()
        mock_device.get_state = MagicMock(return_value={"power": True})

        gui._refresh_device_list = MagicMock()
        gui._on_device_select = MagicMock()

        gui._update_device_state(mock_device, {"brightness": 75})

        mock_device.set_state.assert_called_once_with({"brightness": 75})

        gui._refresh_device_list.assert_called_once()
        gui._on_device_select.assert_called_once()

    @patch('tkinter.messagebox.showerror')
    def test_update_device_state_error(self, mock_showerror, gui):
        """Test error handling when updating device state."""
        mock_device = MagicMock()
        mock_device.set_state = MagicMock(side_effect=ValueError("Test error"))

        gui._refresh_device_list = MagicMock()
        gui._on_device_select = MagicMock()

        gui._update_device_state(mock_device, {"power": True})

        mock_showerror.assert_called_once()
        args, _ = mock_showerror.call_args
        assert "Error" == args[0]
        assert "Test error" in args[1]

    def test_notification_preferences(self, gui, event_manager):
        """Test updating notification preferences."""
        mock_notifier = MagicMock(spec=NotificationService)
        mock_notifier._event_types = []
        gui._find_subscribers_by_type = MagicMock(return_value=[mock_notifier])

        with patch('tkinter.messagebox.showinfo') as mock_showinfo:
            gui._update_notification_preferences()

        assert EventType.MOTION_DETECTED in mock_notifier._event_types
        assert EventType.SYSTEM_ALERT in mock_notifier._event_types

    def test_find_subscribers_by_type(self, gui, event_manager):
        """Test finding subscribers by type."""
        logger = LoggingEventSubscriber()
        notifier = NotificationService()
        event_manager.subscribe(logger)
        event_manager.subscribe(notifier)

        gui.event_manager = event_manager

        loggers = gui._find_subscribers_by_type(LoggingEventSubscriber)
        notifiers = gui._find_subscribers_by_type(NotificationService)

        assert len(loggers) >= 1
        assert len(notifiers) >= 1
        assert all(isinstance(sub, LoggingEventSubscriber) for sub in loggers)
        assert all(isinstance(sub, NotificationService) for sub in notifiers)

    @patch('tkinter.Tk')
    @patch('src.smart_home.gui.main_gui.SmartHomeGUI')
    def test_launch_gui(self, mock_gui_class, mock_tk, event_manager):
        """Test the GUI launch function."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_gui = MagicMock()
        mock_gui_class.return_value = mock_gui

        with patch('tkinter.mainloop'):
            launch_gui(event_manager)

        mock_gui_class.assert_called_once()

        mock_root.protocol.assert_called_once()

        assert mock_root.mainloop.called

    def test_add_device_controls(self, gui):
        """Test adding device controls based on capabilities."""
        parent_frame = MagicMock()

        mock_device = MagicMock()
        mock_device.get_state = MagicMock(return_value={
            "power": True,
            "brightness": 80,
            "target_temperature": 22.0,
            "locked": True
        })

        with patch('tkinter.BooleanVar') as mock_bool_var:
            bool_instance = MagicMock()
            bool_instance.get = MagicMock(return_value=True)
            mock_bool_var.return_value = bool_instance

            row = 0
            new_row = gui._add_power_controls(mock_device, parent_frame, row)
            assert new_row > row

        with patch('tkinter.IntVar') as mock_int_var:
            int_instance = MagicMock()
            int_instance.get = MagicMock(return_value=80)
            mock_int_var.return_value = int_instance

            row = new_row
            new_row = gui._add_brightness_controls(mock_device, parent_frame, row)
            assert new_row > row

        with patch('tkinter.DoubleVar') as mock_double_var:
            with patch('tkinter.StringVar') as mock_string_var:
                double_instance = MagicMock()
                double_instance.get = MagicMock(return_value=22.0)
                mock_double_var.return_value = double_instance

                string_instance = MagicMock()
                string_instance.get = MagicMock(return_value="heat")
                mock_string_var.return_value = string_instance

                row = new_row
                new_row = gui._add_temperature_controls(mock_device, parent_frame, row)
                assert new_row > row

        row = new_row
        new_row = gui._add_lock_controls(mock_device, parent_frame, row)
        assert new_row > row


class TestIntegration:
    """End-to-end integration tests for the Smart Home system with GUI."""

    def test_event_system_integration(self):
        """Test that the event system works correctly with the GUI."""
        event_manager = EventManager()
        logger = LoggingEventSubscriber()
        notifier = NotificationService()
        event_manager.subscribe(logger)
        event_manager.subscribe(notifier)

        test_event = Event(
            event_type=EventType.SYSTEM_ALERT,
            source="test-source",
            data={"message": "Integration test", "severity": "high"}
        )

        event_manager.notify(test_event)

        log_entries = logger.get_log()
        assert len(log_entries) > 0
        latest_entry = log_entries[-1]
        assert latest_entry["type"] == str(EventType.SYSTEM_ALERT)
        assert latest_entry["source"] == "test-source"

        notifications = notifier.get_notification_history()
        assert len(notifications) > 0
        latest_notification = notifications[-1]
        assert "ALERT" in latest_notification["message"]
        assert latest_notification["source"] == "test-source"

    def test_device_factory_integration(self):
        """Test device factory integration with the system."""
        light_factory = LightingDeviceFactory()
        climate_factory = ClimateDeviceFactory()
        security_factory = SecurityDeviceFactory()

        light = light_factory.create_device("test-light", "Test Light")
        thermostat = climate_factory.create_device("test-therm", "Test Thermostat")
        lock = security_factory.create_device("test-lock", "Test Lock")

        assert light.get_id() == "test-light"
        assert light.get_name() == "Test Light"

        assert thermostat.get_id() == "test-therm"
        assert thermostat.get_name() == "Test Thermostat"

        assert lock.get_id() == "test-lock"
        assert lock.get_name() == "Test Lock"

        light.set_state({"power": True, "brightness": 75})
        thermostat.set_state({"target_temperature": 23.5})
        lock.set_state({"locked": True})

        assert light.get_state()["power"] is True
        assert light.get_state()["brightness"] == 75
        assert thermostat.get_state()["target_temperature"] == 23.5
        assert lock.get_state()["locked"] is True


if __name__ == "__main__":
    pytest.main(['-xvs', __file__])
