import os

from paramtools import parameters


current_path = os.path.abspath(os.path.dirname(__file__))


class Baseball(parameters.Parameters):
    project_schema = os.path.join(current_path, "schema.json")
    baseline_parameters = os.path.join(current_path, "baseball.json")
