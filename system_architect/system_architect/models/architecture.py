#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.db import models
from logging import getLogger
from .core import CoreModel, Project, System


__all__ = ('SystemArchitecture',)


logger = getLogger(__name__)


class SystemArchitecture(CoreModel):
    """
    A conglomeration of systems that can be functionally assessed.

    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        help_text="The project this architecture belongs to.",
    )
    systems = models.ManyToManyField(
        System,
        help_text="The systems included in this architecture.",
    )

    @property
    def functional_satisfaction(self):
        satisfaction = {}

        if not self.systems:
            return satisfaction

        for function in self.project.functions:
            satisfaction[function] = 0.0

        return satisfaction


latest_fun_req_mappings = """
SELECT mapping_fun_req.requiring_function_id, mapping_fun_req.required_function_id, mapping_fun_req.scenario_id, mapping_fun_req.expert_id, Max(mapping_fun_req.Time) AS latest_vote_time
FROM mapping_fun_req
GROUP BY mapping_fun_req.requiring_function_id, mapping_fun_req.required_function_id, mapping_fun_req.scenario_id, mapping_fun_req.expert_id;
"""

latest_fun_sat_mappings = """
SELECT mapping_fun_sat.satisfying_function_id, mapping_fun_sat.satisfied_function_id, mapping_fun_sat.scenario_id, mapping_fun_sat.expert_id, Max(mapping_fun_sat.time) AS latest_vote_time
FROM mapping_fun_sat
GROUP BY mapping_fun_sat.satisfying_function_id, mapping_fun_sat.satisfied_function_id, mapping_fun_sat.scenario_id, mapping_fun_sat.expert_id;
"""

latest_sys_req_mappings = """
SELECT mapping_sys_req.system_id, mapping_sys_req.performing_function_id, mapping_sys_req.requires_function_id, mapping_sys_req.scenario_id, mapping_sys_req.expert_id, Max(mapping_sys_req.Time) AS latest_vote_time
FROM mapping_sys_req
GROUP BY mapping_sys_req.system_id, mapping_sys_req.performing_function_id, mapping_sys_req.requires_function_id, mapping_sys_req.scenario_id, mapping_sys_req.expert_id;
"""

latest_sys_sat_mappings = """
SELECT mapping_sys_sat.system_id, mapping_sys_sat.function_id, mapping_sys_sat.scenario_id, mapping_sys_sat.expert_id, Max(mapping_sys_sat.Time) AS latest_vote_time
FROM mapping_sys_sat
GROUP BY mapping_sys_sat.system_id, mapping_sys_sat.function_id, mapping_sys_sat.scenario_id, mapping_sys_sat.expert_id;
"""

confidence_fun_req = """
SELECT latest_fun_req_mappings.requiring_function_id, latest_fun_req_mappings.required_function_id, latest_fun_req_mappings.scenario_id, Sum(mapping_fun_req.confidence) AS sum_of_confidence
FROM mapping_fun_req INNER JOIN latest_fun_req_mappings ON (mapping_fun_req.time = latest_fun_req_mappings.latest_vote_time) AND (mapping_fun_req.expert_id = latest_fun_req_mappings.expert_id) AND (mapping_fun_req.scenario_id = latest_fun_req_mappings.scenario_id) AND (mapping_fun_req.required_function_id = latest_fun_req_mappings.required_function_id) AND (mapping_fun_req.requiring_function_id = latest_fun_req_mappings.requiring_function_id)
GROUP BY latest_fun_req_mappings.requiring_function_id, latest_fun_req_mappings.required_function_id, latest_fun_req_mappings.scenario_id;
"""

confidence_fun_sat = """
SELECT latest_fun_sat_mappings.satisfying_function_id, latest_fun_sat_mappings.satisfied_function_id, latest_fun_sat_mappings.scenario_id, Sum(mapping_fun_sat.confidence) AS sum_of_confidence
FROM latest_fun_sat_mappings INNER JOIN mapping_fun_sat ON (latest_fun_sat_mappings.satisfying_function_id = mapping_fun_sat.satisfying_function_id) AND (latest_fun_sat_mappings.satisfied_function_id = mapping_fun_sat.satisfied_function_id) AND (latest_fun_sat_mappings.scenario_id = mapping_fun_sat.scenario_id) AND (latest_fun_sat_mappings.expert_id = mapping_fun_sat.expert_id) AND (latest_fun_sat_mappings.latest_vote_time = mapping_fun_sat.time)
GROUP BY latest_fun_sat_mappings.satisfying_function_id, latest_fun_sat_mappings.satisfied_function_id, latest_fun_sat_mappings.scenario_id;
"""

confidence_sys_req = """
SELECT latest_sys_req_mappings.system_id, latest_sys_req_mappings.performing_function_id, latest_sys_req_mappings.requires_function_id, latest_sys_req_mappings.scenario_id
FROM latest_sys_req_mappings INNER JOIN mapping_sys_req ON (latest_sys_req_mappings.system_id=mapping_sys_req.system_id) AND (latest_sys_req_mappings.performing_function_id=mapping_sys_req.performing_function_id) AND (latest_sys_req_mappings.requires_function_id=mapping_sys_req.requires_function_id) AND (latest_sys_req_mappings.scenario_id=mapping_sys_req.scenario_id) AND (latest_sys_req_mappings.expert_id=mapping_sys_req.expert_id) AND (latest_sys_req_mappings.latest_vote_time=mapping_sys_req.time);
"""

functional_shortfall = """
SELECT functions.ID, Max([functional_requirement].[requirement]*(1-[functions_1].[level_satisfied])) AS shortfall
FROM functions AS functions_1 INNER JOIN (functions INNER JOIN functional_requirement ON functions.ID = functional_requirement.requiring_function_id) ON functions_1.ID = functional_requirement.required_function_id
GROUP BY functions.ID;
"""
