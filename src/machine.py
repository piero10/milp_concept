import pyomo.environ as pyo
from pyomo.environ import *

from src.base_model import BaseModel
from src.task import Task, big_M


class Machine(BaseModel):
    """
    станок. выполняет задания из пула задач, максимизирует награду за выполнения заданий
    """

    def __init__(
        self,
        id,
        planning_period_start: float,
        planning_period_end: float,
        tasks: list[Task]
    ):
        """
        :param id: Имя модели
        :param planning_period_start: начало периодапланирования
        :param planning_period_end: окончание периода планирования
        :tasks: массив операций, кот надо выполнить на этом станке
        """
        super().__init__(id)

        self._planning_period_start = planning_period_start
        self._planning_period_end = planning_period_end

        self._tasks_dct = {t.id: t for t in tasks}
        self._tasks = tasks
        self._tasks_double_idx = [(t1.id, t2.id)  for t1 in tasks for t2 in tasks]

        self.d_pos = pyo.Var(self._tasks_double_idx, domain=pyo.NonNegativeReals)
        self.d_neg = pyo.Var(self._tasks_double_idx, domain=pyo.NonNegativeReals)
        self.y_pos = Var(self._tasks_double_idx, domain=pyo.Binary)
        self.add_sub_models(self._tasks)


    def create_constraints(self):
        """
        создаем огранияения модели
        """
        super().create_constraints()

        self.constr_no_tasks_overalapping()


    def constr_no_tasks_overalapping(self):
        """
        создаем огранияения на не пересечение операций
        """
        already_processed_idx = set()

        M = 100000  # Large enough to bound variables
        e = 1e-6

        for t1_idx, t1 in self._tasks_dct.items():
            for t2_idx, t2 in self._tasks_dct.items():
                if t1_idx == t2_idx:
                    continue

                if (t1_idx, t2_idx) in already_processed_idx or (t2_idx, t1_idx) in already_processed_idx:
                    continue

                already_processed_idx.add((t1_idx, t2_idx))

                self.add_component(
                    f"no_overlaping_1_{t1_idx}_{t2_idx}",
                    pyo.Constraint(expr=t1.middle_var - t2.middle_var == self.d_pos[t1_idx, t2_idx] - self.d_neg[t1_idx, t2_idx])
                )

                self.add_component(
                            f"no_overlaping_2_{t1}_{t2}",
                            pyo.Constraint(
                                expr=self.d_pos[t1_idx, t2_idx] + self.d_neg[t1_idx, t2_idx] >= t1._length_var / 2 + t2._length_var / 2 -
                                     (1 - t1._exists_var) * big_M -  (1 - t2._exists_var) * big_M
                            )
                        )

                self.add_component(
                    f"no_overlaping_3_{t1}_{t2}",
                    pyo.Constraint(expr=self.d_pos[t1_idx, t2_idx] >= e * self.y_pos[t1_idx, t2_idx]))

                self.add_component(
                    f"no_overlaping_4_{t1}_{t2}",
                    pyo.Constraint(expr=self.d_neg[t1_idx, t2_idx] <= M * (1 - self.y_pos[t1_idx, t2_idx])))

                self.add_component(
                    f"no_overlaping_5_{t1}_{t2}",
                    pyo.Constraint(expr=self.d_neg[t1_idx, t2_idx] >= e * (1 - self.y_pos[t1_idx, t2_idx])))

                self.add_component(
                    f"no_overlaping_6_{t1}_{t2}",
                    pyo.Constraint(expr=self.d_pos[t1_idx, t2_idx] <= M * self.y_pos[t1_idx, t2_idx]))


    def create_objective(self):
        """
        создаем целевую функцию
        """
        koeff = 0.1
        self.objective = pyo.Objective(
            expr=
            - sum(t.exists_var * t.reward for t in self._tasks)
            + koeff * sum(self.d_pos[idx] for idx in self._tasks_double_idx)
            + koeff * sum(self.d_neg[idx] for idx in self._tasks_double_idx),

        sense=pyo.minimize)


        return self.objective

