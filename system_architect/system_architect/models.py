from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from polymorphic.models import PolymorphicModel
from uuid import uuid4


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
                                           related_name='super_scenario',
                                           help_text="Scenarios that refine this one.")


class Category(CoreModel):
    kind = models.PositiveSmallIntegerField(choices=((0, 'Functions'),
                                                     (1, 'Systems'),
                                                     (2, 'Both')), blank=False, null=False)

    class Meta:
        verbose_name_plural = 'categories'


class WeightingScale(CoreModel):
    def add_level(self, name, value):
        WeightLevel.objects.create(name=name, value=value, scale=self)

    def __str__(self):
        return "<Scale: {}>".format(self.name)


class WeightLevel(models.Model):
    scale = models.ForeignKey(WeightingScale, related_name='levels', help_text="The scale that owns this level.")
    name = models.CharField(max_length=32, help_text="")
    value = models.FloatField(help_text="The numerical value of this level.")

    class Meta:
        ordering = ['scale', '-value']

    def __str__(self):
        return "<{} Scale: {} Value>".format(self.scale.name, self.name)


class Function(CoreModel):
    categories = models.ManyToManyField(Category, blank=True)
    required_functions = models.ManyToManyField('self', blank=True, symmetrical=False,
                                                related_name='required_by', through='FunctionalRequirement',
                                                through_fields=('requiring', 'required'),
                                                help_text="The functions this function requires.")
    satisfies = models.ManyToManyField('self', blank=True, symmetrical=False,
                                       related_name='satisfied_by_functions', through='FunctionalSatisfaction',
                                       through_fields=('satisfier', 'satisfied'),
                                       help_text="The functions this function satisfies.")


class System(CoreModel):
    categories = models.ManyToManyField(Category, blank=True)
    satisfies = models.ManyToManyField(Function, blank=True, symmetrical=False,
                                       related_name='satisfied_by_systems', through='SystemSatisfaction',
                                       through_fields=('satisfier', 'satisfied'),
                                       help_text="The functions this function satisfies.")


class Relationship(PolymorphicModel):
    scenario = models.ForeignKey(Scenario, blank=True, null=True)
    scale = models.ForeignKey(WeightingScale, related_name='relationships',
                              help_text="The scale to use to assess this relationship.")
    notes = models.TextField(blank=True, help_text="Comments on the relationship.")

    def latest_votes(self):
        # TODO: if using PostgreSQL, use distinct: http://stackoverflow.com/questions/18433314
        # return self.votes.values('expert').annotate(cast_on=models.aggregates.Max('cast_on'))
        return self.votes.values('expert').latest('cast_on')


class FunctionalRequirement(Relationship):
    requiring = models.ForeignKey(Function, related_name='requiring_relationship',
                                  help_text="The function that requires the other.")
    required = models.ForeignKey(Function, related_name='required_relationship',
                                 help_text="The function that is required.")

    def __str__(self):
        return "{} requires {}".format(self.requiring, self.required)


class FunctionalSatisfaction(Relationship):
    source = 'satisfier'
    target = 'satisfied'
    satisfier = models.ForeignKey(Function, related_name='satisfying_relationship',
                                  help_text="The function that satisfies the other.")
    satisfied = models.ForeignKey(Function, related_name='satisfied_functional_relationship',
                                  help_text="The function that is satisfied.")

    def __str__(self):
        return "{} satisfies {}".format(self.satisfier, self.satisfied)



class SystemSatisfaction(Relationship):
    source = 'satisfier'
    target = 'satisfied'
    satisfier = models.ForeignKey(System, related_name='satisfying_relationship',
                                  help_text="The system that satisfies the function.")
    satisfied = models.ForeignKey(Function, related_name='satisfied_system_relationship',
                                  help_text="The function that is satisfied by the system.")

    def __str__(self):
        return "{} satisfies {}".format(self.satisfier, self.satisfied)


class Organization(CoreModel):
    pass


class ExpertProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=128, blank=True)
    organization = models.ForeignKey(Organization, blank=True, null=True, related_name='personnel')
    phone = models.CharField(max_length=32)

    def __str__(self):
        return str(self.user)


@receiver(models.signals.post_save, sender=User)
def create_expert_profile(sender, instance, created, **kwargs):
    if created:
        ExpertProfile.objects.create(user=instance)


@receiver(models.signals.post_save, sender=User)
def save_expert_profile(sender, instance, **kwargs):
    instance.expertprofile.save()


class Vote(models.Model):
    relationship = models.ForeignKey(Relationship)
    expert = models.ForeignKey(ExpertProfile, blank=True, null=True,
                               help_text="The subject matter expert that provided this input.")
    comments = models.TextField(blank=True, help_text="Notes the user can use to explain their vote.")
    value = models.ForeignKey(WeightLevel, help_text="The value of the vote.")
    cast_on = models.DateTimeField(auto_now=True, help_text="When this vote was cast")
    confidence = models.PositiveSmallIntegerField(choices=((0, 'High'),
                                                           (1, 'Moderate'),
                                                           (2, 'Low')), default=0,
                                                  help_text="The confidence the SME has on their vote.")

    class Meta:
        indexes = [
            models.Index(fields=['relationship', 'expert', '-cast_on']),
        ]
