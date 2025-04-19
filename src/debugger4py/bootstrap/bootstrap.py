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


class Debugger4pyBootstrap:

    @staticmethod
    def startup(__AT_TYPE__):
        from src.debugger4py.base import AssertUtil
        AssertUtil.non_null(__AT_TYPE__, "The AT-TYPE cannot be null.")
        AssertUtil.is_true(isinstance(__AT_TYPE__, type), "The AT-TYPE is not a type.")
        from src.debugger4py.enhancer4py import LeetcodePythonDebugEnhancer
        AssertUtil.is_true(issubclass(__AT_TYPE__, LeetcodePythonDebugEnhancer),
                           "The AT-TYPE is not an AT class.")
        from src.debugger4py.proxy import EnhancerProxyFactory
        __enhancer__ = EnhancerProxyFactory.create_enhancer_proxy(__AT_TYPE__)
        from src.debugger4py.pipeline import PipelineProcessor
        PipelineProcessor.process(__enhancer__)
