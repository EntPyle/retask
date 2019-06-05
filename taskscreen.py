from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from taskfunctions import TaskCollection, Task


class TaskScreen(Screen):

    # TODO check for hidden recurring tasks on load, status flag, schedule flag switch

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_collection = TaskCollection()
        print('creating task screen')
        self.archive = TaskCollection()

    # self.register_event_type('on_quit_app')

    def refill_task_collection(self, task_collection):
        # use something like this to switch between archive and normal
        print('refilling task collection')
        for task in task_collection.tasks:
            print('adding task')
            print(task, task.text, task.group, task.frequency)
            taskwidget = self.add_taskwidget(task, task_out=True)

    def remove_task(self, instance):
        self.archive.new_task()
        self.task_collection.remove_task(instance.task)
        self.ids['task_container'].ids['container'].remove_widget(instance)

    def new_task(self):
        '''Wrapper for task collection fx new_task'''
        self.add_taskwidget(self.task_collection.new_task())

    def add_taskwidget(self, task, task_out=False):
        taskwidget = TaskWidget()  # create task widget
        taskwidget.task = task  # bind passed task object to widget
        taskwidget.bind(on_delete=self.remove_task)
        taskwidget.bind(on_task_changed=self.modify_task)
        self.ids['task_container'].ids['container'].add_widget(taskwidget)
        if task_out:
            return taskwidget

    def modify_task(self, instance):
        '''Wrapper for task collection fx modify_task'''
        self.task_collection.modify_task(instance.task)

class TopBar(BoxLayout):
    # contains app header

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_add_taskwidget')

    def on_add_taskwidget(self):
        pass

class TaskWidget(BoxLayout):
    '''
    Change widget height and size_hint_y to 0 to hide. Be sure to save original settings

    '''
    edit = BooleanProperty(None)
    task = ObjectProperty(None)

    # stored_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_delete')
        # self.register_event_type('on_task_changed')
        self.register_event_type('on_complete')
        self.register_event_type('on_edit_group')
        self.edit_wid_list = [
            self.ids['task_btm'],
            self.ids['freq_spin'],
            self.ids['group_spin'],
            self.ids['but_add_g'],
            self.ids['but_del']
        ]
        self.norm_wid_list = [
            self.ids['lbl_freq'],
            self.ids['lbl_group'],
            self.ids['btn_complete']
        ]

    def on_task(self, instance, value):
        '''Used to link widget parameters to the task object'''
        print('on task fired')
        print(self, instance, value)
        self.ids['task_input'].text = self.task.text
        self.ids['lbl_freq'].text = self.task.frequency
        self.ids['lbl_group'].text = self.task.group
        self.ids['freq_spin'].text = self.task.frequency
        self.ids['group_spin'].text = self.task.group
        if self.ids['task_input'].text == '':
            # This is a new task
            self.toggle_widget(*self.edit_wid_list)
            self.edit = True
        else:
            # This is a reloaded task
            self.toggle_widget(*self.norm_wid_list)
            self.edit = False

    def on_edit(self, instance, value):
        print('on_edit fired')
        print('Edit: ', value)
        if value:
            # edit mode
            self.ids['task_input'].disabled = False
        else:
            # display mode
            self.task.text = self.ids['task_input'].text
            self.task.frequency = self.ids['lbl_freq'].text = self.ids['freq_spin'].text
            self.task.group = self.ids['lbl_group'].text = self.ids['group_spin'].text
            self.ids['task_input'].disabled = True
            # self.dispatch('on_task_changed')
        self.toggle_widget(*self.edit_wid_list)
        self.toggle_widget(*self.norm_wid_list)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) is True and self.edit is False:
            # if touch is inside task widget
            if self.ids['btn_complete'].collide_point(*touch.pos) is True:
                # if mark complete is touched
                return super(TaskWidget, self).on_touch_down(touch)
            else:
                self.edit = not self.edit  # enters edit mode
                # CHECK need to have all other task widgets leave edit mode
                # return True
        elif self.collide_point(*touch.pos) is False and self.edit is True:
            # if touch is outside and task widget is in edit mode
            self.edit = not self.edit  # exits edit mode
            # return True
            return super(TaskWidget, self).on_touch_down(touch)
        else:  # super return allows the touch to carry on
            return super(TaskWidget, self).on_touch_down(touch)

    def on_delete(self):
        # move to archive
        return self

    # def on_task_changed(self):
    #     return self

    def on_complete(self):
        # add in temp archive to undo and/or schedule revive
        self.toggle_widget(self)
        return self

    def on_edit_group(self):
        # create popup to add group to task class
        popup = AddGroupPopup()
        popup.bind(on_add_group=self.refresh_groups)
        popup.open()
        # Task.add_group(value)
        return self

    def refresh_groups(self, popup):
        group_name = popup.ids['grp_input'].text
        Task.add_group(group_name)
        # self.stored_data.put('groups', names = Task.group_list)
        self.ids['group_spin'].values = Task.group_list

    def toggle_widget(self, *args):
        '''Toggles view state of the passed widgets'''
        for wid in args:
            # print('Id: ',wid)
            if hasattr(wid, 'saved_attrs'):
                wid.height, wid.size_hint_y, wid.opacity = wid.saved_attrs
                del wid.saved_attrs
            else:
                wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity
                wid.height, wid.size_hint_y, wid.opacity = 0, None, 0

class AddGroupPopup(Popup):
    # Properties
    # Functions
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_add_group')

    def on_open(self):
        pass

    def on_add_group(self):
        pass