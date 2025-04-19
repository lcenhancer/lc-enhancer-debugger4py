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

from inspect import isabstract

from src.debugger4py.base import AssertUtil, ClassUtil, ModuleUtil
from src.debugger4py.executor import LeetcodeExecutorFactory, LeetcodeExecutorProcessor, LeetcodeInvokerFactory
from src.debugger4py.parser_lib import InputParserProcessor
from src.debugger4py.printer import OutputPrinterProcessor
from .builtin_pipeline import Pipeline


class BootstrapPipeline(Pipeline):

    def __init__(self,
                 enhancer,
                 input_provider,
                 output_consumer,
                 output_printer,
                 leetcode_executor,
                 input_parser
                 ):
        AssertUtil.non_null(enhancer, "The enhancer cannot be null.")
        self.enhancer = enhancer
        AssertUtil.non_null(input_provider, "The input provider cannot be null.")
        self.input_provider = input_provider
        AssertUtil.non_null(output_consumer, "The output consumer cannot be null.")
        self.output_consumer = output_consumer
        AssertUtil.non_null(output_printer, "The output printer cannot be null.")
        self.output_printer = output_printer
        AssertUtil.non_null(leetcode_executor, "The leetcode executor cannot be null.")
        self.leetcode_executor = leetcode_executor
        AssertUtil.non_null(input_parser, "The input parser cannot be null.")
        self.input_parser = input_parser
        self.pipeline_runners_mapping = {}
        self.pipeline_runners_invokers = []
        builtin_pipeline_classes = ClassUtil.get_classes_from_module(
            ModuleUtil.load_module_from_file("src.debugger4py.pipeline.builtin_pipeline"),
            lambda cls:
            not isabstract(cls)
            and issubclass(cls, Pipeline)
        )
        builtin_pipelines = ClassUtil.instantiate_classes(builtin_pipeline_classes)
        import inspect
        for builtin_pipeline in builtin_pipelines:
            pipeline_entries = inspect.getmembers(
                type(builtin_pipeline),
                predicate=lambda x: (inspect.isfunction(x) or inspect.ismethod(
                    x)) and x.__name__ == '__pipeline_entry_point__'
            )
            pipeline_entry_invokers = [LeetcodeInvokerFactory.get_leetcode_invoker(pipeline_entry[1], -2147483648) for
                                       pipeline_entry in pipeline_entries]
            self.pipeline_runners_invokers.extend(pipeline_entry_invokers)
            for pipeline_entry_invoker in pipeline_entry_invokers:
                self.pipeline_runners_mapping[pipeline_entry_invoker.get_id()] = builtin_pipeline

    def run(self):
        while True:
            input_str = self.input_provider.provide_next_input()
            if self.input_provider.is_end(input_str):
                break
            boss_leetcode_executor = LeetcodeExecutorFactory.copy_by_leetcode_executor(self.leetcode_executor)
            boss_leetcode_executor = self.__do_enhance_before_input_parse_process__(boss_leetcode_executor)
            input_parse_object = InputParserProcessor.process(self.input_parser, boss_leetcode_executor, input_str)
            boss_leetcode_executor = self.__do_enhance_before_after_parse_process__(boss_leetcode_executor)
            executor_output_object = LeetcodeExecutorProcessor.process(boss_leetcode_executor, input_parse_object)
            output_str = OutputPrinterProcessor.process(
                self.output_printer,
                executor_output_object,
                boss_leetcode_executor.get_return_type()
            )
            self.output_consumer.consume_next_output(output_str)

    def __do_enhance_before_input_parse_process__(self, boss_leetcode_executor):
        candidate_invokers = boss_leetcode_executor.get_candidate_invokers()
        if candidate_invokers is not None:
            candidate_invokers.extend(self.pipeline_runners_invokers)
        return boss_leetcode_executor

    def __do_enhance_before_after_parse_process__(self, boss_leetcode_executor):
        self.create_leetcode_instance_if_necessary(boss_leetcode_executor)
        leetcode_invoker = boss_leetcode_executor.get_executor()
        if leetcode_invoker.get_id() not in self.pipeline_runners_mapping:
            return boss_leetcode_executor
        selected_pipeline_runner_instance = self.pipeline_runners_mapping[leetcode_invoker.get_id()]
        selected_pipeline_runner_instance.set_delegate(self)
        boss_leetcode_executor.set_executor(None)
        return LeetcodeExecutorFactory.get_leetcode_executor(
            selected_pipeline_runner_instance,
            leetcode_invoker
        )

    @classmethod
    def create_leetcode_instance_if_necessary(cls, boss_leetcode_executor):
        leetcode_instance = boss_leetcode_executor.get_instance()
        if not isinstance(leetcode_instance, type):
            return
        from src.debugger4py.enhancer_lib import LeetcodePythonDebugEnhancer
        if issubclass(leetcode_instance, LeetcodePythonDebugEnhancer):
            return
        from inspect import isabstract
        if isabstract(leetcode_instance):
            return
        if leetcode_instance.__name__.find("Solution") == -1:
            return
        leetcode_invoker = boss_leetcode_executor.get_executor()
        if not leetcode_invoker.is_suitable(leetcode_instance):
            return
        boss_leetcode_executor.set_instance(leetcode_instance())

    def get_order(self) -> int:
        return 0

    def get_enhancer(self):
        return self.enhancer

    def get_input_provider(self):
        return self.input_provider

    def get_output_consumer(self):
        return self.output_consumer

    def get_output_printer(self):
        return self.output_printer

    def get_leetcode_executor(self):
        return self.leetcode_executor

    def get_input_parser(self):
        return self.input_parser


class PipelineProcessor:

    @staticmethod
    def process(enhancer):
        AssertUtil.non_null(enhancer, "The enhancer cannot be null.")
        from src.debugger4py.proxy import EnhancerProxyFactory
        AssertUtil.is_true(EnhancerProxyFactory.is_enhancer(enhancer),
                           "The enhancer is not a LeetcodePythonDebugEnhancer instance."
                           )
        payload = enhancer.get_enhancer_payload()
        AssertUtil.non_null(payload, "The enhancer payload cannot be null.")
        leetcode_executor = LeetcodeExecutorFactory.get_leetcode_executor(payload)
        from src.debugger4py.printer import OutputPrinterFactory
        output_printer = OutputPrinterFactory.get_output_printer(enhancer)
        from src.debugger4py.parser_lib import InputParserFactory
        input_parser = InputParserFactory.get_input_parser(enhancer)
        from src.debugger4py.eio import IOFactory
        with (IOFactory.get_input_provider(enhancer)) as input_provider, (
                IOFactory.get_output_consumer(enhancer)) as output_consumer:
            BootstrapPipeline(
                enhancer,
                input_provider,
                output_consumer,
                output_printer,
                leetcode_executor,
                input_parser
            ).run()
