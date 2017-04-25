from django import forms
from django.contrib import admin

from .models import (Category, Function, FunctionalRequirement, FunctionalSatisfaction, Scenario,
                     System, SystemSatisfaction, Vote, WeightLevel, WeightingScale)


class FunctionalRequirementInline(admin.TabularInline):
    model = FunctionalRequirement
    fields = ['required', 'scenario', 'notes', 'scale']
    fk_name = 'requiring'
    extra = 0


class FunctionalSatisfactionInline(admin.TabularInline):
    model = FunctionalSatisfaction
    fields = ['satisfied', 'scenario', 'notes', 'scale']
    fk_name = 'satisfier'
    extra = 0


@admin.register(Function)
class FunctionAdmin(admin.ModelAdmin):
    model = Function
    inlines = [FunctionalRequirementInline, FunctionalSatisfactionInline]


class SystemSatisfactionInline(admin.TabularInline):
    model = SystemSatisfaction
    fields = ['satisfied', 'scenario', 'notes', 'scale']
    fk_name = 'satisfier'
    extra = 0


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    model = System
    inlines = [SystemSatisfactionInline]


class WeightLevelInline(admin.TabularInline):
    model = WeightLevel
    fields = ['name', 'value']
    fk_name = 'scale'
    extra = 0


@admin.register(WeightingScale)
class WeightingScaleAdmin(admin.ModelAdmin):
    model = WeightingScale
    inlines = [WeightLevelInline]


def vote_form_factory(vote):
    class VoteForm(forms.ModelForm):
        value = forms.ModelChoiceField(
            queryset=WeightLevel.objects.filter(relationships=vote.relationship)
        )
    return VoteForm


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if obj is not None and obj.type is not None:
            kwargs['form'] = vote_form_factory(obj.type)
        return super().get_form(request, obj, **kwargs)


admin.site.register(Category)
admin.site.register(Scenario)
