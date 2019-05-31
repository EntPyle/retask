from kivy.app import App
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from taskfunctions import TaskCollection, Task


class TaskScreen(Screen):

    # check for hidden recurring tasks

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_collection = TaskCollection()
        print('creating task screen')
        self.archive = TaskCollection()

    # self.register_event_type('on_quit_app')

    def remove_task(self, instance):
        self.archive.new_task()
        self.task_collection.remove_task(instance.task)
        self.ids['task_container'].ids['container'].remove_widget(instance)

    def set_task_collection(self, task_collection):
        # use something like this to switch between archive and normal
        self.task_collection = task_collection
        print('setting task collection')
        for task in self.task_collection.tasks:
            print('adding task')
            self.add_taskwidget(task)

    def new_task(self):
        self.add_taskwidget(self.task_collection.new_task())

    def add_taskwidget(self, task):
        print('adding task widget')
        taskwidget = TaskWidget()
        print('Initialized Task Widget')
        taskwidget.task = task
        print('bound task to task widget')
        taskwidget.bind(on_delete=self.remove_task)
        taskwidget.bind(on_task_changed=self.modify_task)
        self.ids['task_container'].ids['container'].add_widget(taskwidget)
        print('widget added')

    def modify_task(self, instance):
        self.task_collection.modify_task(instance.task)


# def modify_groups(self):
# 	popup = GroupWidget()

# def pre_quit_exec(self):
# 	for child in self.ids['task_container'].ids['container'].children:
# 		child.edit = False
# 	self.dispatch('on_quit_app')

# def on_quit_app(self):
# 	pass


class TopBar(BoxLayout):
    # contains app header

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_add_taskwidget')
        # self.register_event_type('on_quit_pressed')

    def on_add_taskwidget(self):
        pass

    # def on_quit_pressed(self):
    #     pass


class TaskWidget(BoxLayout):
    '''
    Change widget height and size_hint_y to 0 to hide. Be sure to save original settings

    '''
    edit = BooleanProperty(True)
    task = ObjectProperty(None)

    # stored_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        print('Initializing a task widget')
        self.register_event_type('on_delete')
        self.register_event_type('on_task_changed')
        self.register_event_type('on_complete')
        self.register_event_type('on_edit_group')
        print('events registered')
        print(kwargs)
        super().__init__(**kwargs)
        print('super init')

    # self.stored_data = JsonStore('data.json')

    def toggle_edit(self):
        self.edit = not self.edit
        App.get_running_app().toggle_widget(
            self.ids['task_btm'],
            self.ids['lbl_freq'],
            self.ids['lbl_group'],
            self.ids['btn_complete'])

    def on_edit(self, instance, value):
        if value:
            self.ids['task_input'].disabled = False
        else:
            self.task.text = self.ids['task_input'].text
            self.task.frequency = self.ids['lbl_freq'].text = self.ids['freq_spin'].text
            self.task.group = self.ids['lbl_group'].text = self.ids['group_spin'].text
            self.ids['task_input'].disabled = True
            self.dispatch('on_task_changed')

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) is True and self.edit is False:
            if self.ids['btn_complete'].collide_point(*touch.pos) is True:
                return super(TaskWidget, self).on_touch_down(touch)
            else:
                self.toggle_edit()
                return True
        elif self.collide_point(*touch.pos) is False and self.edit is True:
            self.toggle_edit()
            return True
        else:  # super return allows the touch to carry on
            return super(TaskWidget, self).on_touch_down(touch)

    def on_delete(self):
        return self

    def on_complete(self):
        # add in temp archive to undo.
        App.get_running_app().toggle_widget(self)
        return self

    def on_task_changed(self):
        return self

    def on_edit_group(self):
        # create popup to add group to task class
        popup = AddGroupPopup()
        popup.bind(on_add_group=self.refresh_groups)
        popup.open()
        # Task.add_group(value)
        return self

    def on_task(self, instance, value):
        self.ids['task_input'].text = self.task.text
        self.ids['lbl_freq'].text = self.task.frequency
        self.ids['lbl_group'].text = self.task.group
        self.ids['freq_spin'].text = self.task.frequency
        self.ids['group_spin'].text = self.task.group
        if self.ids['task_input'].text == '':
            self.edit = True
            App.get_running_app().toggle_widget(
                self.ids['lbl_freq'],
                self.ids['lbl_group'],
                self.ids['btn_complete'])
        else:
            self.edit = False

    def refresh_groups(self, popup):
        group_name = popup.ids['grp_input'].text
        Task.add_group(group_name)
        # self.stored_data.put('groups', names = Task.group_list)
        self.ids['group_spin'].values = Task.group_list


class AddGroupPopup(Popup):
    # Properties
    # Functions
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_event_type('on_add_group')

    def on_open(self):
        pass

    def on_add_group(self):
        pass
