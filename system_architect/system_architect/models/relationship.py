from django.db import models
from polymorphic.models import PolymorphicModel
from .base import Function, Scenario, System, WeightingScale

__all__ = ('FunctionRequires', 'FunctionSatisfies', 'SystemRequires', 'SystemSatisfies', 'SystemSatisfactionRequires')


class Relationship(PolymorphicModel):
    """A general relationship between functions and/or systems."""

    scenario = models.ForeignKey(Scenario, blank=True, null=True)
    scale = models.ForeignKey(WeightingScale, related_name='relationships',
                              help_text="The scale to use to assess this relationship.")
    notes = models.TextField(blank=True, help_text="Comments on the relationship.")

    def latest_votes(self):
        # TODO: if using PostgreSQL, use `distinct`: http://stackoverflow.com/questions/18433314
        # return self.votes.values('expert').annotate(cast_on=models.aggregates.Max('cast_on'))
        # return Vote.objects.filter(relationship=self).values('expert').latest('cast_on')
        return self.votes.values('expert').latest('cast_on')


class FunctionRequires(Relationship):
    """
    A relationship between a function that requires another.

    ..note::
        A function may require a series of functions to be satisfied, e.g., in order to successfully intercept an
        airborne threat, the ship must be able to find, fix, track, target, engage the threat and assess if the
        engagement was successful. Each one of those functions must be satisfied for the interception to be achieved.
        In this case the function is satisfied by a series of AND statements, e.g., in order to achieve this function,
        this function AND this other function have to be achieved.

    """

    requiring = models.ForeignKey(Function, related_name='+',
                                  help_text="The function that requires the other.")
    required = models.ForeignKey(Function, related_name='+',
                                 help_text="The function that is required.")

    class Meta:
        verbose_name_plural = 'Required Functions'

    def __str__(self):
        return "{} requires {}".format(self.requiring, self.required)


class FunctionSatisfies(Relationship):
    """
    A relationship between a function that satisfies another.

    ..note::
        A function may be satisfied by other functions, e.g., to detect an airborne threat, the AAW officer could
        receive a warning from a warning receiver (if the aircraft is targeting the ship), detect it with an active
        radar, or receive information from another sensor through a datalink. This corresponds to a series of OR
        statements for satisfying a function, e.g., this function can be satisfied by this function OR this other
        function.
    """
    satisfier = models.ForeignKey(Function, related_name='+',
                                  help_text="The function that satisfies the other.")
    satisfied = models.ForeignKey(Function, related_name='+',
                                  help_text="The function that is satisfied.")

    class Meta:
        verbose_name_plural = 'Functions Satisfied'

    def __str__(self):
        return "{} satisfies {}".format(self.satisfier, self.satisfied)


class SystemRequires(Relationship):
    """
    A relationship between a system that requires a function.

    ..note::
        A system may require a series of functions, e.g., an SM-2 may require a function called <Launch SM-2> and
        <Control SM-2>. As it was the case with a function requiring a series of functions, these statements allow
        for an AND aggregation of the functional requirements, e.g., in order for this system to be operational, this
        function AND this other function must be achieved.
    """
    requiring = models.ForeignKey(System, related_name='+',
                                  help_text="The system that requires the function.")
    required = models.ForeignKey(Function, related_name='+',
                                 help_text="The function that is required.")

    class Meta:
        verbose_name_plural = 'Required Functions'

    def __str__(self):
        return "{} requires {}".format(self.requiring, self.required)


class SystemSatisfies(Relationship):
    """
    A relationship between a system that satisfies a function.

    ..note::
        A system may satisfy functions, e.g., a radar may provide the function track airborne target. As it was the
        case with the functions being satisfied by other functions, this statement allows for an OR aggregation, e.g.,
        this function can be satisfied by this system OR this other system.

    ..note::
        A system performing a function may be incompatible with another system performing a function, e.g., a radar
        interfering with a satellite communication system, as reported[Brown, 1987] in the case of HMS Sheffield. The
        radar was not able to search for airborne threats while the SATCOM system was in use, at the same time, the
        SATCOM system could not receive data while the radar was emitting.
    """
    satisfier = models.ForeignKey(System, related_name='+',
                                  help_text="The system that satisfies the function.")
    satisfied = models.ForeignKey(Function, related_name='+',
                                  help_text="The function that is satisfied by the system.")
    incompatible = models.ManyToManyField('self', blank=True,
                                          help_text="Other system satisfying functions this one is incompatible with.")

    class Meta:
        verbose_name_plural = 'Functions Satisfied'

    def __str__(self):
        return "{} satisfies {}".format(self.satisfier, self.satisfied)


class SystemSatisfactionRequires(Relationship):
    """
    A relationship between a system satisfying relationship and a required function.

    ..note::
        A system performing a function may require a series of functions, e.g., a SAM with a semi-active seeker will
        require illumination in order to engage a target. The system may be able to perform other functions, but may
        be incapable of achieving a sub-set of possible functions if other functions are not achieved. This statement
        allows for an AND aggregation, e.g., in order for this system to perform the given function, this different
        function AND this other function must be achieved.

    """
    relationship = models.ForeignKey(SystemSatisfies, related_name='functions_required_by_system_satisfaction')
    required = models.ForeignKey(Function, related_name='required_relationship',
                                 help_text="The function that is required.")

    class Meta:
        verbose_name_plural = 'Required Functions'

    def __str__(self):
        return "{} required by {} while satisfying {}".format(self.required,
                                                              self.relationship.satisfier,
                                                              self.relationship.satisfied)
