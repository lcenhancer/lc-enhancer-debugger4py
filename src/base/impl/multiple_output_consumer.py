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

from typing import List

from src.base.interfaces.output_consumer import OutputConsumer
from src.base.util.assert_util import AssertUtil


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
