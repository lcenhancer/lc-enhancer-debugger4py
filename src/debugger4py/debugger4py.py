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

from .enhancer4py import LeetcodePythonDebugEnhancer


class Debugger4py(LeetcodePythonDebugEnhancer):
    VERSION = "1.0.0"

    @staticmethod
    def __debugger_main__(AT):
        from src.debugger4py.base import AssertUtil
        AssertUtil.non_null(AT, "The AT parameter cannot be null.")
        __AT_TYPE__ = AT
        if isinstance(AT, str):
            from src.debugger4py.base import ClassUtil
            __AT_TYPE__ = ClassUtil.load_class(AT)
        AssertUtil.is_true(isinstance(__AT_TYPE__, type), f"Cannot load AT-TYPE: str{AT}")
        AssertUtil.is_true(__AT_TYPE__.__name__ != "Debugger4py", "Cannot start from an abstract Debugger4py.")
        print("Debugger4py[" + Debugger4py.VERSION + "] starting.")
        from src.debugger4py.bootstrap import Debugger4pyBootstrap
        Debugger4pyBootstrap.startup(__AT_TYPE__)
