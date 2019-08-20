import calendar as cal
import datetime as dt

from ruamel.yaml import YAML, yaml_object


def _get_next_day_of(target_type: str = 'weekday', next_day_name: str = 'Monday'):
    tt = target_type.lower()
    tt_opts = ['day', 'weekday', 'week', 'month', 'quarter', 'year']
    if tt not in tt_opts:
        raise ValueError(f'target_type must be one of {tt_opts}, instead of {tt}')
    today = dt.date.today()
    next_day = tuple(cal.day_name).index(next_day_name)
    while True:
        # looping to allow quarter and annual to use month functionality
        if tt == 'day':
            # return tomorrow
            return today + dt.timedelta(days=1)
        elif tt == 'weekday':
            # return next weekday
            if today.weekday() < 4:
                return today + dt.timedelta(days=1)
            else:
                return today + dt.timedelta(days=3)
        elif tt == 'week':
            # return date of next_day_name in next week
            return today + dt.timedelta(days=7 - today.weekday() + next_day)
        elif tt == 'month':
            # return date of first weekday in next month
            for day in cal.Calendar().itermonthdays2(today.year, today.month + 1):
                if day[1] < 5:  # day is target weekday
                    break
            return today.replace(month=today.month + 1, day=day[0])
        elif tt == 'quarter':
            # change month of 'today' to last month of current quarter
            today = today.replace(month=(today.month + 2) // 3 * 3, day=1)
            # day changed to avoid days in month error
            tt = 'month'
        elif tt == 'year':
            # return date of first weekday in current month number of next year
            today = today.replace(year=today.year + 1, month=today.month - 1, day=1)
            tt = 'month'

@yaml_object(YAML())
class Task(object):
    frequency_list = ['One-Time', 'Daily', 'Weekly', 'Monthly', 'Quarterly', 'Annual']

    def __init__(self, text='', id_num=1, group='None', frequency='One-Time'):

        self.id = id_num
        self._text = text
        self._init_time = self._edit_time = self._refresh_time = dt.date.today()
        self._group = group
        self._frequency = frequency
        self.set_due_date(self)
        self._day_name = 'Monday'

    @staticmethod
    def set_due_date(self):
        # freq to next occurrence trigger dict
        if self._frequency == self.frequency_list[0]:  # Once
            self._due_date = None
        elif self._frequency == self.frequency_list[1]:  # Daily
            self._due_date = _get_next_day_of(target_type='weekday')
        elif self._frequency == self.frequency_list[2]:  # Weekly
            self._due_date = _get_next_day_of(target_type='week')
        elif self._frequency == self.frequency_list[3]:  # Monthly
            self._due_date = _get_next_day_of(target_type='month')
        elif self._frequency == self.frequency_list[4]:  # Quarterly
            self._due_date = _get_next_day_of(target_type='quarter')
        elif self._frequency == self.frequency_list[5]:  # Annually
            # first day month task was created in.
            self._due_date = _get_next_day_of(target_type='year')

    def is_task_due(self):
        if self._due_date is not None:
            return self._due_date <= dt.date.today()
        else:
            return False

    '''
    # on task creation:
    # set start to task creation moment (aka current time). DONE
    # set due to next start time. DONE

    # on task complete:
    # set refresh_time to next refresh_time. If _due_time is None, archive task.

    # on app start:
    # refresh tasks based on current time
    # if next task start is before current moment and task is complete, move to current display
    # if overdue indicate
    
    '''

    @property
    def text(self):
        return str(self._text)

    @text.setter
    def text(self, text):
        if self._text != text:
            self._text = text
            self._edit_time = dt.date.today()

    @property
    def group(self):
        return str(self._group)

    @group.setter
    def group(self, group):
        if self._group != group:
            self._group = group
            self._edit_time = dt.date.today()

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, freq):
        if freq in self.frequency_list:
            self._frequency = freq
            self._edit_time = dt.date.today()

@yaml_object(YAML())
class TaskCollection(object):

    def __init__(self):
        self.count = 0
        self.tasks = []
        self.group_list = ['None']
        self.archived_tasks = []
        self.scheduled_tasks = []

    def new_task(self):
        # may not need both of these
        task = Task()
        self._add_task(task)
        return self.tasks[-1]

    def _add_task(self, task):
        task.id = self.count + 1
        self.count += 1
        self.tasks.append(task)

    def modify_task(self, task):
        for tsk in self.tasks:
            if tsk.id == task.id:
                self.tasks[self.tasks.index(tsk)] = task
                break

    def schedule_task(self, task):
        if task._due_date is not None:
            self.scheduled_tasks.append(task)
            self.tasks.remove(task)
            self.count -= 1
        else:
            self.archive_task(task)

    def check_scheduled_tasks(self):
        for task in self.scheduled_tasks:
            if task.is_task_due():
                self._add_task(task)
                self.scheduled_tasks.remove(task)

    def archive_task(self, task):
        '''
        Stores a deleted task in a list
        :param task: the task to be deleted form the collection
        :return: None
        '''
        self.archived_tasks.append(task)
        self.tasks.remove(task)
        self.count -= 1

    def recover_task(self, out_task=False):
        '''
        Used to undo the deletion of a task
        :param out_task: set to True to return the task
        :return: [task]
        '''
        recovered_task = self.archived_tasks.pop()
        self._add_task(recovered_task)
        if out_task:
            return recovered_task

    def filter_tasks(self, freq='', group='', text=''):
        '''
        return a list of tasks that meet the filter

        :param freq: frequency to filter by in tasks
        :param group: group to filter by in tasks
        :param text: str to search for in tasks
        :return task_list: filtered task list
        '''
        filt_tasks = []
        text.lower()
        if freq != '':
            for frequency in Task.frequency_list:
                if freq.lower() in frequency.lower():
                    freq_tasks = (task for task in self.tasks if task._frequency == frequency)
                    [filt_tasks.append(task) for task in freq_tasks if task not in filt_tasks]
        if group != '':
            for group_name in self.group_list:
                if group.lower() in group_name.lower():
                    grp_tasks = [task for task in self.tasks if task.group == group_name]
                    [filt_tasks.append(task) for task in grp_tasks if task not in filt_tasks]

        if text != '':
            text_tasks = [task for task in self.tasks if text in task.text.lower()]
            [filt_tasks.append(task) for task in text_tasks if task not in filt_tasks]
        return filt_tasks

    def bin_tasks_by(self, category='group'):
        if category.lower() == 'group':
            binned_tasks = {group: self.filter_tasks(group=group) for group in self.group_list}
        else:  # category.lower() == 'frequency':
            binned_tasks = {frequency: self.filter_tasks(freq=frequency) for frequency in Task.frequency_list}
        return {key: binned_tasks[key] for key in binned_tasks if len(binned_tasks[key]) > 0}

    def add_group(self, group_name):
        group_name = str(group_name)
        if group_name not in self.group_list and group_name is not '':
            self.group_list.append(group_name)
        else:
            print(self.group_list)
            raise ValueError(f'Group {group_name} already exists')
        return self

    def rename_group(self, old_group_name, new_group_name):
        idx = self.group_list.index(str(old_group_name))
        self.group_list[idx] = str(new_group_name)
        self._update_groups(old_group_name, new_group_name)
        return self

    def delete_group(self, group_name):
        # add check for group existence and if any tasks are in group
        self.group_list.remove(str(group_name))
        self._update_groups(group_name)
        return self

    def _update_groups(self, group_name, new_group_name='None'):
        for task in self.tasks:
            if task.group == group_name:
                task.group = new_group_name
