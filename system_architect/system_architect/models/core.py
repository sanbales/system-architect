#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from uuid import uuid4

__all__ = ('CoreModel', 'Scenario', 'Category', 'Function', 'Project', 'System', 'WeightingScale', 'WeightLevel')


class CoreModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, help_text="An explanation of the item.")

    class Meta:
        abstract = True

    def __str__(self):
        return "<{}: '{}'>".format(self.__class__.__name__,
                                   self.name[:32] + ('...' if len(self.name) > 32 else ''))


class Term(CoreModel):
    pass


class Project(CoreModel):
    """
    The highest level entity that serves as a grouping for the system architecture to be developed.

    """
    glossary = models.ManyToManyField(Term, help_text="A list of terms that are relevant to this project")

    def add_goal(self, **kwargs):
        return Goal.objects.create(project=self, **kwargs)

    def add_category(self, **kwargs):
        return Category.objects.create(project=self, **kwargs)

    def add_function(self, **kwargs):
        return Function.objects.create(project=self, **kwargs)

    def add_system(self, **kwargs):
        return System.objects.create(project=self, **kwargs)

    def add_scale(self, **kwargs):
        return WeightingScale.objects.create(project=self, **kwargs)


class Goal(CoreModel):
    """
    The one or one of the objectives of the project. This should be a high level statement that describes what
    the overarching functionality desired is.

    ..note::
        The description field should contain a narrative that describes the goal in tangible terms.

    ..note::
        Terms can be associated with the goal description to clarify non-intuitive domain-specific terminology.

    """

    body = models.TextField(help_text="A narrative that describes the goal.")
    project = models.ForeignKey(Project, related_name='goals',
                                help_text="The project that owns this goal.")
    terms = models.ManyToManyField(Term, help_text="Terms that are relevant to explaining this goal.")

    @property
    def glossary(self):
        return self.project.glossary.all()


class Scenario(CoreModel):
    project = models.ForeignKey(Project, related_name='scenarios',
                                help_text="The project that owns this scenario.")
    parent = models.ForeignKey('self', blank=True, null=True,
                               related_name='sub_scenarios',
                               help_text="A broader and more encompassing scenario.")


class Category(CoreModel):
    project = models.ForeignKey(Project, related_name='categories',
                                help_text="The project that owns this category.")
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

    ..note::
        Functions may not require systems, e.g., shooting down an airborne target may not require an SM-2, nor may it
        require a missile, as this relationship would prescribe a system solution to a particular need. When users
        specify these relationships they are biasing the solution space. It is possible that the solution the user has
        in mind is in fact the most effective one, but the system should not allow that relationship to occur because
        conditions may change, or the user may not have a complete understanding of the possible means to achieve that
        function. Furthermore, if one was to face the need to state that one function requires more than one system,
        it is more valuable to decompose that function into the sub-functions the systems in question would perform
        towards the satisfaction of the former function. This is a better representation of reality because if both
        systems are required it means that they are inherently performing different functions, each of which is
        required to satisfy the first function.

    ..note::
        Functions may not be incompatible with another function, e.g., <detect airborne targets> and <communicate
        through satellite relays> cannot be made incompatible because their incompatibility arises from the
        technologies used. During the Falklands War it may have been a true statement that those two functions were
        incompatible, but as technology progressed, said incompatibilities were removed by using newer systems that
        did not interfere with one another.

    """
    project = models.ForeignKey(Project, related_name='functions',
                                help_text="The project that owns this functions.")
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

    ..note::
        Systems may not require another system, e.g., an SM-2 may not require a MK 41 Vertical Launch System (VLS).
        If a user desires to specify a system requiring another, that system requirement is an indication that the
        requiring system (e.g., the SM-2 in the prior example) requires a function that is provided by the required
        system (e.g., the MK 41 VLS may provide “host and launch Standard Missile”). It may be true that at the time
        of the specification, only one system could provide this functionality, but that does not mandate that
        another system in the future may not be able to provide the required functionality. By having systems require
        functions, the framework is made more robust to future developments and can identify functions that may be of
        interest for future development in order to develop more robust architectures.

    """
    project = models.ForeignKey(Project, related_name='systems',
                                help_text="The project that owns this system.")
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
    project = models.ForeignKey(Project, related_name='scales',
                                help_text="The project that owns this weighting scale.")
    criteria = models.CharField(max_length=255,
                                help_text="The succinct statement that explains what the weighting scale is measuring.")

    def add_level(self, name, value):
        return WeightLevel.objects.create(name=name, value=value, scale=self)

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
