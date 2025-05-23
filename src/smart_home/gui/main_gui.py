import threading
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from src.smart_home.automation.event_system import EventManager, LoggingEventSubscriber, NotificationService
from src.smart_home.devices.device_factories import (
    LightingDeviceFactory, ClimateDeviceFactory,
    SecurityDeviceFactory, SensorDeviceFactory
)
from src.smart_home.interfaces.device import DeviceType, DeviceCapability
from src.smart_home.interfaces.event import EventType, Event


class SmartHomeGUI:
    """Main GUI class for the Smart Home Automation System."""

    def __init__(self, root: tk.Tk, event_manager: EventManager):
        self.root = root
        self.root.title("Smart Home Automation System")
        self.root.geometry("900x600")
        self.event_manager = event_manager

        self.devices = {}
        self.device_factories = self._create_factories()

        self.device_icons = {
            DeviceType.LIGHT: "💡",
            DeviceType.THERMOSTAT: "🌡️",
            DeviceType.LOCK: "🔒",
            DeviceType.CAMERA: "📹",
            DeviceType.SPEAKER: "🔊",
            DeviceType.SENSOR: "📡"
        }

        self._create_widgets()

        self.log_update_active = True
        self.log_thread = threading.Thread(target=self._update_logs_periodically, daemon=True)
        self.log_thread.start()

    def _create_factories(self):
        """Create all device factories."""
        return {
            DeviceType.LIGHT: LightingDeviceFactory(),
            DeviceType.THERMOSTAT: ClimateDeviceFactory(),
            DeviceType.LOCK: SecurityDeviceFactory(),
            DeviceType.CAMERA: SecurityDeviceFactory(),
            DeviceType.SENSOR: SensorDeviceFactory()
        }

    def _create_widgets(self):
        """Create all GUI widgets."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.dashboard_frame = ttk.Frame(self.notebook)
        self.devices_frame = ttk.Frame(self.notebook)
        self.events_frame = ttk.Frame(self.notebook)
        self.notifications_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.notebook.add(self.devices_frame, text="Devices")
        self.notebook.add(self.events_frame, text="Events")
        self.notebook.add(self.notifications_frame, text="Notifications")

        self._setup_dashboard_tab()
        self._setup_devices_tab()
        self._setup_events_tab()
        self._setup_notifications_tab()

    def _setup_dashboard_tab(self):
        """Setup the dashboard tab."""
        status_frame = ttk.LabelFrame(self.dashboard_frame, text="System Status")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(status_frame, text="Smart Home System Active", font=("Arial", 14)).pack(pady=10)

        status_indicators = ttk.Frame(status_frame)
        status_indicators.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(status_indicators, text="🟢 Event System: Running").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(status_indicators, text="🟢 Device Management: Ready").grid(row=1, column=0, sticky="w", padx=5,
                                                                             pady=5)
        ttk.Label(status_indicators, text="🟢 Notification Service: Active").grid(row=0, column=1, sticky="w", padx=5,
                                                                                 pady=5)
        ttk.Label(status_indicators, text="🟢 Automation: Enabled").grid(row=1, column=1, sticky="w", padx=5, pady=5)

        actions_frame = ttk.LabelFrame(self.dashboard_frame, text="Quick Actions")
        actions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Button(actions_frame, text="Add New Device", command=self._show_add_device_dialog).grid(
            row=0, column=0, padx=10, pady=10)
        ttk.Button(actions_frame, text="Generate System Test Event", command=self._generate_test_event).grid(
            row=0, column=1, padx=10, pady=10)
        ttk.Button(actions_frame, text="Clear Event Log", command=self._clear_event_log).grid(
            row=0, column=2, padx=10, pady=10)

        self.recent_events_frame = ttk.LabelFrame(self.dashboard_frame, text="Recent Events")
        self.recent_events_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.recent_events_text = scrolledtext.ScrolledText(self.recent_events_frame, height=5)
        self.recent_events_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.recent_events_text.config(state=tk.DISABLED)

    def _setup_devices_tab(self):
        """Setup the devices tab."""
        devices_panel = ttk.Frame(self.devices_frame)
        devices_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        toolbar = ttk.Frame(devices_panel)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Add Device", command=self._show_add_device_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Refresh", command=self._refresh_device_list).pack(side=tk.LEFT, padx=2)

        list_frame = ttk.Frame(devices_panel)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "name", "type", "state")
        self.device_tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        self.device_tree.heading("id", text="Device ID")
        self.device_tree.heading("name", text="Name")
        self.device_tree.heading("type", text="Type")
        self.device_tree.heading("state", text="State")

        self.device_tree.column("id", width=100)
        self.device_tree.column("name", width=150)
        self.device_tree.column("type", width=100)
        self.device_tree.column("state", width=150)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.device_tree.yview)
        self.device_tree.configure(yscroll=scrollbar.set)

        self.device_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.device_tree.bind("<<TreeviewSelect>>", self._on_device_select)

        self.device_details_panel = ttk.LabelFrame(self.devices_frame, text="Device Details")
        self.device_details_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.device_placeholder = ttk.Label(self.device_details_panel,
                                            text="Select a device to view details and controls")
        self.device_placeholder.pack(pady=50)

        self.device_control_panel = ttk.Frame(self.device_details_panel)

        self._create_demo_devices()

    def _setup_events_tab(self):
        """Setup the events tab."""
        log_frame = ttk.Frame(self.events_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        controls = ttk.Frame(log_frame)
        controls.pack(fill=tk.X, pady=5)

        ttk.Button(controls, text="Clear Log", command=self._clear_event_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Refresh", command=self._refresh_event_log).pack(side=tk.LEFT, padx=5)

        ttk.Label(controls, text="Filter by event type:").pack(side=tk.LEFT, padx=10)
        self.event_type_var = tk.StringVar(value="All")
        event_filter = ttk.Combobox(controls, textvariable=self.event_type_var)
        event_filter['values'] = ['All'] + [e.name for e in EventType]
        event_filter.pack(side=tk.LEFT, padx=5)
        event_filter.bind('<<ComboboxSelected>>', self._refresh_event_log)

        self.event_log_text = scrolledtext.ScrolledText(log_frame)
        self.event_log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.event_log_text.config(state=tk.DISABLED)

        simulator_frame = ttk.LabelFrame(self.events_frame, text="Event Simulator")
        simulator_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(simulator_frame, text="Event Type:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.sim_event_type = tk.StringVar()
        event_type_combo = ttk.Combobox(simulator_frame, textvariable=self.sim_event_type)
        event_type_combo['values'] = [e.name for e in EventType]
        event_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        event_type_combo.current(0)

        ttk.Label(simulator_frame, text="Source:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.sim_source = tk.StringVar(value="simulator-device-1")
        ttk.Entry(simulator_frame, textvariable=self.sim_source).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(simulator_frame, text="Data (JSON):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.sim_data = tk.StringVar(value='{"message": "Test event", "severity": "low"}')
        ttk.Entry(simulator_frame, textvariable=self.sim_data, width=40).grid(row=2, column=1, padx=5, pady=5,
                                                                              sticky="w")

        ttk.Button(simulator_frame, text="Generate Event", command=self._generate_simulated_event).grid(
            row=3, column=0, columnspan=2, padx=5, pady=10)

    def _setup_notifications_tab(self):
        """Setup the notifications tab."""
        notifications_frame = ttk.Frame(self.notifications_frame)
        notifications_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        controls = ttk.Frame(notifications_frame)
        controls.pack(fill=tk.X, pady=5)

        ttk.Button(controls, text="Clear Notifications", command=self._clear_notifications).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls, text="Refresh", command=self._refresh_notifications).pack(side=tk.LEFT, padx=5)

        settings_frame = ttk.LabelFrame(notifications_frame, text="Notification Settings")
        settings_frame.pack(fill=tk.X, pady=5)

        self.notify_motion = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Motion Events", variable=self.notify_motion).grid(
            row=0, column=0, padx=10, pady=5, sticky="w")

        self.notify_door = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Door Events", variable=self.notify_door).grid(
            row=0, column=1, padx=10, pady=5, sticky="w")

        self.notify_system = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="System Alerts", variable=self.notify_system).grid(
            row=0, column=2, padx=10, pady=5, sticky="w")

        ttk.Button(settings_frame, text="Update Notification Preferences",
                   command=self._update_notification_preferences).grid(
            row=1, column=0, columnspan=3, pady=10)

        self.notification_log_text = scrolledtext.ScrolledText(notifications_frame)
        self.notification_log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.notification_log_text.config(state=tk.DISABLED)

        self._refresh_notifications()

    def _create_demo_devices(self):
        """Create some demo devices for the UI."""
        light_factory = self.device_factories[DeviceType.LIGHT]
        climate_factory = self.device_factories[DeviceType.THERMOSTAT]
        security_factory = self.device_factories[DeviceType.LOCK]

        living_room_light = light_factory.create_device(
            "light-living-1", "Living Room Light",
            {"dimmable": True, "color_adjustable": True}
        )

        bedroom_thermostat = climate_factory.create_device(
            "therm-bed-1", "Bedroom Thermostat",
            {"min_temp": 15.0, "max_temp": 28.0}
        )

        front_door_lock = security_factory.create_device(
            "lock-front-1", "Front Door Lock"
        )

        self.devices[living_room_light.get_id()] = living_room_light
        self.devices[bedroom_thermostat.get_id()] = bedroom_thermostat
        self.devices[front_door_lock.get_id()] = front_door_lock

        living_room_light.set_state({"power": True, "brightness": 80, "color": "warm"})
        bedroom_thermostat.set_state({"power": True, "target_temperature": 22.5, "mode": "heat"})
        front_door_lock.set_state({"locked": True})

        self._refresh_device_list()

    def _show_add_device_dialog(self):
        """Show dialog for adding a new device."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Device")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Device Type:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        device_type_var = tk.StringVar()
        device_type_combo = ttk.Combobox(dialog, textvariable=device_type_var)
        device_type_combo['values'] = [t.name for t in DeviceType]
        device_type_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        device_type_combo.current(0)

        ttk.Label(dialog, text="Device ID:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        device_id_var = tk.StringVar(value=f"device-{int(time.time())}")
        ttk.Entry(dialog, textvariable=device_id_var).grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(dialog, text="Device Name:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        device_name_var = tk.StringVar(value="New Device")
        ttk.Entry(dialog, textvariable=device_name_var).grid(row=2, column=1, padx=10, pady=10, sticky="w")

        props_frame = ttk.LabelFrame(dialog, text="Device Properties")
        props_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        ttk.Label(props_frame, text="Select a device type to see available properties").pack(padx=10, pady=10)

        ttk.Button(dialog, text="Add Device", command=lambda: self._add_new_device(
            device_type_var.get(), device_id_var.get(), device_name_var.get(), dialog
        )).grid(row=4, column=0, columnspan=2, pady=20)

    def _add_new_device(self, device_type_name, device_id, device_name, dialog):
        """Add a new device to the system."""
        try:
            device_type = DeviceType[device_type_name]

            factory = self.device_factories.get(device_type)

            if not factory:
                messagebox.showerror("Error", f"No factory available for device type: {device_type_name}")
                return

            new_device = factory.create_device(device_id, device_name)

            self.devices[device_id] = new_device

            self._refresh_device_list()

            dialog.destroy()

            messagebox.showinfo("Success", f"Device '{device_name}' added successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add device: {str(e)}")

    def _refresh_device_list(self):
        """Refresh the device list in the UI."""
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)

        for device_id, device in self.devices.items():
            device_type_name = device.__class__.__name__
            device_state = str(device.get_state())

            self.device_tree.insert("", tk.END, values=(
                device_id,
                device.get_name(),
                device_type_name,
                device_state[:50] + ("..." if len(device_state) > 50 else "")
            ))

    def _on_device_select(self, event):
        """Handle device selection in the tree."""
        selection = self.device_tree.selection()
        if not selection:
            return

        item = self.device_tree.item(selection[0])
        device_id = item["values"][0]

        device = self.devices.get(device_id)
        if not device:
            return

        for widget in self.device_control_panel.winfo_children():
            widget.destroy()
        self.device_placeholder.pack_forget()

        self.device_control_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        device_name = device.get_name()
        device_type = device.__class__.__name__
        device_state = device.get_state()

        ttk.Label(self.device_control_panel, text=f"{device_name} ({device_id})",
                  font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        ttk.Label(self.device_control_panel, text=f"Type: {device_type}").grid(
            row=1, column=0, columnspan=2, sticky="w", padx=5, pady=2)

        row = 2

        if hasattr(device, 'get_capabilities'):
            capabilities = device.get_capabilities()

            if DeviceCapability.POWER in capabilities:
                row = self._add_power_controls(device, self.device_control_panel, row)

            if DeviceCapability.BRIGHTNESS in capabilities:
                row = self._add_brightness_controls(device, self.device_control_panel, row)

            if DeviceCapability.TEMPERATURE in capabilities:
                row = self._add_temperature_controls(device, self.device_control_panel, row)

            if DeviceCapability.LOCK_UNLOCK in capabilities:
                row = self._add_lock_controls(device, self.device_control_panel, row)

        ttk.Label(self.device_control_panel, text="Current State:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, sticky="w", padx=5, pady=(10, 2))
        row += 1

        for key, value in device_state.items():
            ttk.Label(self.device_control_panel, text=f"{key}: {value}").grid(
                row=row, column=0, columnspan=2, sticky="w", padx=5, pady=2)
            row += 1

    def _add_power_controls(self, device, parent, start_row):
        """Add power controls for a device."""
        ttk.Label(parent, text="Power Control:", font=("Arial", 10, "bold")).grid(
            row=start_row, column=0, sticky="w", padx=5, pady=(10, 2))
        start_row += 1

        current_state = device.get_state().get("power", False)
        power_var = tk.BooleanVar(value=current_state)

        ttk.Checkbutton(parent, text="Power ON/OFF", variable=power_var,
                        command=lambda: self._update_device_state(device, {"power": power_var.get()})).grid(
            row=start_row, column=0, padx=5, pady=2, sticky="w")

        return start_row + 1

    def _add_brightness_controls(self, device, parent, start_row):
        """Add brightness controls for a device."""
        ttk.Label(parent, text="Brightness Control:", font=("Arial", 10, "bold")).grid(
            row=start_row, column=0, sticky="w", padx=5, pady=(10, 2))
        start_row += 1

        current_brightness = device.get_state().get("brightness", 50)
        brightness_var = tk.IntVar(value=current_brightness)

        brightness_scale = ttk.Scale(parent, from_=0, to=100, orient=tk.HORIZONTAL,
                                     variable=brightness_var, length=200)
        brightness_scale.grid(row=start_row, column=0, padx=5, pady=2, sticky="w")

        brightness_label = ttk.Label(parent, text=f"{current_brightness}%")
        brightness_label.grid(row=start_row, column=1, padx=5, pady=2, sticky="w")

        def update_brightness(*args):
            value = int(brightness_var.get())
            brightness_label.config(text=f"{value}%")
            self._update_device_state(device, {"brightness": value})

        brightness_var.trace_add("write", update_brightness)

        return start_row + 1

    def _add_temperature_controls(self, device, parent, start_row):
        """Add temperature controls for a device."""
        ttk.Label(parent, text="Temperature Control:", font=("Arial", 10, "bold")).grid(
            row=start_row, column=0, sticky="w", padx=5, pady=(10, 2))
        start_row += 1

        current_temp = device.get_state().get("target_temperature", 22.0)
        temp_var = tk.DoubleVar(value=current_temp)

        temp_scale = ttk.Scale(parent, from_=15, to=30, orient=tk.HORIZONTAL,
                               variable=temp_var, length=200)
        temp_scale.grid(row=start_row, column=0, padx=5, pady=2, sticky="w")

        temp_label = ttk.Label(parent, text=f"{current_temp}°C")
        temp_label.grid(row=start_row, column=1, padx=5, pady=2, sticky="w")

        def update_temperature(*args):
            value = round(temp_var.get(), 1)
            temp_label.config(text=f"{value}°C")
            self._update_device_state(device, {"target_temperature": value})

        temp_var.trace_add("write", update_temperature)

        ttk.Label(parent, text="Mode:").grid(row=start_row + 1, column=0, padx=5, pady=2, sticky="w")

        mode_var = tk.StringVar(value=device.get_state().get("mode", "auto"))
        modes = ttk.Combobox(parent, textvariable=mode_var, values=["off", "heat", "cool", "auto"])
        modes.grid(row=start_row + 1, column=1, padx=5, pady=2, sticky="w")

        def update_mode(*args):
            self._update_device_state(device, {"mode": mode_var.get()})

        mode_var.trace_add("write", update_mode)

        return start_row + 2

    def _add_lock_controls(self, device, parent, start_row):
        """Add lock controls for a device."""
        ttk.Label(parent, text="Lock Control:", font=("Arial", 10, "bold")).grid(
            row=start_row, column=0, sticky="w", padx=5, pady=(10, 2))
        start_row += 1

        current_locked = device.get_state().get("locked", True)
        lock_var = tk.BooleanVar(value=current_locked)

        lock_frame = ttk.Frame(parent)
        lock_frame.grid(row=start_row, column=0, columnspan=2, sticky="w", padx=5, pady=2)

        ttk.Button(lock_frame, text="Lock", command=lambda: self._update_device_state(
            device, {"locked": True, "last_user": "GUI User"})).pack(side=tk.LEFT, padx=5)

        ttk.Button(lock_frame, text="Unlock", command=lambda: self._update_device_state(
            device, {"locked": False, "last_user": "GUI User"})).pack(side=tk.LEFT, padx=5)

        return start_row + 1

    def _update_device_state(self, device, state_update):
        """Update a device's state."""
        try:
            device.set_state(state_update)

            self._refresh_device_list()

            self._on_device_select(None)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update device: {str(e)}")

    def _generate_test_event(self):
        """Generate a test event for demonstration."""
        event = Event(
            event_type=EventType.SYSTEM_ALERT,
            source="system",
            data={
                "message": "This is a test alert triggered from the GUI",
                "severity": "info"
            }
        )
        self.event_manager.notify(event)
        messagebox.showinfo("Event Generated", "Test event has been generated and sent to all subscribers.")

    def _generate_simulated_event(self):
        """Generate a simulated event from user input."""
        try:
            event_type = EventType[self.sim_event_type.get()]

            import json
            data = json.loads(self.sim_data.get()) if self.sim_data.get() else {}

            event = Event(
                event_type=event_type,
                source=self.sim_source.get(),
                data=data
            )
            self.event_manager.notify(event)

            messagebox.showinfo("Success", "Event generated successfully!")

            self._refresh_event_log()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate event: {str(e)}")

    def _refresh_event_log(self, *args):
        """Refresh the event log display."""
        for subscriber in self._find_subscribers_by_type(LoggingEventSubscriber):
            log_entries = subscriber.get_log()

            selected_type = self.event_type_var.get()
            if selected_type != "All":
                log_entries = [entry for entry in log_entries
                               if entry["type"] == f"EventType.{selected_type}"]

            self.event_log_text.config(state=tk.NORMAL)
            self.event_log_text.delete(1.0, tk.END)

            for entry in log_entries:
                time_str = entry.get('timestamp', 'N/A')
                event_type = entry.get('type', 'Unknown')
                source = entry.get('source', 'Unknown')
                data = entry.get('data', {})

                log_line = f"[{time_str}] {event_type} from {source}\n"
                if data:
                    log_line += f"    Data: {data}\n"
                log_line += "-" * 50 + "\n"

                self.event_log_text.insert(tk.END, log_line)

            self.event_log_text.config(state=tk.DISABLED)

            self._update_dashboard_events(log_entries[-5:] if log_entries else [])

    def _update_dashboard_events(self, recent_events):
        """Update the recent events display on the dashboard."""
        self.recent_events_text.config(state=tk.NORMAL)
        self.recent_events_text.delete(1.0, tk.END)

        for entry in reversed(recent_events):  # Show newest first
            time_str = entry.get('timestamp', 'N/A')
            event_type = entry.get('type', 'Unknown').replace('EventType.', '')
            source = entry.get('source', 'Unknown')

            log_line = f"[{time_str[-8:]}] {event_type} from {source}\n"
            self.recent_events_text.insert(tk.END, log_line)

        self.recent_events_text.config(state=tk.DISABLED)

    def _refresh_notifications(self):
        """Refresh the notifications display."""
        for subscriber in self._find_subscribers_by_type(NotificationService):
            notifications = subscriber.get_notification_history()

            self.notification_log_text.config(state=tk.NORMAL)
            self.notification_log_text.delete(1.0, tk.END)

            for notification in notifications:
                time_str = notification.get('timestamp', 'N/A')
                message = notification.get('message', 'No message')
                source = notification.get('source', 'Unknown')

                log_line = f"[{time_str}] {message}\n"
                log_line += f"    Source: {source}\n"
                log_line += "-" * 50 + "\n"

                self.notification_log_text.insert(tk.END, log_line)

            self.notification_log_text.config(state=tk.DISABLED)

    def _find_subscribers_by_type(self, subscriber_type):
        """Helper to find subscribers of a specific type."""
        result = []

        for event_type in EventType:
            subscribers_set = getattr(self.event_manager, '_subscribers', {}).get(event_type, set())
            for subscriber in subscribers_set:
                if isinstance(subscriber, subscriber_type) and subscriber not in result:
                    result.append(subscriber)

        return result

    def _clear_event_log(self):
        """Clear the event log."""
        for subscriber in self._find_subscribers_by_type(LoggingEventSubscriber):
            subscriber.clear_log()

        self._refresh_event_log()
        messagebox.showinfo("Success", "Event log cleared.")

    def _clear_notifications(self):
        """Clear the notifications history."""
        for subscriber in self._find_subscribers_by_type(NotificationService):
            if hasattr(subscriber, '_notification_history'):
                subscriber._notification_history = []

        self._refresh_notifications()
        messagebox.showinfo("Success", "Notification history cleared.")

    def _update_notification_preferences(self):
        """Update notification preferences."""
        event_types = []

        if self.notify_motion.get():
            event_types.append(EventType.MOTION_DETECTED)

        if self.notify_door.get():
            event_types.append(EventType.DOOR_OPENED)
            event_types.append(EventType.DOOR_CLOSED)

        if self.notify_system.get():
            event_types.append(EventType.SYSTEM_ALERT)

        for subscriber in self._find_subscribers_by_type(NotificationService):
            if hasattr(subscriber, '_event_types'):
                subscriber._event_types = event_types

        messagebox.showinfo("Success", "Notification preferences updated.")

    def _update_logs_periodically(self):
        """Update logs periodically in a separate thread."""
        while self.log_update_active:
            try:
                self._refresh_event_log()
                self._refresh_notifications()
            except Exception:
                pass

            time.sleep(5)

    def on_closing(self):
        """Handle window closing event."""
        self.log_update_active = False
        if self.log_thread:
            self.log_thread.join(timeout=0.5)
        self.root.destroy()


def launch_gui(event_manager=None):
    """Launch the Smart Home GUI."""
    if event_manager is None:
        event_manager = EventManager()

        event_manager.subscribe(LoggingEventSubscriber())
        event_manager.subscribe(NotificationService())

    root = tk.Tk()

    gui = SmartHomeGUI(root, event_manager)

    root.protocol("WM_DELETE_WINDOW", gui.on_closing)

    root.mainloop()

    return gui


if __name__ == "__main__":
    launch_gui()
