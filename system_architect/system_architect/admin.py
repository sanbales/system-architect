from django import forms
from django.contrib import admin
from nested_admin.nested import NestedModelAdmin, NestedTabularInline

from .models import (Category, Function, FunctionRequires, FunctionSatisfies, Goal, Project, Scenario, System,
                     SystemRequires, SystemSatisfies, SystemSatisfactionRequires, Term, Vote, WeightLevel,
                     WeightingScale)


class FunctionRequiresInline(NestedTabularInline):
    model = FunctionRequires
    fields = ['required', 'scenario', 'notes', 'scale']
    fk_name = 'requiring'
    extra = 0


class FunctionSatisfiesInline(NestedTabularInline):
    model = FunctionSatisfies
    fields = ['satisfied', 'scenario', 'notes', 'scale']
    fk_name = 'satisfier'
    extra = 0


class FunctionInline(NestedTabularInline):
    model = Function
    inlines = [FunctionRequiresInline, FunctionSatisfiesInline]
    extra = 0


@admin.register(Function)
class FunctionAdmin(NestedModelAdmin):
    model = Function
    inlines = [FunctionRequiresInline, FunctionSatisfiesInline]


class SystemRequiresInline(NestedTabularInline):
    model = SystemRequires
    fields = ['required', 'scenario', 'notes', 'scale']
    fk_name = 'requiring'
    extra = 0


class SystemSatisfactionRequiresInline(NestedTabularInline):
    model = SystemSatisfactionRequires
    fields = ['required', 'scenario', 'notes', 'scale']
    fk_name = 'relationship'
    extra = 0


class SystemSatisfiesInline(NestedTabularInline):
    model = SystemSatisfies
    fields = ['satisfied', 'scenario', 'notes', 'scale']
    inlines = [SystemSatisfactionRequiresInline]
    fk_name = 'satisfier'
    extra = 0


class SystemInline(NestedTabularInline):
    model = System
    inlines = [SystemRequiresInline, SystemSatisfiesInline]
    extra = 0


@admin.register(System)
class SystemAdmin(NestedModelAdmin):
    model = System
    inlines = [SystemRequiresInline, SystemSatisfiesInline]


# @admin.register(SystemSatisfies)
# class SystemSatisfiesAdmin(NestedModelAdmin):
#     model = SystemSatisfies
#     inlines = [SystemSatisfactionRequiresInline]


class WeightLevelInline(NestedTabularInline):
    model = WeightLevel
    fields = ['name', 'value']
    fk_name = 'scale'
    extra = 0


@admin.register(WeightingScale)
class WeightingScaleAdmin(NestedModelAdmin):
    model = WeightingScale
    inlines = [WeightLevelInline]


def vote_form_factory(vote):
    class VoteForm(forms.ModelForm):
        value = forms.ModelChoiceField(
            queryset=WeightLevel.objects.filter(relationships=vote.relationship)
        )
    return VoteForm


@admin.register(Vote)
class VoteAdmin(NestedModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if obj is not None and obj.type is not None:
            kwargs['form'] = vote_form_factory(obj.type)
        return super().get_form(request, obj, **kwargs)


class GoalInline(NestedTabularInline):
    model = Goal
    fields = ['name', 'description']
    extra = 0


@admin.register(Project)
class ProjectAdmin(NestedModelAdmin):
    model = Project
    fields = ['name', 'description', 'glossary']
    inlines = [GoalInline, FunctionInline, SystemInline]


admin.site.register(Category)
admin.site.register(Scenario)
admin.site.register(Term)
