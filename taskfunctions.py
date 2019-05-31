import time


class Task(object):
    group_list = ['None']
    status_list = ['normal', 'edit', 'archived']
    frequency_list = ['Once', 'Weekly', 'Monthly', 'Quarterly', 'Annually']

    def __init__(self, text='', id_num=1, group='', frequency='Once'):
        self.id = id_num
        self._text = text
        self.time = self._get_time_now()
        self._group = group
        self._frequency = frequency
        self._status = 'edit'
        self._complete = False

    def _get_time_now(self):
        month = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct',
                 11: 'Nov', 12: 'Dec'}
        now = time.localtime(time.time())
        year = str(now[0])
        month = month[now[1]]
        day = str(now[2]).zfill(2)
        hour = str(now[3]).zfill(2)
        minute = str(now[4]).zfill(2)
        stamp = hour + ':' + minute + ' ' + month + ' ' + day + ' ' + year
        return stamp

    def archive_task(self):
        pass

    # move task to archive list

    @classmethod
    def add_group(cls, group_name):
        group_name = str(group_name)
        if group_name not in cls.group_list:
            cls.group_list.append(group_name)
        else:
            raise ValueError('Group {group_name} already exists')
        return cls

    @classmethod
    def rename_group(cls, old_group_name, new_group_name):
        idx = cls.group_list.index(str(old_group_name))
        cls.group_list[idx] = str(new_group_name)
        return cls

    @classmethod
    def delete_group(cls, group_name):
        # add check for group existence and if any tasks are in group
        cls.group_list.remove(str(group_name))
        return cls

    @property
    def text(self):
        return str(self._text)

    @text.setter
    def text(self, text):
        if self._text != text:
            self._text = text
            self.time = self._get_time_now()

    @property
    def group(self):
        return str(self._group)

    @group.setter
    def group(self, group):
        if self._group != group:
            self._group = group
            self.time = self._get_time_now()

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, freq):
        if freq in self.frequency_list:
            self._frequency = freq

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        if status in status_list:
            self._status = status

    # create event that will trigger the view change for edit or archival

    @property
    def complete(self):
        return self._complete

    @complete.setter
    def complete(self, value):
        if type(value) is bool:
            self._complete = value
        else:
            raise TypeError(f'Complete values must be boolean, not {value}, type {type(value)}')


class TaskCollection(object):

    def __init__(self):
        self.count = 0
        self.tasks = []

    def new_task(self):
        task = Task()
        self._add_task(task)
        return self.tasks[-1]

    def _add_task(self, task):
        task.id = self.count + 1
        self.count += 1
        self.tasks.append(task)

    def remove_task(self, task):
        self.tasks.remove(task)
        self.count -= 1

    def modify_task(self, task):
        for tsk in self.tasks:
            if tsk.id == task.id:
                self.tasks[self.tasks.index(tsk)] = task
                break

# -----------------
# t = Task('First Task')
# Task.add_group('First Group')
# print(Task.group_list)
