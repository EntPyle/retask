from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from taskfunctions import TaskCollection


# Todo switch to recycle view instead of just adding tons of widgets
# Todo add in ability to show all tasks including hidden tasks (just append the scheduled tasks to the tasks list)
# Todo add in ability to show tasks for next days, weeks, or months tasks optional
class TaskScreen(Screen):

    # TODO add in keybinding ctrl+Z to call task_collection.recover_task() when no tasks are in edit mode

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_collection = TaskCollection()
        # self.scheduled_tasks = TaskCollection()
        # self.archive = TaskCollection()

    def refill_task_collection(self, task_collection):
        # makes stored task_c the task_c used in TaskScreen
        self.task_collection = task_collection
        self.task_collection.check_scheduled_tasks()
        for task in self.task_collection.tasks:
            taskwidget = self.add_taskwidget(task, task_out=False)

    def archive_task(self, instance):
        print(self.task_collection.tasks, instance.task.text)
        self.task_collection.archive_task(instance.task)
        self.ids['task_container'].ids['container'].remove_widget(instance)
        self.ids['task_container'].ids['container'].do_layout()

    def recover_task(self):
        if len(self.task_collection.archived_tasks) > 0:
            task = self.task_collection.recover_task(out_task=True)
            self.add_taskwidget(task)

    def new_task(self):
        '''Wrapper for task collection fx new_task'''
        self.add_taskwidget(self.task_collection.new_task())

    def add_taskwidget(self, task, task_out=False):
        taskwidget = TaskWidget()  # create task widget
        taskwidget.task = task  # bind passed task object to widget
        taskwidget.bind(on_delete=self.archive_task)
        taskwidget.bind(on_task_changed=self.modify_task)
        taskwidget.bind(on_refresh_groups=self.refresh_groups)
        taskwidget.bind(on_complete=self.schedule_task)
        self.ids['task_container'].ids['container'].add_widget(taskwidget)
        if task_out:
            return taskwidget

    def modify_task(self, instance):
        '''Wrapper for task collection fx modify_task'''
        self.task_collection.modify_task(instance.task)

    def schedule_task(self, instance):
        '''Wrapper for task collection fx schedule_task'''
        self.task_collection.schedule_task(instance.task)
        self.ids['task_container'].ids['container'].remove_widget(instance)
        self.ids['task_container'].ids['container'].do_layout()

    def manage_groups_popup(self):
        # create popup to add group to task class
        popup = ManageGroupPopup()
        popup.bind(on_dismiss=self.refresh_groups)
        popup.open()
        return self

    def refresh_groups(self, popup):
        for task_wid in self.ids['task_container'].ids['container'].children:
            task_wid.ids['group_spin'].values = task_wid.group_list = self.task_collection.group_list
            task_wid.ids['lbl_group'].text = task_wid.ids['group_spin'].text = task_wid.task.group

class TopBar(BoxLayout):
    # contains app header

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_add_taskwidget')
        self.register_event_type('on_manage_groups')

    def on_add_taskwidget(self):
        pass

    def on_manage_groups(self):
        pass


class ManageGroupPopup(Popup):
    # Properties
    group_list = ListProperty([])

    # Functions
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_new_group')
        self.group_list = App.get_running_app().screenmanager.get_screen('screen-task').task_collection.group_list

    def on_open(self):
        for group in self.group_list:
            self.add_groupwidget(group)
        self.ids['new_grp_input'].focus = True

    def on_dismiss(self):
        return self

    def on_new_group(self):
        group = self.ids['new_grp_input'].text
        if group == '':
            pass
        else:
            try:
                App.get_running_app().screenmanager.get_screen('screen-task').task_collection.add_group(group)
            except ValueError:
                # group already exists do nothing
                pass
            else:
                self.add_groupwidget(group)
            finally:
                self.ids['new_grp_input'].text = ''

    def rename_group(self, instance):
        App.get_running_app().screenmanager.get_screen('screen-task').task_collection.rename_group(instance.old_group,
                                                                                                   instance.group)

    def delete_group(self, instance):
        App.get_running_app().screenmanager.get_screen('screen-task').task_collection.delete_group(instance.group)
        self.ids['container'].remove_widget(instance)

    def add_groupwidget(self, group):
        group_w = GroupWidget(group)  # create group widget
        group_w.bind(on_delete_group=self.delete_group)
        group_w.bind(on_rename_group=self.rename_group)
        if group == 'None':
            group_w.ids['grp_input'].disabled = True
        self.ids['container'].add_widget(group_w)


