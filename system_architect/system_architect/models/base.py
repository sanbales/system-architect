from django.db import models
from uuid import uuid4

__all__ = ('CoreModel', 'Scenario', 'Category', 'Function', 'System', 'WeightingScale', 'WeightLevel')


class CoreModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "<{}: '{}'>".format(self.__class__.__name__,
                                   self.name[:32] + ('...' if len(self.name) > 32 else ''))


class Scenario(CoreModel):
    sub_scenarios = models.ManyToManyField('self', symmetrical=False, blank=True,
                                           related_name='super_scenarios',
                                           help_text="Scenarios that refine this one.")


class Category(CoreModel):
    parent = models.ForeignKey('self', blank=True, null=True, related_name='sub_categories',
                               help_text="The super-category.")
    kind = models.PositiveSmallIntegerField(choices=((0, 'Functions'),
                                                     (1, 'Systems'),
                                                     (2, 'Both')), blank=False, null=False,
                                            help_text="The type of entities that can be in this category.")

    class Meta:
        verbose_name_plural = 'categories'


class Function(CoreModel):
    """
    A thing that can or must be done.

    ..note::
        Functions have to be defined clearly so other users can understand them without ambiguity and be able to link
        their own functions and systems to them.

        Functions cannot reference a system or class of system in their name, unless they are indicating a specific
        functionality requirement for a specific system or class of systems, otherwise they should be a system or a
        mapping between functions and systems.

    """
    categories = models.ManyToManyField(Category, blank=True)
    requires = models.ManyToManyField('self', blank=True, symmetrical=False,
                                      related_name='required_by_functions', through='FunctionRequires',
                                      through_fields=('requiring', 'required'),
                                      help_text="The functions this function requires.")
    satisfies = models.ManyToManyField('self', blank=True, symmetrical=False,
                                       related_name='satisfied_by_functions', through='FunctionSatisfies',
                                       through_fields=('satisfier', 'satisfied'),
                                       help_text="The functions this function satisfies.")


class System(CoreModel):
    """
    An entity that can satisfy certain functions.

    ..note::
        Systems can be defined as entities that perform a function, e.g., a radar receiver, or computational elements
        that perform a function, e.g., identification algorithm.
        - Generally computational elements may reside on specific hardware so it is customary to focus on physical
          systems, but as more functionality is assigned to software that can reside on a multitude of hardware
          systems, it is important to acknowledge this explicitly in the knowledge base.
        A system exhibits processes that fulfill a function, systems that do not perform a function that is relevant
        to the needs of a project are not relevant.

    """
    categories = models.ManyToManyField(Category, blank=True)
    requires = models.ManyToManyField(Function, blank=True, symmetrical=False,
                                      related_name='required_by_systems', through='SystemRequires',
                                      through_fields=('requiring', 'required'),
                                      help_text="The functions this function requires.")
    satisfies = models.ManyToManyField(Function, blank=True, symmetrical=False,
                                       related_name='satisfied_by_systems', through='SystemSatisfies',
                                       through_fields=('satisfier', 'satisfied'),
                                       help_text="The functions this function satisfies.")


class WeightingScale(CoreModel):
    def add_level(self, name, value):
        WeightLevel.objects.create(name=name, value=value, scale=self)

    def __str__(self):
        return "<Scale: {}>".format(self.name)

    @property
    def max(self):
        return max(level.value for level in self.levels.all())

    @property
    def min(self):
        return min(level.value for level in self.levels.all())


class WeightLevel(models.Model):
    scale = models.ForeignKey(WeightingScale, related_name='levels',
                              help_text="The scale that owns this level.")
    name = models.CharField(max_length=32, help_text="The name of the scale.")
    value = models.FloatField(help_text="The numerical value of this level.")

    class Meta:
        ordering = ['scale', '-value']

    def __str__(self):
        return "<{} Scale: {} Value>".format(self.scale.name, self.name)
