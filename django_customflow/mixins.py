# -*- coding:utf-8 -*-
# create_time: 2019/8/5 16:02
# __author__ = 'brad'
from . import utils


class WorkflowMixin(object):
    """Mixin class to make objects workflow aware.
    """

    def get_workflow(self):
        """Returns the current workflow of the object.
        """
        return utils.get_workflow(self)

    def remove_workflow(self):
        """Removes the workflow from the object. After this function has been
        called the object has no *own* workflow anymore (it might have one via
        its content type).

        """
        return utils.remove_workflow_from_object(self)

    def set_workflow(self, workflow):
        """Sets the passed workflow to the object. This will set the local
        workflow for the object.

        If the object has already the given workflow nothing happens.
        Otherwise the object gets the passed workflow and the state is set to
        the workflow's initial state.

        **Parameters:**

        workflow
            The workflow which should be set to the object. Can be a Workflow
            instance or a string with the workflow name.
        obj
            The object which gets the passed workflow.
        """
        return utils.set_workflow_for_object(self, workflow)

    def get_state(self):
        """Returns the current workflow state of the object.
        """
        return utils.get_state(self)

    def set_state(self, state):
        """Sets the workflow state of the object.
        """
        return utils.set_state(self, state)

    def set_initial_state(self):
        """Sets the initial state of the current workflow to the object.
        """
        return self.set_state(self.get_workflow().initial_state)

    def do_transition(self, transition, user):
        """Processes the passed transition (if allowed).
        """
        return utils.do_transition(self, transition, user)

    def do_next_state(self):

        state = self.get_state()
        transitions = state.transitions.all()

        # info:这里代表状态节点是最后的一层了
        if not transitions:
            return False

        for transition in transitions:
            if transition.condition:
                cond = utils.import_from_string(transition.condition)
                # todo:目前这里是轮询到条件正确的一个, 就跳出轮询设置状态了
                if not cond().run(self, transition):
                    continue
            if transition.task:
                # todo:task是顺序还是异步执行, 还是有前向倚赖,这个需要确定完善
                task = utils.import_from_string(transition.task)
                task().run(self, transition)
            next_state_instance = transition.destination
            self.set_state(next_state_instance)

            # info:记录日志
            self.set_log(state=next_state_instance.name, source_state=state.name, transition=transition.name)

            # todo:这个是遍历操作, 只要是设置为下一个状态不需要手动操作, 就在这里执行
            if not next_state_instance.manual:
                return self.do_next_state()
            return True

    def set_log(self, state, source_state=None, transition=None):
        return utils.set_log(self, state, source_state, transition)

    def get_log(self):
        return utils.get_log(self)

    def workflow_is_finished(self):
        state = self.get_state()
        if not state.transitions.all():
            return True
        else:
            return False