class GroupWidget(BoxLayout):
    group = StringProperty('')
    old_group = StringProperty('')

    def __init__(self, group='', **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_delete_group')
        self.register_event_type('on_rename_group')
        self.register_event_type('on_change_focus')
        self.group = group

    def on_change_focus(self):
        if self.ids['grp_input'].focus:
            self.old_group = self.ids['grp_input'].text
        elif self.old_group != self.ids['grp_input'].text:
            self.group = self.ids['grp_input'].text
            self.dispatch('on_rename_group')

    def on_delete_group(self):
        return self

    def on_rename_group(self):
        return self

class TaskWidget(BoxLayout):
    '''
    Change widget height and size_hint_y to 0 to hide. Be sure to save original settings

    '''
    edit = BooleanProperty(None)
    task = ObjectProperty(None)
    group_list = ListProperty(['None'])

    # stored_data = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_delete')
        self.register_event_type('on_complete')
        self.group_list = App.get_running_app().screenmanager.get_screen('screen-task').task_collection.group_list
        Window.bind(on_keyboard=self.on_keyboard)
        self.edit_wid_list = [
            self.ids['task_btm'],
            self.ids['edit_spc'],
            self.ids['freq_spin'],
            self.ids['group_spin'],
            self.ids['but_del']
        ]
        self.norm_wid_list = [
            self.ids['lbl_freq'],
            self.ids['lbl_group'],
            self.ids['btn_complete']
        ]

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        # print(key, codepoint, modifier)
        if self.edit and key == 27:  # escape
            self.edit = not self.edit
        # Delete doesn't work well when you try and delete several tasks in a row
        # if self.edit and key == 127: # delete
        #     self.ids['but_del'].dispatch('on_release')
        if self.edit and codepoint == 'g':
            self.ids['group_spin'].is_open = True
        if self.edit and codepoint == 'f':
            self.ids['freq_spin'].is_open = True

    def on_task(self, instance, value):
        '''Used to link widget parameters to the task object'''
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
        if value:
            # edit mode
            self.ids['task_input'].disabled = False
            self.group_list = App.get_running_app().screenmanager.get_screen('screen-task').task_collection.group_list
            self.ids['group_spin'].values = self.group_list
            self.ids['task_input'].focus = True
            # self.height = '110dp'
        else:
            # display mode
            self.task.text = self.ids['task_input'].text
            self.task.frequency = self.ids['lbl_freq'].text = self.ids['freq_spin'].text
            self.task.group = self.ids['lbl_group'].text = self.ids['group_spin'].text
            self.ids['task_input'].disabled = True
            self.ids['task_input'].focus = False
            # self.height = '50dp'
        self.toggle_widget(*self.edit_wid_list)
        self.toggle_widget(*self.norm_wid_list)

    def frequency_changed(self):
        self.task.frequency = self.ids['freq_spin'].text
        self.task.set_due_date(self.task)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) is True and self.edit is False:
            # if touch is inside task widget
            if self.ids['btn_complete'].collide_point(*touch.pos) is True:
                # if mark complete is touched
                return super(TaskWidget, self).on_touch_down(touch)
            else:
                self.edit = not self.edit  # enters edit mode
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

    def on_complete(self):
        # add in temp archive to undo and/or schedule revive
        self.toggle_widget(self)
        return self

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


class DeleteTaskPopup(Popup):
    # Properties
    # Functions
    # Todo add in delete task confirmation
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    def on_open(self):
        pass

    def on_dismiss(self):
        return self
