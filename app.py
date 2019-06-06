from kivy.config import Config

Config.set('graphics', 'window_state', 'maximized')
Config.set('kivy', 'exit_on_escape', '0')
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SwapTransition
from taskscreen import TaskScreen
from ruamel.yaml import YAML
from pathlib import Path

'''
The App implementation
'''

# Builder.load_file('todone.kv')

class todoneApp(App):

    def build(self):
        self.icon = 'data/icon/todone_icon.png'  # Don't know why icon isn't set :(
        self.title = 'ToDone'
        self.init()
        return self.screenmanager

    def init(self):
        self.store_file_path = Path('task_store.yml')
        self.screenmanager = ScreenManager(transition=SwapTransition())
        self.taskscreen = TaskScreen(name='screen-task')
        # self.taskscreen.bind(on_quit_app=self.quit)
        self.screenmanager.add_widget(self.taskscreen)
        self.load_data(self.store_file_path)
        self.screenmanager.current = 'screen-task'

    def store_data(self, store_file_path, task_collection):
        YAML().dump(task_collection, store_file_path)

    def load_data(self, store_file_path):
        if store_file_path.is_file():
            task_c = YAML().load(store_file_path)
            self.taskscreen.refill_task_collection(task_c)

    def on_pause(self):
        return True

    def on_stop(self):
        # print('Stopped')
        # TODO clear archive
        # delete current store/overwrite data
        self.store_data(self.store_file_path, self.taskscreen.task_collection)

    # def toggle_widget(self, *args):
    #     # print('Args: ',args)
    #     for wid in args:
    #         # print('Id: ',wid)
    #         if hasattr(wid, 'saved_attrs'):
    #             wid.height, wid.size_hint_y, wid.opacity = wid.saved_attrs
    #             del wid.saved_attrs
    #         else:
    #             wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity
    #             wid.height, wid.size_hint_y, wid.opacity = 0, None, 0


if __name__ == '__main__':
    todoneApp().run()
