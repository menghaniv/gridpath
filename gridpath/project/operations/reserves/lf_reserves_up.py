#!/usr/bin/env python
# Copyright 2017 Blue Marble Analytics LLC. All rights reserved.

"""
Add project-level components for upward load-following reserves
"""

import csv
import os.path

from gridpath.project.operations.reserves.reserve_provision import \
    generic_determine_dynamic_components, generic_add_model_components, \
    generic_load_model_data, generic_export_module_specific_results

# Reserve-module variables
MODULE_NAME = "lf_reserves_up"
# Dynamic components
HEADROOM_OR_FOOTROOM_DICT_NAME = "headroom_variables"
# Inputs
BA_COLUMN_NAME_IN_INPUT_FILE = "lf_reserves_up_ba"
RESERVE_PROVISION_DERATE_COLUMN_NAME_IN_INPUT_FILE = "lf_reserves_up_derate"
RESERVE_BALANCING_AREAS_INPUT_FILE_NAME = \
    "load_following_up_balancing_areas.tab"
# Model components
RESERVE_PROVISION_VARIABLE_NAME = "Provide_LF_Reserves_Up_MW"
RESERVE_PROVISION_DERATE_PARAM_NAME = "lf_reserves_up_derate"
RESERVE_PROVISION_SUBHOURLY_ADJUSTMEN_PARAM_NAME = \
    "lf_reserves_up_provision_subhourly_energy_adjustment"
RESERVE_BALANCING_AREA_PARAM_NAME = "lf_reserves_up_zone"
RESERVE_PROJECTS_SET_NAME = "LF_RESERVES_UP_PROJECTS"
RESERVE_BALANCING_AREAS_SET_NAME = "LF_RESERVES_UP_ZONES"
RESERVE_PROJECT_OPERATIONAL_TIMEPOINTS_SET_NAME = \
    "LF_RESERVES_UP_PROJECT_OPERATIONAL_TIMEPOINTS"


def determine_dynamic_components(d, scenario_directory, horizon, stage):
    """

    :param d:
    :param scenario_directory:
    :param horizon:
    :param stage:
    :return:
    """

    generic_determine_dynamic_components(
        d=d,
        scenario_directory=scenario_directory,
        horizon=horizon,
        stage=stage,
        reserve_module=MODULE_NAME,
        headroom_or_footroom_dict=HEADROOM_OR_FOOTROOM_DICT_NAME,
        ba_column_name=BA_COLUMN_NAME_IN_INPUT_FILE,
        reserve_provision_variable_name=RESERVE_PROVISION_VARIABLE_NAME,
        reserve_provision_derate_param_name=
        RESERVE_PROVISION_DERATE_PARAM_NAME,
        reserve_provision_subhourly_adjustment_param_name=
        RESERVE_PROVISION_SUBHOURLY_ADJUSTMEN_PARAM_NAME,
        reserve_balancing_area_param_name=RESERVE_BALANCING_AREA_PARAM_NAME
    )


def add_model_components(m, d):
    """

    :param m:
    :param d:
    :return:
    """

    generic_add_model_components(
        m=m,
        d=d,
        reserve_projects_set=RESERVE_PROJECTS_SET_NAME,
        reserve_balancing_area_param=RESERVE_BALANCING_AREA_PARAM_NAME,
        reserve_provision_derate_param=RESERVE_PROVISION_DERATE_PARAM_NAME,
        reserve_balancing_areas_set=RESERVE_BALANCING_AREAS_SET_NAME,
        reserve_project_operational_timepoints_set=
        RESERVE_PROJECT_OPERATIONAL_TIMEPOINTS_SET_NAME,
        reserve_provision_variable_name=RESERVE_PROVISION_VARIABLE_NAME,
        reserve_provision_subhourly_adjustment_param=
        RESERVE_PROVISION_SUBHOURLY_ADJUSTMEN_PARAM_NAME
    )


def load_model_data(m, d, data_portal, scenario_directory, horizon, stage):
    """

    :param m:
    :param d:
    :param data_portal:
    :param scenario_directory:
    :param horizon:
    :param stage:
    :return:
    """
    generic_load_model_data(
        m=m,
        d=d,
        data_portal=data_portal,
        scenario_directory=scenario_directory,
        horizon=horizon,
        stage=stage,
        ba_column_name=BA_COLUMN_NAME_IN_INPUT_FILE,
        derate_column_name=
        RESERVE_PROVISION_DERATE_COLUMN_NAME_IN_INPUT_FILE,
        reserve_balancing_area_param=RESERVE_BALANCING_AREA_PARAM_NAME,
        reserve_provision_derate_param=RESERVE_PROVISION_DERATE_PARAM_NAME,
        reserve_projects_set=RESERVE_PROJECTS_SET_NAME,
        reserve_provision_subhourly_adjustment_param
        =RESERVE_PROVISION_SUBHOURLY_ADJUSTMEN_PARAM_NAME,
        reserve_balancing_areas_input_file
        =RESERVE_BALANCING_AREAS_INPUT_FILE_NAME
    )


def export_results(scenario_directory, horizon, stage, m, d):
    """
    Export project-level results for upward load-following
    :param scenario_directory:
    :param horizon:
    :param stage:
    :param m:
    :param d:
    :return:
    """

    generic_export_module_specific_results(
        m=m,
        d=d,
        scenario_directory=scenario_directory,
        horizon=horizon,
        stage=stage,
        module_name=MODULE_NAME,
        reserve_project_operational_timepoints_set=
        RESERVE_PROJECT_OPERATIONAL_TIMEPOINTS_SET_NAME,
        reserve_provision_variable_name=RESERVE_PROVISION_VARIABLE_NAME
    )


def get_inputs_from_database(subscenarios, c, inputs_directory):
    """

    :param subscenarios
    :param c:
    :param inputs_directory:
    :return:
    """

    project_bas = c.execute(
        """SELECT project, lf_reserves_up_ba
        FROM inputs_project_lf_reserves_up_bas
            WHERE lf_reserves_up_ba_scenario_id = {}
            AND project_lf_reserves_up_ba_scenario_id = {}""".format(
            subscenarios.LF_RESERVES_UP_BA_SCENARIO_ID,
            subscenarios.PROJECT_LF_RESERVES_UP_BA_SCENARIO_ID
        )
    ).fetchall()

    # Make a dict for easy access
    prj_ba_dict = dict()
    for (prj, ba) in project_bas:
        prj_ba_dict[str(prj)] = "." if ba is None else str(ba)

    with open(os.path.join(inputs_directory, "projects.tab"), "r"
              ) as projects_file_in:
        reader = csv.reader(projects_file_in, delimiter="\t")

        new_rows = list()

        # Append column header
        header = reader.next()
        header.append("lf_reserves_up_ba")
        new_rows.append(header)

        # Append correct values
        for row in reader:
            # If project specified, check if BA specified or not
            if row[0] in prj_ba_dict.keys():
                row.append(prj_ba_dict[row[0]])
                new_rows.append(row)
            # If project not specified, specify no BA
            else:
                row.append(".")
                new_rows.append(row)

    with open(os.path.join(inputs_directory, "projects.tab"), "w") as \
            projects_file_out:
        writer = csv.writer(projects_file_out, delimiter="\t")
        writer.writerows(new_rows)