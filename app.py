from kivy.config import Config

Config.set('graphics', 'window_state', 'maximized')
Config.set('kivy', 'exit_on_escape', '0')
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SwapTransition
from taskscreen import TaskScreen
import threading

try:
    import cPickle as pickle
except ImportError:
    import pickle
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
        self.store_file_path = 'task_store'
        self.screenmanager = ScreenManager(transition=SwapTransition())
        self.taskscreen = TaskScreen(name='screen-task')
        # self.taskscreen.bind(on_quit_app=self.quit)
        self.screenmanager.add_widget(self.taskscreen)
        self.start_load_thread()
        self.screenmanager.current = 'screen-task'

    def store_data(self, store_file_path, task_collection):
        self.screenmanager.clear_widgets()
        data = task_collection.encode(encoding='utf-8', errors='strict')
        print(data)
        with open(store_file_path, 'wb') as f:
            f.write(data)
        self.stop()

    def pickle_data(self, obj, store_name):
        # can save any object passed
        with open(store_name, 'wb') as store:  # Overwrites existing file
            pickle.dump(obj, store, -1)

    def load_data(self, store_file_path):
        def unpickle_data(store_name):
            with open(store_name, 'rb') as store:
                while True:
                    try:
                        yield pickle.load(store)
                    except EOFError:
                        break

        # with open(self.store_file_path, 'ab+') as f:
        #     f.seek(0)
        #     stored_data = f.read()
        #     if stored_data == b'':
        #         self.screenmanager.current = 'screen-task'
        #     else:
        #         self.start_load_thread(stored_data)          
        for task_collect in unpickle_data(store_file_path):
            print('Testing', task_collect)
            print('Tasks', task_collect.tasks)
            for atask in task_collect.tasks:
                print('Task text:', atask.text)
                self.taskscreen.add_taskwidget(atask)
            # add to collection

    def start_load_thread(self):
        t = threading.Thread(target=self.load_data, args=(self.store_file_path,))
        t.daemon = True
        t.start()

    def start_store_thread(self, store_file_path, task_collection):
        t = threading.Thread(target=self.pickle_data, args=(
            task_collection, store_file_path))
        t.daemon = True
        t.start()

    # def quit(self, *args):
    #     task_collection = self.taskscreen.task_collection
    #     self.start_store_thread(
    #         self.store_file_path, task_collection)

    def on_pause(self):
        return True

    def on_stop(self):
        task_collection = self.taskscreen.task_collection
        self.start_store_thread(
            self.store_file_path, task_collection)

    def toggle_widget(self, *args):
        # print('Args: ',args)
        for wid in args:
            # print('Id: ',wid)
            if hasattr(wid, 'saved_attrs'):
                wid.height, wid.size_hint_y, wid.opacity = wid.saved_attrs
                del wid.saved_attrs
            else:
                wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity
                wid.height, wid.size_hint_y, wid.opacity = 0, None, 0


if __name__ == '__main__':
    todoneApp().run()
