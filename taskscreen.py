import re

from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ObjectProperty, BooleanProperty, ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from taskfunctions import TaskCollection


# Todo add a way switch to screen/view of completed tasks so they can be marked incomplete
# Todo (optional) add in ability to show tasks for next days, weeks, or months tasks
# Add in a day selector that changes the 'today' and refreshes the hidden tasks. Reset with another time
class TaskScreen(Screen):
    task_widgets = ListProperty([])
    hidden_task_widgets = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_collection = TaskCollection()

    def refill_task_collection(self, task_collection):
        # makes stored task_c the task_c used in TaskScreen
        self.task_collection = task_collection
        self.task_collection.check_scheduled_tasks()
        for task in self.task_collection.tasks:
            taskwidget = self.add_taskwidget(task, task_out=False)

    def archive_task(self, instance):
        #         # print(self.task_collection.tasks, instance.task.text)
        self.task_collection.archive_task(instance.task)
        self.task_widgets.remove(instance)
        self.set_layout()

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
        taskwidget.bind(on_refresh_groups=self.refresh_groups)
        taskwidget.bind(on_complete=self.schedule_task)
        self.task_widgets.append(taskwidget)
        self.set_layout()
        if task_out:
            return taskwidget

    def schedule_task(self, instance):
        '''Wrapper for task collection fx schedule_task'''
        if instance.task in self.task_collection.scheduled_tasks:
            instance.opacity = 1
            self.task_collection.scheduled_tasks.remove(instance.task)
            instance.ids['btn_complete'].background_normal, instance.ids['btn_complete'].background_down = instance.ids[
                                                                                                               'btn_complete'].background_down, \
                                                                                                           instance.ids[
                                                                                                               'btn_complete'].background_normal
            # make a normal task
        else:
            self.task_collection.schedule_task(instance.task)
            self.task_widgets.remove(instance)
        self.set_layout()

    def toggle_scheduled_tasks(self):
        if self.ids['top_bar'].ids['toggle_complete'].state == 'down':
            for task in self.task_collection.scheduled_tasks:
                self.task_collection._add_task(task)
                task_w = self.add_taskwidget(task, task_out=True)
                task_w.opacity = 0.5
                task_w.ids['btn_complete'].background_normal, task_w.ids['btn_complete'].background_down = task_w.ids[
                                                                                                               'btn_complete'].background_down, \
                                                                                                           task_w.ids[
                                                                                                               'btn_complete'].background_normal

        else:
            delete_list = []
            for task_w in self.task_widgets:
                if task_w.task in self.task_collection.scheduled_tasks:
                    task_w.opacity = 1
                    task_w.ids['btn_complete'].background_normal, task_w.ids['btn_complete'].background_down = \
                        task_w.ids[
                            'btn_complete'].background_down, \
                        task_w.ids[
                            'btn_complete'].background_normal
                    delete_list.append(task_w)
            [self.archive_task(task_w2) for task_w2 in delete_list]

    def search_tasks(self, value):
        search_dict = {}
        TaskWidget().hideshow_widget(True, *self.hidden_task_widgets)
        self.hidden_task_widgets = []
        if ':' not in value and value != '':  # plain text search
            search_dict['text'] = value
        elif ':' in value:  # parsing required
            search_text = [val.strip() for val in
                           re.findall('(?<=[fg]:)\s*[\w]*', value)]  # finds text that follow keys
            if '' in search_text:
                return True
            search_keys = [key.strip() for key in re.split('(?<=[fg]:)\s*[\w]*', value)]  # finds g: and f:

            for idx, text in enumerate(search_text):
                key = search_keys[idx]
                if 'g:' in key:
                    search_dict['group'] = text
                elif 'f:' in key:
                    search_dict['freq'] = text
                else:
                    pass
            if ':' not in search_keys[-1]:
                search_dict['text'] = search_keys[-1].strip()
        else:  # no search
            return True

        filtered_tasks = self.task_collection.filter_tasks(**search_dict)
        for task_w in self.task_widgets:
            if task_w.task not in filtered_tasks:
                self.hidden_task_widgets.append(task_w)
        TaskWidget().hideshow_widget(False, *self.hidden_task_widgets)

    def set_layout(self, *args):
        [child.container.clear_widgets() for child in self.ids['task_container_section'].children]
        self.ids['task_container_section'].clear_widgets()
        if 'freq' in App.get_running_app().layout.lower():
            binned_tasks = self.task_collection.bin_tasks_by('frequency')
            for freq in binned_tasks:
                freq_container = TaskWidgetContainer()
                freq_container.ids['container'].add_widget(Label(text=freq + ' Tasks'))
                for task_w in self.task_widgets:
                    if task_w.task.frequency == freq:
                        task_w.show_freq_lbl = False
                        task_w.show_group_lbl = True
                        freq_container.ids['container'].add_widget(task_w)
                self.ids['task_container_section'].add_widget(freq_container)
        elif 'group' in App.get_running_app().layout.lower():
            binned_tasks = self.task_collection.bin_tasks_by('group')
            for group in binned_tasks:
                group_container = TaskWidgetContainer()
                group_container.ids['container'].add_widget(Label(text=group + ' Tasks'))
                for task_w in self.task_widgets:
                    if task_w.task.group == group:
                        task_w.show_freq_lbl = True
                        task_w.show_group_lbl = False
                        group_container.ids['container'].add_widget(task_w)
                self.ids['task_container_section'].add_widget(group_container)
        else:  # list view
            self.ids['task_container_section'].add_widget(TaskWidgetContainer())
            for task_w in self.task_widgets:
                task_w.show_freq_lbl = True
                task_w.show_group_lbl = True
                self.ids['task_container_section'].children[-1].ids['container'].add_widget(task_w)
        if self.ids['task_container_section'].width == 100:
            self.ids['task_container_section']._trigger_layout()
        if Window.size[0] / len(self.ids['task_container_section'].children) < 80:
            # App.get_running_app().layout = 'List'
            self.ids['task_container_section'].rows = 6
            # self.ids['task_container_section'].cols = 1
        elif Window.size[0] / len(self.ids['task_container_section'].children) < 150:
            self.ids['task_container_section'].rows = 3
        elif Window.size[0] / len(self.ids['task_container_section'].children) < 300:
            self.ids['task_container_section'].rows = 2
        else:
            self.ids['task_container_section'].rows = 1
        self.ids['task_container_section']._trigger_layout()
        print(Window.size[0] / len(self.ids['task_container_section'].children))

    def on_touch_down(self, touch):
        for container in self.ids['task_container_section'].children:
            for task_w in container.children:
                if type(task_w) == 'TaskWidget':
                    task_w.on_touch_down(touch)
        return super(TaskScreen, self).on_touch_down(touch)

    def manage_groups_popup(self):
        # create popup to add group to task class
        popup = ManageGroupPopup()
        popup.bind(on_dismiss=self.refresh_groups)
        popup.open()
        return self

    def refresh_groups(self, popup):
        for task_wid in self.task_widgets:
            task_wid.ids['group_spin'].values = task_wid.group_list = self.task_collection.group_list
            task_wid.ids['lbl_group'].text = task_wid.ids['group_spin'].text = task_wid.task.group

