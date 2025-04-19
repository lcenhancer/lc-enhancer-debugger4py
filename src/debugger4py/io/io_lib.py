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

import io
import sys

from abc import ABCMeta, abstractmethod
from typing import List

from src.debugger4py.base import Order, Closable, AssertUtil, StringUtil


class InputProvider(Order, Closable, metaclass=ABCMeta):
    @abstractmethod
    def provide_next_input(self) -> str: pass

    @abstractmethod
    def is_end(self, input_str: str) -> bool: pass


class OutputConsumer(Order, Closable, metaclass=ABCMeta):
    @abstractmethod
    def consume_next_output(self, output_str: str): pass


class BaseBufferReaderInputProvider(InputProvider, metaclass=ABCMeta):

    def __init__(self, buffered_reader: io.TextIOWrapper):
        AssertUtil.non_null(buffered_reader, "The bufferedReader cannot be null.")
        self.buffered_reader = buffered_reader

    @classmethod
    def from_stream(cls, stream: io.BytesIO, encoding: str = 'utf-8'):
        buffered_reader = io.TextIOWrapper(stream, encoding)
        return cls(buffered_reader)

    def provide_next_input(self) -> str:
        return self.buffered_reader.readline().rstrip('\r\n')

    def is_end(self, input_str: str) -> bool:
        return StringUtil.is_blank(input_str)

    def get_order(self) -> int:
        return 0

    def close(self):
        self.buffered_reader.close()


class BaseBufferWriterOutputConsumer(OutputConsumer, metaclass=ABCMeta):

    def __init__(self, buffered_writer: io.TextIOWrapper):
        AssertUtil.non_null(buffered_writer, "The bufferedWriter cannot be null.")
        self.buffered_writer = buffered_writer

    @classmethod
    def from_stream(cls, stream: io.BytesIO, encoding: str = 'utf-8'):
        buffered_writer = io.TextIOWrapper(stream, encoding)
        return cls(buffered_writer)

    def consume_next_output(self, output_str: str):
        if StringUtil.is_empty(output_str):
            return
        self.buffered_writer.write(output_str)
        self.buffered_writer.write("\n")
        self.buffered_writer.flush()

    def get_order(self) -> int:
        return 0

    def close(self):
        self.buffered_writer.close()


class ConsoleInputProvider(BaseBufferReaderInputProvider):

    def __init__(self, encoding: str = 'utf-8'):
        super().__init__(io.TextIOWrapper(sys.stdin.buffer, encoding=encoding))


class ConsoleOutputConsumer(BaseBufferWriterOutputConsumer):

    def __init__(self, encoding: str = 'utf-8'):
        super().__init__(io.TextIOWrapper(sys.stdout.buffer, encoding=encoding))

    def close(self):
        pass


class FileInputProvider(BaseBufferReaderInputProvider):

    def __init__(self, file_path: str, encoding: str = 'utf-8'):
        super().__init__(io.TextIOWrapper(open(file_path, "rb", -1), encoding=encoding))


class FileOutputConsumer(BaseBufferWriterOutputConsumer):

    def __init__(self, file_path: str, encoding: str = 'utf-8'):
        super().__init__(io.TextIOWrapper(open(file_path, "wb", -1), encoding=encoding))


class StringInputProvider(BaseBufferReaderInputProvider):

    def __init__(self, string: str, encoding: str = 'utf-8'):
        byte_data = string.encode(encoding)
        bytes_io = io.BytesIO(byte_data)
        bytes_io.seek(0)
        super().__init__(io.TextIOWrapper(bytes_io, encoding=encoding))


class MultipleInputProvider(InputProvider):

    def __init__(self, providers: List[InputProvider]):
        AssertUtil.not_empty(providers, "The providers cannot be null and empty.")
        self.providers = tuple(providers)
        self.providers_size = len(providers)
        self.pos = 0
        self.closeFlag = False

    def provide_next_input(self) -> str:
        if self.closeFlag:
            return ""
        if self.pos >= self.providers_size:
            return ""
        s = self.providers[self.pos].provide_next_input()
        if self.is_end(s):
            self.pos += 1
            return self.provide_next_input()
        return s

    def is_end(self, input_str: str) -> bool:
        if self.closeFlag:
            return True
        if self.pos >= self.providers_size:
            return True
        return self.providers[self.pos].is_end(input_str)

    def close(self):
        self.closeFlag = True
        for provider in self.providers:
            try:
                provider.close()
            finally:
                pass

    def get_order(self) -> int:
        return 0


class MultipleOutputConsumer(OutputConsumer):

    def __init__(self, consumers: List[OutputConsumer]):
        AssertUtil.not_empty(consumers, "The consumers cannot be null and empty.")
        self.consumers = tuple(consumers)
        self.closeFlag = False

    def consume_next_output(self, output_str: str):
        if self.closeFlag:
            return
        for consumer in self.consumers:
            if self.closeFlag:
                break
            try:
                consumer.consume_next_output(output_str)
            finally:
                pass

    def close(self):
        self.closeFlag = True
        for consumer in self.consumers:
            try:
                consumer.close()
            finally:
                pass

    def get_order(self) -> int:
        return 0


class IOFactory:
    @staticmethod
    def get_input_provider(enhancer) -> InputProvider:
        AssertUtil.non_null(enhancer, "The enhancer cannot be null.")
        input_provider = enhancer.get_input_provider()
        if input_provider is not None:
            return input_provider
        return ConsoleInputProvider()

    @staticmethod
    def get_output_consumer(enhancer) -> OutputConsumer:
        AssertUtil.non_null(enhancer, "The enhancer cannot be null.")
        output_consumer = enhancer.get_output_consumer()
        if output_consumer is not None:
            return output_consumer
        # By default, the console is used as the output consumer.
        return ConsoleOutputConsumer()
