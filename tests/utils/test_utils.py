import numpy as np

from utils.utils import node_to_job_and_task, job_and_task_to_node


def test_node_to_job_and_task():
    assert node_to_job_and_task(13, 5) == (2, 3)
    assert node_to_job_and_task(9, 5) == (1, 4)
    assert node_to_job_and_task(0, 1) == (0, 0)


def test_job_and_task_to_node():
    assert job_and_task_to_node(0, 4, 5) == 4
    assert job_and_task_to_node(5, 5, 6) == 35
    assert job_and_task_to_node(3, 2, 4) == 14
