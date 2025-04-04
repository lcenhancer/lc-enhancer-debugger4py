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

from abc import abstractmethod, ABCMeta
from typing import Generic, TypeVar, Type, Any, Mapping, Set

from src.base.interfaces.order import Order

AcceptableType = TypeVar('AcceptableType')
Strategy = TypeVar('Strategy')
Output = TypeVar('Output')


class Strategizable(Generic[AcceptableType, Strategy, Output], Order, metaclass=ABCMeta):

    @abstractmethod
    def get_acceptable_type(self) -> Type[AcceptableType]:
        pass

    @classmethod
    def get_object_type(cls, obj: Any) -> Type:
        if obj is None:
            return type(None)
        if isinstance(obj, type):
            return obj
        return type(obj)

    @classmethod
    def find_strategy_set(cls, obj: Any, strategies_map: Mapping[Type, Set[Strategy]]) -> Set[Strategy]:
        strategy_set = strategies_map.get(cls.get_object_type(obj), strategies_map.get(type(None), None))
        if not strategy_set:
            raise RuntimeError(f"Cannot find any appropriate accepted strategy set for the object: {obj}")
        return strategy_set

    @abstractmethod
    def accept(self, obj_type: Type, obj: Any, strategies_map: Mapping[Type, Set[Strategy]]) -> Output:
        pass
