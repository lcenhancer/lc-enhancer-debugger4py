"""

Copyright (C) 2025-2030 LcEnhancer(https://github.com/lcenhancer).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

from abc import ABCMeta, abstractmethod
from typing import Type, List, Any

from src.debugger4py.base_lib.util_lib import AssertUtil


class Order(metaclass=ABCMeta):
    @abstractmethod
    def get_order(self) -> int: pass


class Closable(metaclass=ABCMeta):
    @abstractmethod
    def close(self): pass


class Strategizable(Order, metaclass=ABCMeta):
    @abstractmethod
    def get_acceptable_type(self) -> Type:
        pass

    @classmethod
    def get_object_type(cls, obj) -> Type:
        if obj is None:
            return type(None)
        if isinstance(obj, type):
            return obj
        return type(obj)

    @classmethod
    def find_strategies(cls, obj, strategies_map) -> List:
        strategies = strategies_map.get(cls.get_object_type(obj), strategies_map.get(cls.get_object_type(Any), None))
        AssertUtil.not_empty(strategies, f"Cannot find any appropriate accepted strategy for the object: {obj}")
        return strategies

    @abstractmethod
    def accept(self, obj_type: Type, obj, strategies_map):
        pass
