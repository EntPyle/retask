import time

from ruamel.yaml import YAML, yaml_object


@yaml_object(YAML())
class Task(object):
    status_list = ['normal', 'edit', 'archived']
    frequency_list = ['Once', 'Weekly', 'Monthly', 'Quarterly', 'Annually']

    def __init__(self, text='', id_num=1, group='', frequency='Once'):
        self.id = id_num
        self._text = text
        self._init_time = self._edit_time = self._get_time_now()
        self._group = group
        self._frequency = frequency
        self._status = 'edit'
        # self._complete = False # TODO delete if not needed

    @staticmethod
    def _get_time_now():
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

    # TODO create function to set next occurency time based on frequency and time of completion

    # @classmethod
    # def add_group(cls, group_name):
    #     group_name = str(group_name)
    #     if group_name not in cls.group_list:
    #         cls.group_list.append(group_name)
    #     else:
    #         raise ValueError('Group {group_name} already exists')
    #     return cls
    #
    # @classmethod
    # def rename_group(cls, old_group_name, new_group_name):
    #     idx = cls.group_list.index(str(old_group_name))
    #     cls.group_list[idx] = str(new_group_name)
    #     return cls
    #
    # @classmethod
    # def delete_group(cls, group_name):
    #     # add check for group existence and if any tasks are in group
    #     cls.group_list.remove(str(group_name))
    #     return cls

    @property
    def text(self):
        return str(self._text)

    @text.setter
    def text(self, text):
        if self._text != text:
            self._text = text
            self._edit_time = self._get_time_now()

    @property
    def group(self):
        return str(self._group)

    @group.setter
    def group(self, group):
        if self._group != group:
            self._group = group
            self._edit_time = self._get_time_now()

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, freq):
        if freq in self.frequency_list:
            self._frequency = freq
            self._edit_time = self._get_time_now()

    @property
    def status(self):
        return self._status

    @status.setter
    # may not be needed
    def status(self, status):
        if status in self.status_list:
            self._status = status
            self._edit_time = self._get_time_now()

@yaml_object(YAML())
class TaskCollection(object):

    def __init__(self):
        self.count = 0
        self.tasks = []
        self.group_list = ['None']
        self.archived_tasks = []

    def new_task(self):
        # may not need both of these
        task = Task()
        self._add_task(task)
        return self.tasks[-1]

    def _add_task(self, task):
        # could set task = Task() by default
        task.id = self.count + 1
        self.count += 1
        self.tasks.append(task)

    def modify_task(self, task):
        for tsk in self.tasks:
            if tsk.id == task.id:
                self.tasks[self.tasks.index(tsk)] = task
                break

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

    def add_group(self, group_name):
        group_name = str(group_name)
        if group_name not in self.group_list:
            self.group_list.append(group_name)
        else:
            raise ValueError('Group {group_name} already exists')
        return self

    def rename_group(self, old_group_name, new_group_name):
        idx = self.group_list.index(str(old_group_name))
        self.group_list[idx] = str(new_group_name)
        return self

    def delete_group(self, group_name):
        # add check for group existence and if any tasks are in group
        self.group_list.remove(str(group_name))
        return self

    # TODO add sorting function for tasks. Bind to a gui sorting dropdown
    # TODO hide until next occurrence function. Add to 'waiting' list
    # TODO show if current time is past next occurence time stamp. Remove from waiting list. Schedule calls in taskscreen

# -----------------TESTING
# from pathlib import Path
# t = Task('First Task')
# Task.add_group('First Group')
# print(Task.group_list)
# tc = TaskCollection()
# tc._add_task(t)
# print(tc)
# yaml = YAML()
# yaml.dump(tc, Path('test_dump.yml'))
# to = yaml.load(Path('test_dump.yml'))
# print(to.tasks[-1].text)
