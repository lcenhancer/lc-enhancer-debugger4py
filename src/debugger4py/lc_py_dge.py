from abc import ABCMeta
from typing import List

from src.debugger4py.io_lib import InputProvider, OutputConsumer
from src.debugger4py.printer_lib import BaseOutputPrintStrategy


class LeetcodePythonDebugEnhancer(metaclass=ABCMeta):
    def get_input_provider(self) -> InputProvider: pass

    def get_output_consumer(self) -> OutputConsumer: pass

    def get_output_print_strategies(self) -> List[BaseOutputPrintStrategy]: pass
