# -*- coding:utf-8 -*-
# create_time: 2019/8/6 11:48
# __author__ = 'brad'


class RunMixin(object):
    def run(self, obj, transition):
        raise NotImplementedError(".run() must be overridden.")


class BaseTask(object, RunMixin):
    pass


class WaitingTask(object, RunMixin):
    """
    WaitingTask will set the current state waiting for the task result.
    """
    pass
