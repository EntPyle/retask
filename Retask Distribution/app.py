from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'window_state', 'maximized')
Config.set('kivy', 'exit_on_escape', '0')

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.settings import SettingsWithTabbedPanel
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SwapTransition
from kivy.properties import StringProperty
from taskscreen import TaskScreen
from ruamel.yaml import YAML
from pathlib import Path

'''
The App implementation
'''

Builder.load_file('baseclasses.kv')
Builder.load_file('groups.kv')
Builder.load_file('topbar.kv')
Builder.load_file('taskwidget.kv')
Builder.load_file('retask.kv')


class retaskApp(App):
    font_size = StringProperty('')
    layout = StringProperty('')

    def build(self):
        self.icon = 'data/icon/todone_icon.png'  # Don't know why icon isn't set :(
        self.title = 'Retask'
        ### Settings
        self.settings_cls = SettingsWithTabbedPanel
        self.font_size = str(self.config.get('My Settings', 'font_size'))
        self.layout = str(self.config.get('My Settings', 'layout_setting'))
        self.store_file_path = Path('task_store.yml')
        #########################
        self.screenmanager = ScreenManager(transition=SwapTransition())
        self.taskscreen = TaskScreen(name='screen-task')
        # self.taskscreen.bind(on_quit_app=self.quit)
        self.screenmanager.add_widget(self.taskscreen)
        self.load_data(self.store_file_path)
        Window.bind(on_keyboard=self.on_keyboard)
        Window.bind(on_resize=self.taskscreen.set_layout)
        self.use_kivy_settings = False
        return self.screenmanager

    def build_config(self, config):
        """
        Set the default values for the configs sections.
        """
        config.setdefaults('My Settings', {'font_size': 18,
                                           'layout_setting': 'Frequency in Columns'})

    def build_settings(self, settings):
        """
        Add our custom section to the default configuration object.
        """
        # We use the string defined above for our JSON, but it could also be
        # loaded from a file as follows:
        settings.add_json_panel('My Settings', self.config, filename='json_settings.json')

    def on_config_change(self, config, section, key, value):
        """
        Respond to changes in the configuration.
        """
        print(config, section, key, value, type(value))
        if section == "My Settings":
            if key == "font_size":
                print('font changed')
                self.font_size = str(value)
            elif key == "layout_setting":
                self.layout = str(value)
                self.taskscreen.set_layout()

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        # print(codepoint, modifier)
        if 'ctrl' in modifier and codepoint == 'q':
            self.stop()
        if 'ctrl' in modifier and codepoint == 'g':
            self.taskscreen.manage_groups_popup()
        if 'ctrl' in modifier and codepoint == 'n':
            self.taskscreen.new_task()
        if 'ctrl' in modifier and codepoint == 'z':
            self.taskscreen.recover_task()
        if 'ctrl' in modifier and codepoint == 'f':
            self.taskscreen.ids['top_bar'].ids['search_box'].ids['search_input'].focus = True

    def store_data(self, clear_archive=True):
        if clear_archive:
            self.taskscreen.task_collection.archived_tasks.clear()
        YAML().dump(self.taskscreen.task_collection, self.store_file_path)

    def load_data(self, store_file_path):
        if store_file_path.is_file():
            task_c = YAML().load(store_file_path)
            self.taskscreen.refill_task_collection(task_c)

    def on_pause(self):
        return True

    def on_stop(self):
        # print('Stopped')
        # delete current store/overwrite data
        self.taskscreen.ids['top_bar'].ids['toggle_complete'].state = 'normal'
        self.store_data()

if __name__ == '__main__':
    retaskApp().run()
