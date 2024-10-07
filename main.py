from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.popup import Popup  # Import Popup for alarm
from kivy.core.audio import SoundLoader  # Import SoundLoader for alarm sound
from kivy.properties import ObjectProperty

class PomodoroApp(App):
    def build(self):
        self.default_work_time = 25 * 60  # Default: 25 minutes in seconds
        self.default_break_time = 5 * 60  # Default: 5 minutes in seconds
        self.current_time = self.default_work_time
        self.is_work_time = True
        self.timer_running = False
        self.completed_cycles = 0  # To count Pomodoro cycles

        # Load alarm sound
        self.alarm_sound = SoundLoader.load('alarm.wav')  # Ensure you have an 'alarm.wav' file in the app directory
        if self.alarm_sound:
            self.alarm_sound.loop = True  # Play the sound 
        else:
            print("Alarm sound file not found!")

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header Layout (contains Timer and Cycle Counter)
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)

        # Timer Label
        self.timer_label = Label(text=self.format_time(self.current_time), font_size=48)
        header_layout.add_widget(self.timer_label)

        # Cycle Counter in the Upper Right
        self.cycle_counter_label = Label(text=f"Cycles: {self.completed_cycles}", size_hint_x=None, width=150, halign='right', valign='middle')
        header_layout.add_widget(self.cycle_counter_label)
        layout.add_widget(header_layout)

        # Start/Stop Button
        self.start_stop_button = Button(text="Start", on_press=self.toggle_timer)
        layout.add_widget(self.start_stop_button)

        # Timer Customization
        customization_layout = BoxLayout(size_hint_y=None, height=40)

        self.work_time_input = TextInput(hint_text="Work minutes", multiline=False, input_filter='int')
        self.break_time_input = TextInput(hint_text="Break minutes", multiline=False, input_filter='int')
        set_timer_button = Button(text="Set Timer", on_press=self.set_custom_times)

        customization_layout.add_widget(self.work_time_input)
        customization_layout.add_widget(self.break_time_input)
        customization_layout.add_widget(set_timer_button)
        layout.add_widget(customization_layout)

        # Task Input Field
        task_input_layout = BoxLayout(size_hint_y=None, height=40)
        self.task_input = TextInput(hint_text="Add a task", multiline=False)
        add_task_button = Button(text="Add", on_press=self.add_task)
        task_input_layout.add_widget(self.task_input)
        task_input_layout.add_widget(add_task_button)
        layout.add_widget(task_input_layout)

        # Scrollable Task List
        self.scroll_view = ScrollView(size_hint=(1, None), height=200)
        self.task_list_layout = GridLayout(cols=1, size_hint_y=None)
        self.task_list_layout.bind(minimum_height=self.task_list_layout.setter('height'))
        self.scroll_view.add_widget(self.task_list_layout)
        layout.add_widget(self.scroll_view)

        return layout

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{int(minutes):02}:{int(seconds):02}"

    def toggle_timer(self, instance):
        if self.timer_running:
            Clock.unschedule(self.update_timer)
            self.timer_running = False
            self.start_stop_button.text = "Start"
        else:
            Clock.schedule_interval(self.update_timer, 1)
            self.timer_running = True
            self.start_stop_button.text = "Pause"

    def update_timer(self, dt):
        if self.current_time > 0:
            self.current_time -= 1
        else:
            # Timer has reached zero, trigger alarm
            self.toggle_timer(None)  # Stop the timer
            self.show_alarm()

        self.timer_label.text = self.format_time(self.current_time)

    def set_custom_times(self, instance):
        # Set custom work and break times from user input
        try:
            work_minutes = int(self.work_time_input.text)
            break_minutes = int(self.break_time_input.text)
            if work_minutes > 0:
                self.default_work_time = work_minutes * 60
            if break_minutes > 0:
                self.default_break_time = break_minutes * 60
            self.current_time = self.default_work_time  # Reset timer to the new work time
            self.timer_label.text = self.format_time(self.current_time)
        except ValueError:
            # Handle non-integer input
            pass

    def add_task(self, instance):
        task_text = self.task_input.text
        if task_text:
            task_layout = BoxLayout(size_hint_y=None, height=40)

            # CheckBox to mark task as done
            checkbox = CheckBox()
            checkbox.bind(active=self.on_checkbox_active)

            # Label for the task text
            task_label = Label(text=task_text, markup=True)  # Enable markup for strike-through

            # Add to the layout
            task_layout.add_widget(checkbox)
            task_layout.add_widget(task_label)

            # Add the task layout to the task list
            self.task_list_layout.add_widget(task_layout)
            
            # Clear the input field
            self.task_input.text = ''

    def on_checkbox_active(self, checkbox, value):
        # If task is checked (completed)
        task_label = checkbox.parent.children[0]  # Assuming Label is the first child
        if value:
            # Strike-through effect using markup
            task_label.text = f"[s]{task_label.text}[/s]"
            task_label.color = (0.5, 0.5, 0.5, 1)  # Grays out the task label
        else:
            # Reverts the task label when unchecked
            task_label.text = task_label.text.replace("[s]", "").replace("[/s]", "")
            task_label.color = (1, 1, 1, 1)  # Restore normal color

    def show_alarm(self):
        # Play the alarm sound
        if self.alarm_sound:
            self.alarm_sound.play()

        # Create a popup to notify the user
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Label(text="Time's up!", font_size=24)
        dismiss_button = Button(text="Dismiss", size_hint=(1, 0.3))
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(dismiss_button)

        self.alarm_popup = Popup(title="Alarm",
                                 content=popup_layout,
                                 size_hint=(None, None),
                                 size=(300, 200),
                                 auto_dismiss=False)  # Prevent dismissing by clicking outside

        dismiss_button.bind(on_press=self.dismiss_alarm)
        self.alarm_popup.open()

    def dismiss_alarm(self, instance):
        # Stop the alarm sound
        if self.alarm_sound:
            self.alarm_sound.stop()

        self.alarm_popup.dismiss()

        # Switch to the next phase
        self.is_work_time = not self.is_work_time
        self.current_time = self.default_work_time if self.is_work_time else self.default_break_time
        if self.is_work_time:
            self.completed_cycles += 1
            self.cycle_counter_label.text = f"Cycles: {self.completed_cycles}"
        self.timer_label.text = self.format_time(self.current_time)

        # Optionally, automatically start the next timer
        # Uncomment the following lines to auto-start
        # Clock.schedule_interval(self.update_timer, 1)
        # self.timer_running = True
        # self.start_stop_button.text = "Pause"

if __name__ == "__main__":
    PomodoroApp().run()
