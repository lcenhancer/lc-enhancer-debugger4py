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

from src.base.interfaces.input_provider import InputProvider
from src.base.util.assert_util import AssertUtil


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
