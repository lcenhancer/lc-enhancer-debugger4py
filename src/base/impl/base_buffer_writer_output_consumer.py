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
from abc import ABCMeta

from src.base.interfaces.output_consumer import OutputConsumer
from src.base.util.assert_util import AssertUtil
from src.base.util.string_util import StringUtil


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
