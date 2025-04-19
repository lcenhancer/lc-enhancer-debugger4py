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

import json
from abc import ABCMeta, abstractmethod
from inspect import isabstract
from typing import Mapping, Type, List, final, Any

from src.debugger4py.base import Strategizable, AssertUtil, ClassUtil, ModuleUtil, ContainerUtil, OrderUtil


class BaseOutputPrintStrategy(Strategizable, metaclass=ABCMeta):

    @abstractmethod
    def print_output(self, obj, strategies_map: Mapping[Type, List]) -> str:
        pass

    @final
    def accept(self, obj_type, obj, strategies_map) -> str:
        return self.print_output(obj, strategies_map)


class OutputPrinter(BaseOutputPrintStrategy):

    def __init__(self, printing_strategies: List[BaseOutputPrintStrategy]):
        printing_strategies.append(self)
        printing_strategies = [e for e in printing_strategies if e is not None]
        from collections import defaultdict
        groups = defaultdict(list)
        for printing_strategy in printing_strategies:
            groups[printing_strategy.get_acceptable_type()].append(printing_strategy)
        groups[self.get_object_type(Any)].append(self)
        for __type__ in groups:
            OrderUtil.desc_sort(groups[__type__])
        self.strategies = groups

    def get_acceptable_type(self) -> Type:
        return Any

    def get_order(self) -> int:
        return -1

    def print_output(self, obj: Any, strategies_map: Mapping[Type, List]) -> str:
        return json.dumps(obj)

    def print_object(self, obj: Any, obj_type: Type) -> str:
        strategy_set = self.find_strategies(obj if obj_type is None else obj_type, self.strategies)
        last_error = None
        for strategy in strategy_set:
            try:
                return strategy.accept(None, obj, self.strategies)
            except Exception as e:
                last_error = e
            finally:
                pass
        raise RuntimeError(f"Cannot printing output: {obj}", last_error)


class OutputPrinterFactory:

    @staticmethod
    def get_output_printer(enhancer) -> OutputPrinter:
        AssertUtil.non_null(enhancer, "The enhancer cannot be null.")
        builtin_strategy_classes = ClassUtil.get_classes_from_module(
            ModuleUtil.load_module_from_file("src.debugger4py.printer.builtin_strategy"),
            lambda cls:
            not isabstract(cls)
            and issubclass(cls, BaseOutputPrintStrategy)
        )
        builtin_strategies = ClassUtil.instantiate_classes(builtin_strategy_classes)
        custom_strategies = enhancer.get_output_print_strategies()
        if ContainerUtil.not_empty(custom_strategies):
            builtin_strategies.extend(custom_strategies)
        return OutputPrinter(builtin_strategies)


class OutputPrinterProcessor:

    @staticmethod
    def process(printer, output_obj, output_obj_type):
        AssertUtil.non_null(printer, "The printer cannot be null.")
        AssertUtil.is_true(isinstance(printer, OutputPrinter), "The printer is not a OutputPrinter.")
        return printer.print_object(output_obj, output_obj_type)