class TopBar(BoxLayout):
    # contains app header

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_add_taskwidget')
        self.register_event_type('on_manage_groups')
        self.register_event_type('on_search_entry')
        self.register_event_type('on_show_complete_tasks')

    def on_add_taskwidget(self):
        pass

    def on_manage_groups(self):
        pass

    def on_search_entry(self):
        pass

    def on_show_complete_tasks(self):
        pass


class TaskWidgetContainer(ScrollView):
    container = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class TaskWidget(BoxLayout):
    '''
    Change widget height and size_hint_y to 0 to hide. Be sure to save original settings

    '''
    edit = BooleanProperty(None)
    task = ObjectProperty(None)
    group_list = ListProperty(['None'])
    show_freq_lbl = BooleanProperty(True)
    show_group_lbl = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_delete')
        self.register_event_type('on_complete')
        self.group_list = App.get_running_app().screenmanager.get_screen('screen-task').task_collection.group_list
        Window.bind(on_keyboard=self.on_keyboard)
        self.edit_wid_list = [
            self.ids['edit_spc'],
            self.ids['freq_spin'],
            self.ids['group_spin'],
            self.ids['but_del'],
            self.ids['task_btm']]
        self.norm_wid_list = [
            self.ids['lbl_freq'],
            self.ids['lbl_group'],
            self.ids['btn_complete']
        ]

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        #         # print(key, codepoint, modifier)
        if self.edit and key == 27:  # escape
            self.edit = not self.edit
        # Delete doesn't work well when you try and delete several tasks in a row
        # if self.edit and key == 127: # delete
        #     self.ids['but_del'].dispatch('on_release')
        if self.edit and modifier == 'shift' and codepoint == 'g':
            self.ids['group_spin'].is_open = True
        if self.edit and modifier == 'shift' and codepoint == 'f':
            self.ids['freq_spin'].is_open = True

    def on_task(self, instance, value):
        '''Used to link widget parameters to the task object'''
        self.ids['task_input'].text = self.task.text
        self.ids['lbl_freq'].text = self.task.frequency
        self.ids['lbl_group'].text = self.task.group
        self.ids['freq_spin'].text = self.task.frequency
        self.ids['group_spin'].text = self.task.group
        if self.ids['task_input'].text == '' and self.task.frequency == 'One-Time' and self.task.group == 'None':
            # This is a new task
            self.hideshow_widget(True, *self.edit_wid_list)
            self.edit = True
        else:
            # This is a reloaded task
            self.hideshow_widget(True, *self.norm_wid_list)
            self.edit = False

    def on_edit(self, instance, value):
        if value:
            # edit mode
            self.ids['task_input'].disabled = False
            self.group_list = App.get_running_app().screenmanager.get_screen('screen-task').task_collection.group_list
            self.ids['group_spin'].values = self.group_list
            self.ids['task_input'].focus = True
            # self.height = '110dp'
            self.hideshow_widget(True, *self.edit_wid_list)
            self.hideshow_widget(False, *self.norm_wid_list)
        else:
            # display mode
            self.task.text = self.ids['task_input'].text
            self.task.frequency = self.ids['lbl_freq'].text = self.ids['freq_spin'].text
            self.task.group = self.ids['lbl_group'].text = self.ids['group_spin'].text
            self.ids['task_input'].disabled = True
            self.ids['task_input'].focus = False
            App.get_running_app().store_data(clear_archive=False)
            self.hideshow_widget(False, *self.edit_wid_list)
            self.hideshow_widget(True, *self.norm_wid_list)
            # self.height = '50dp'
        App.get_running_app().screenmanager.get_screen('screen-task').set_layout()
        self._trigger_layout()

    def on_show_freq_lbl(self, instance, value):
        if int(value) == True:
            if self.ids['lbl_freq'] not in self.norm_wid_list:
                self.norm_wid_list.append(self.ids['lbl_freq'])
            # show frequency label
            self.hideshow_widget(True, self.ids['lbl_freq'])  # shows
        else:
            if self.ids['lbl_freq'] in self.norm_wid_list:  # False
                self.norm_wid_list.remove(self.ids['lbl_freq'])
            self.hideshow_widget(False, self.ids['lbl_freq'])  # hides

    def on_show_group_lbl(self, instance, value):
        # print(self,instance,value)
        if int(value) == True:
            if self.ids['lbl_group'] not in self.norm_wid_list:
                self.norm_wid_list.append(self.ids['lbl_group'])
            # show group label
            self.hideshow_widget(True, self.ids['lbl_group'])  # shows
        else:
            if self.ids['lbl_group'] in self.norm_wid_list:  # False
                self.norm_wid_list.remove(self.ids['lbl_group'])
            self.hideshow_widget(False, self.ids['lbl_group'])  # hides

    #             # print('hiding g lable')

    def frequency_changed(self):
        self.task.frequency = self.ids['freq_spin'].text
        self.task.set_due_date(self.task)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) is True and self.edit is False:
            # print('saw touch inside task')
            # if touch is inside task widget
            if self.ids['btn_complete'].collide_point(*touch.pos) is False:
                # if mark complete was not touched
                self.edit = not self.edit  # enters edit mode
        elif self.collide_point(*touch.pos) is False and self.edit is True:
            # print('st out')
            # if touch is outside and task widget is in edit mode
            self.edit = not self.edit  # exits edit mode
        else:  # super return allows the touch to carry on
            pass
        return super(TaskWidget, self).on_touch_down(touch)

    def on_delete(self):
        # move to archive
        return self

    def on_complete(self):
        # add in temp archive to undo and/or schedule revive
        return self

    def hideshow_widget(self, show=True, *args):
        '''Toggles view state of the passed widgets'''
        for wid in args:
            #             # print('Id: ',wid)
            if hasattr(wid, 'saved_attrs') and show is True:
                wid.height, wid.size_hint_y, wid.opacity = wid.saved_attrs
                del wid.saved_attrs
            elif show is False:
                wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity
                wid.height, wid.size_hint_y, wid.opacity = 0, None, 0
            else:
                # do nothing for show = True and hasattr = False
                # do nothing for show = False and hasattr = True
                pass

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
            group_w.remove_widget(group_w.but_del)
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
