from typing import Iterable

import pyomo.environ as pyo


class BaseModel(pyo.ConcreteModel):
    """базовый класс модели."""

    def __init__(self, id: str = "", description: str=""):
        super().__init__(id)
        self._id = id
        self._description = description # это поле будем собирать и строить википедию объектов
        self._sub_models = []

    @property
    def id(self):
        return self._id

    def add_sub_model(self, name, sub_model):
        self.add_component(name, sub_model)
        self._sub_models.append(sub_model)

    def add_sub_models(self, sub_models: Iterable):
        [self.add_sub_model(sub_model.name, sub_model) for sub_model in sub_models]

    def _create_constraints(self):
        for mod in self._sub_models:
            mod.create_constraints()

    def create_constraints(self):
        self._create_constraints()
        # + собственные ограничения этой модели

    def _create_objective(self):
        if len(self._sub_models) > 0:
            obj = sum(sub_model.create_objective() for sub_model in self._sub_models)
            return obj

        return 0

    def create_objective(self):
        obj = self._create_objective()
        # + собственная цель этой модели
        return obj
