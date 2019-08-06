# -*- coding:utf-8 -*-
# create_time: 2019/8/6 16:42
# __author__ = 'brad'

from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Workflow(models.Model):
    """A workflow consists of a sequence of connected (through transitions)
    states. It can be assigned to a model and / or model instances. If a
    model instance has a workflow it takes precendence over the model's
    workflow.

    **Attributes:**

    model
        The model the workflow belongs to. Can be any

    content
        The object the workflow belongs to.

    name
        The unique name of the workflow.

    states
        The states of the workflow.

    initial_state
        The initial state the model / content gets if created.

    """
    name = models.CharField(_(u"Name"), max_length=100, unique=True)
    initial_state = models.ForeignKey("State", on_delete=None, verbose_name=_(u"Initial state"),
                                      related_name="workflow_state",
                                      blank=True, null=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()

    def get_initial_state(self):
        """Returns the initial state of the workflow. Takes the first one if
        no state has been defined.
        """
        if self.initial_state:
            return self.initial_state
        else:
            try:
                return self.states.all()[0]
            except IndexError:
                return None

    def get_objects(self):
        """Returns all objects which have this workflow assigned. Globally
        (via the object's content type) or locally (via the object itself).
        """
        from .utils import get_workflow
        objs = []

        # Get all objects whose content type has this workflow
        for wmr in WorkflowModelRelation.objects.filter(workflow=self):
            ctype = wmr.content_type
            # We have also to check whether the global workflow is not
            # overwritten.
            for obj in ctype.model_class().objects.all():
                if get_workflow(obj) == self:
                    objs.append(obj)

        # Get all objects whose local workflow this workflow
        for wor in WorkflowObjectRelation.objects.filter(workflow=self):
            if wor.content not in objs:
                objs.append(wor.content)

        return objs

    def set_to(self, ctype_or_obj):
        """Sets the workflow to passed content type or object. See the specific
        methods for more information.

        **Parameters:**

        ctype_or_obj
            The content type or the object to which the workflow should be set.
            Can be either a ContentType instance or any Django model instance.
        """
        if isinstance(ctype_or_obj, ContentType):
            return self.set_to_model(ctype_or_obj)
        else:
            return self.set_to_object(ctype_or_obj)

    def set_to_model(self, ctype):
        """Sets the workflow to the passed content type. If the content
        type has already an assigned workflow the workflow is overwritten.

        **Parameters:**

        ctype
            The content type which gets the workflow. Can be any Django model
            instance.
        """
        try:
            wor = WorkflowModelRelation.objects.get(content_type=ctype)
        except WorkflowModelRelation.DoesNotExist:
            WorkflowModelRelation.objects.create(content_type=ctype, workflow=self)
        else:
            wor.workflow = self
            wor.save()

    def set_to_object(self, obj):
        """Sets the workflow to the passed object.

        If the object has already the given workflow nothing happens. Otherwise
        the workflow is set to the objectthe state is set to the workflow's
        initial state.

        **Parameters:**

        obj
            The object which gets the workflow.
        """
        from .utils import set_log, set_state

        ctype = ContentType.objects.get_for_model(obj)
        try:
            wor = WorkflowObjectRelation.objects.get(content_type=ctype, content_id=obj.id)
        except WorkflowObjectRelation.DoesNotExist:
            WorkflowObjectRelation.objects.create(content=obj, workflow=self)
            set_state(obj, self.initial_state)
            set_log(obj, self.initial_state.name)
        else:
            if wor.workflow != self:
                wor.workflow = self
                wor.save()
                set_state(self.initial_state)
                set_log(obj, self.initial_state.name)


class State(models.Model):
    """A certain state within workflow.

    **Attributes:**

    name
        The unique name of the state within the workflow.

    workflow
        The workflow to which the state belongs.

    transitions
        The transitions of a workflow state.

    manual
        If the state can do next state process automatically.

    """
    name = models.CharField(_(u"Name"), max_length=100)
    workflow = models.ForeignKey(Workflow, verbose_name=_(u"Workflow"), related_name="states", on_delete=None, )
    transitions = models.ManyToManyField("Transition", verbose_name=_(u"Transitions"), blank=True, null=True,
                                         related_name="states")
    manual = models.BooleanField("Trigger manually", default=False)

    class Meta:
        ordering = ("name",)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.workflow.name)

    def __str__(self):
        return self.__unicode__()


