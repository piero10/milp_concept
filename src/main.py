import pyomo.environ as pyo
import pandas as pd
import json
import os
from tabulate import tabulate

from src.task import Task
from src.machine import Machine


def load_data():
    with open(os.path.join("..", "data", "data.json"), 'r') as file:
        return json.load(file)


def build_model(data: dict):
    pp = data["planning_period"]
    tasks = [
        Task(
            id=d["id"],
            planning_period_start=pp['start'],
            reward=d["reward"],
            deadline=d["deadline"],
            length=d["duration"])
        for d in data["tasks"]
    ]

    machine = Machine(
        id="test_machine",
        planning_period_start=pp["start"],
        planning_period_end=pp["end"],
        tasks=tasks
    )

    return machine



if __name__ == "__main__":
    data = load_data()
    machine = build_model(data)

    machine.create_constraints()
    machine.create_objective()

    solver = pyo.SolverFactory("scip")
    solution = solver.solve(machine)

    print("Оптимизация станка:")
    print("Статус решения:  ", {solution.solver.termination_condition})
    print()

    print("Решение:  ", {solution.solver.termination_condition})
    arr = []
    for t in machine._tasks:
        if t.exists > 0.001:
            arr.append([t.id, t.start, t.end, t.length])
    df = pd.DataFrame(arr, columns=["ИД", "начало", "окончание", "продолжительность"])
    print(tabulate(df, headers=df.columns))
