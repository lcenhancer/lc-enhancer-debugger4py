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

import inspect
import sys
from abc import ABCMeta
from typing import List

from src.debugger4py.base import Order, AssertUtil


class Pipeline(Order, metaclass=ABCMeta):

    def __init__(self):
        self.delegate = None

    def get_enhancer(self):
        AssertUtil.non_null(self.delegate, "The delegate in this pipeline is null.")
        return self.delegate.get_enhancer()

    def get_input_provider(self):
        AssertUtil.non_null(self.delegate, "The delegate in this pipeline is null.")
        return self.delegate.get_input_provider()

    def get_output_consumer(self):
        AssertUtil.non_null(self.delegate, "The delegate in this pipeline is null.")
        return self.delegate.get_output_consumer()

    def get_output_printer(self):
        AssertUtil.non_null(self.delegate, "The delegate in this pipeline is null.")
        return self.delegate.get_output_printer()

    def get_leetcode_executor(self):
        AssertUtil.non_null(self.delegate, "The delegate in this pipeline is null.")
        return self.delegate.get_leetcode_executor()

    def get_input_parser(self):
        AssertUtil.non_null(self.delegate, "The delegate in this pipeline is null.")
        return self.delegate.get_input_parser()

    def set_delegate(self, delegate):
        from src.debugger4py.base import AssertUtil
        AssertUtil.non_null(delegate, "The delegate cannot be null.")
        AssertUtil.is_true(isinstance(delegate, Pipeline), "The delegate is not a Pipeline instance.")
        self.delegate = delegate


class DataStructureDesignScenePipeline(Pipeline):

    def get_order(self) -> int:
        return 0

    def __pipeline_entry_point__(self, operations: List[str], data: List[List]) -> List:
        AssertUtil.not_empty(operations, "The operation list cannot be empty.")
        AssertUtil.not_empty(data, "The data list cannot be empty.")
        AssertUtil.is_true(len(operations) == len(data), "The size of lists operation and data is not equal.")
        data_structure_type = self.get_leetcode_executor().get_instance()
        AssertUtil.non_null(data_structure_type, "The data structure type cannot be null.")
        AssertUtil.is_true(isinstance(data_structure_type, type),
                           "The instance of the leetcode_executor in this pipeline is not a data structure type"
                           )
        data_structure_func = inspect.getmembers(
            data_structure_type,
            predicate=lambda m: (inspect.isfunction(m) or inspect.ismethod(m))
        )
        from src.debugger4py.executor import LeetcodeInvokerFactory
        data_structure_invokers = [LeetcodeInvokerFactory.get_leetcode_invoker(func[1], sys.maxsize) for func in
                                   data_structure_func]
        invokers_mapping = {}
        for invoker in data_structure_invokers:
            invokers_mapping.setdefault(invoker.get_invoker_name(), []).append(invoker)

        from src.debugger4py.executor import LeetcodeExecutorFactory
        from src.debugger4py.parser_lib import InputParserProcessor
        from src.debugger4py.executor import LeetcodeExecutorProcessor
        data_structure_instance = None
        invoker_return_collector = []
        for idx in range(len(operations)):
            operation = operations[idx]
            operation_input = data[idx]
            AssertUtil.is_true(operation in invokers_mapping,
                               f"Cannot find any candidate leetcode invoker by operation: {operation}"
                               )
            leetcode_executor = LeetcodeExecutorFactory.get_leetcode_executor(
                data_structure_type if idx == 0 else data_structure_instance,
                *invokers_mapping[operation])
            input_object = InputParserProcessor.process(self.get_input_parser(), leetcode_executor, operation_input)
            output_object = LeetcodeExecutorProcessor.process(leetcode_executor, input_object)
            if idx == 0:
                data_structure_instance = output_object
                invoker_return_collector.append(None)
            else:
                invoker_return_collector.append(output_object)

        return invoker_return_collector
