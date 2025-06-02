from multiprocessing.spawn import set_executable

import numpy as np
import pyomo.environ as pyo

from src.base_model import BaseModel

big_M = 10e7

class Task(BaseModel):
    """Задание"""

    def __init__(self, id, planning_period_start, deadline, length, reward):
        """
        :param name: ИД задания
        :param planning_period_start: начало периодапланирования
        :param planning_period_end: окончание периода планирования
        :tasks: массив операций, кот надо выполнить на этом станке
        """
        super().__init__(id)

        self._start_var = pyo.Var(bounds=(planning_period_start, deadline), domain=pyo.NonNegativeReals)
        self._end_var = pyo.Var(bounds=(planning_period_start, deadline), domain=pyo.NonNegativeReals)
        self._middle_var = pyo.Var(bounds=(planning_period_start, deadline), domain=pyo.NonNegativeReals)
        self._length_var = pyo.Var(bounds=(0, length), domain=pyo.NonNegativeReals)
        self._length = length
        self._exists_var = pyo.Var(domain=pyo.Binary)
        self.reward = reward

    def create_constraints(self):
        super().create_constraints()
        # связываем переменную длинны с переменной существования операции
        self.add_component("c1", pyo.Constraint(expr=self._end_var == self._start_var + self._exists_var * self._length))

        # создаем пер центр операции
        self.add_component("c2", pyo.Constraint(expr=self._middle_var == (self._start_var + self._end_var) / 2))

        # создаем пер длинна операции
        self.add_component("c3", pyo.Constraint(expr=self._length_var == self._end_var - self._start_var))

    def create_objective(self):
        #obj = super().create_objective()
        return 0

    @property
    def start(self):
        return self._start_var.value

    @property
    def end(self):
        return self._end_var.value

    @property
    def length(self):
        try:
            return self._end_var.value - self._start_var.value
        except:
            return  0

    @property
    def exists(self):
        return self._exists_var.value


    @property
    def middle_var(self):
        return self._middle_var

    @property
    def exists_var(self):
        return self._exists_var