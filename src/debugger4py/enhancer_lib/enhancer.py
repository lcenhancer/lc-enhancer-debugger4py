from abc import ABCMeta
from typing import List, Type

from src.debugger4py.io_lib import InputProvider, OutputConsumer
from src.debugger4py.parser_lib import BaseParameterAcceptStrategy
from src.debugger4py.printer_lib import BaseOutputPrintStrategy


class LeetcodePythonDebugEnhancer(metaclass=ABCMeta):
    def get_input_provider(self) -> InputProvider: pass

    def get_output_consumer(self) -> OutputConsumer: pass

    def get_output_print_strategies(self) -> List[BaseOutputPrintStrategy]: pass

    def get_parameter_accept_strategies(self) -> List[BaseParameterAcceptStrategy]: pass

    def get_enhancer_payload(self) -> Type: pass
