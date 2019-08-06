# -*- coding:utf-8 -*-
# create_time: 2019/8/6 11:48
# __author__ = 'brad'


class BaseTask(object):
    _base = "base"

    def run(self, obj, transition):
        raise NotImplementedError(".run() must be overridden.")