class Transition(models.Model):
    """A transition from a source to a destination state. The transition can
    be used from several source states.

    **Attributes:**

    name
        The unique name of the transition within a workflow.

    workflow
        The workflow to which the transition belongs. Must be a Workflow
        instance.

    destination
        The state after a transition has been processed. Must be a State
        instance.

    condition
        The condition when the transition is available. It is used by import.

    task
        The task when the transition is available. It is used by import.
    """
    name = models.CharField(_(u"Name"), max_length=100)
    workflow = models.ForeignKey(Workflow, verbose_name=_(u"Workflow"), related_name="transitions", on_delete=None, )
    destination = models.ForeignKey(State, verbose_name=_(u"Destination"), null=True, blank=True,
                                    related_name="destination_state", on_delete=None, )
    condition = models.CharField(_(u"Condition"), blank=True, max_length=100)
    task = models.CharField(_(u"Task"), max_length=100, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()


class LogObjectRelation(models.Model):
    content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content type"), related_name="log_object",
                                     blank=True, null=True, on_delete=None, )
    content_id = models.PositiveIntegerField(_(u"Content id"), blank=True, null=True)
    content = fields.GenericForeignKey(ct_field="content_type", fk_field="content_id")
    create_time = models.DateTimeField(blank=True, auto_now_add=True, help_text=_('log create time'),
                                       verbose_name=_('create time'))
    source_state = models.CharField(_("source state"), max_length=36, null=True, blank=True)
    transition = models.CharField(_("transition"), max_length=36, null=True, blank=True)
    state = models.CharField(_("current state"), max_length=36)

    def __unicode__(self):
        return "%s %s - %s" % (self.content_type.name, self.content_id,
                               self.state)

    def __str__(self):
        return self.__unicode__()


class StateObjectRelation(models.Model):
    """Stores the workflow state of an object.

    Provides a way to give any object a workflow state without changing the
    object's model.

    **Attributes:**

    content
        The object for which the state is stored. This can be any instance of
        a Django model.

    state
        The state of content. This must be a State instance.
    """
    content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content type"), related_name="state_object",
                                     blank=True, null=True, on_delete=None, )
    content_id = models.PositiveIntegerField(_(u"Content id"), blank=True, null=True)
    content = fields.GenericForeignKey(ct_field="content_type", fk_field="content_id")
    state = models.ForeignKey(State, verbose_name=_(u"State"), on_delete=None, )

    def __unicode__(self):
        return "%s %s - %s" % (self.content_type.name, self.content_id, self.state.name)

    def __str__(self):
        return self.__unicode__()

    class Meta:
        unique_together = ("content_type", "content_id", "state")


class WorkflowObjectRelation(models.Model):
    """Stores an workflow of an object.

    Provides a way to give any object a workflow without changing the object's
    model.

    **Attributes:**

    content
        The object for which the workflow is stored. This can be any instance of
        a Django model.

    workflow
        The workflow which is assigned to an object. This needs to be a workflow
        instance.
    """
    content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content type"), related_name="workflow_object",
                                     blank=True, null=True, on_delete=None, )
    content_id = models.PositiveIntegerField(_(u"Content id"), blank=True, null=True)
    content = fields.GenericForeignKey(ct_field="content_type", fk_field="content_id")
    workflow = models.ForeignKey(Workflow, verbose_name=_(u"Workflow"), related_name="wors", on_delete=None, )

    class Meta:
        unique_together = ("content_type", "content_id")

    def __unicode__(self):
        return "%s %s - %s" % (self.content_type.name, self.content_id, self.workflow.name)

    def __str__(self):
        return self.__unicode__()


class WorkflowModelRelation(models.Model):
    """Stores an workflow for a model (ContentType).

    Provides a way to give any object a workflow without changing the model.

    **Attributes:**

    Content Type
        The content type for which the workflow is stored. This can be any
        instance of a Django model.

    workflow
        The workflow which is assigned to an object. This needs to be a
        workflow instance.
    """
    content_type = models.ForeignKey(ContentType, verbose_name=_(u"Content Type"), unique=True, on_delete=None, )
    workflow = models.ForeignKey(Workflow, verbose_name=_(u"Workflow"), related_name="wmrs", on_delete=None, )

    def __unicode__(self):
        return "%s - %s" % (self.content_type.name, self.workflow.name)

    def __str__(self):
        return self.__unicode__()
