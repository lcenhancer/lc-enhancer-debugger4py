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
from typing import Type

from src.debugger4py.base import AssertUtil, ContainerUtil, OrderUtil
from .builtin_interceptor import ProxyPointInterceptor, ProxyPointParameterView
from src.debugger4py.enhancer4py import LeetcodePythonDebugEnhancer


class ProxyPointInterceptorManager:

    def __init__(self):
        self.proxy_point_interceptor_map = {}
        from src.debugger4py.base import ClassUtil
        from src.debugger4py.base import ModuleUtil
        builtin_interceptor_classes = ClassUtil.get_classes_from_module(
            ModuleUtil.load_module_from_file("src.debugger4py.proxy.builtin_interceptor"),
            lambda cls:
            not isabstract(cls)
            and issubclass(cls, ProxyPointInterceptor)
        )
        builtin_interceptor_instances = ClassUtil.instantiate_classes(builtin_interceptor_classes)
        for interceptor in builtin_interceptor_instances:
            intercept_point = interceptor.intercept_point()
            AssertUtil.not_blank(intercept_point, "The intercept point cannot be blank.")
            if intercept_point not in self.proxy_point_interceptor_map:
                self.proxy_point_interceptor_map[intercept_point] = []
            self.proxy_point_interceptor_map[intercept_point].append(interceptor)
        for intercept_point in self.proxy_point_interceptor_map:
            OrderUtil.desc_sort(self.proxy_point_interceptor_map[intercept_point])

    def do_intercept_on_before(self, enhancer, point_name: str, param_view: ProxyPointParameterView):
        AssertUtil.non_null(enhancer, "The enhancer cannot be null.")
        AssertUtil.not_blank(point_name, "The proxy point name cannot be blank.")
        AssertUtil.non_null(param_view, "The param view cannot be null.")
        if point_name not in self.proxy_point_interceptor_map:
            return
        interceptors = self.proxy_point_interceptor_map[point_name]
        if ContainerUtil.is_empty(interceptors):
            return
        for interceptor in interceptors:
            interceptor.on_before(enhancer, param_view)

    def do_intercept_on_after(self, enhancer, point_name: str, result_obj):
        AssertUtil.non_null(enhancer, "The enhancer cannot be null.")
        AssertUtil.not_blank(point_name, "The proxy point name cannot be blank.")
        if point_name not in self.proxy_point_interceptor_map:
            return result_obj
        interceptors = self.proxy_point_interceptor_map[point_name]
        if ContainerUtil.is_empty(interceptors):
            return result_obj
        for interceptor in interceptors:
            result_obj = interceptor.on_after(enhancer, result_obj)
        return result_obj


class EnhancerProxyHandler:

    def __init__(self, target: LeetcodePythonDebugEnhancer):
        AssertUtil.non_null(target, "The target cannot be null.")
        AssertUtil.is_true(isinstance(target, LeetcodePythonDebugEnhancer),
                           "The target is not a LeetcodePythonDebugEnhancer target.")
        self.__proxy_target__ = target
        self.__interceptor_manager__ = ProxyPointInterceptorManager()

    def get_target(self):
        return self.__proxy_target__

    def __getattr__(self, item):
        attr = getattr(self.get_target(), item)
        if callable(attr):
            return lambda *args: self.__proxy_point_invoke__(item, attr, *args)
        return attr

    def __proxy_point_invoke__(self, point_name, point_obj, *point_args):
        from src.debugger4py.executor import LeetcodeInvokerFactory
        invoker = LeetcodeInvokerFactory.get_leetcode_invoker(point_obj)
        param_view = ProxyPointParameterView(
            invoker.get_parameter_types(),
            point_args
        )
        self.__interceptor_manager__.do_intercept_on_before(self, point_name, param_view)
        result = invoker.invoke(point_args)
        return self.__interceptor_manager__.do_intercept_on_after(self, point_name, result)


class EnhancerProxyFactory:

    @staticmethod
    def create_enhancer_proxy(__AT__: Type):
        AssertUtil.non_null(__AT__, "The AT type cannot be null.")
        return EnhancerProxyHandler(__AT__())

    @staticmethod
    def aware_source_enhancer(enhancer: LeetcodePythonDebugEnhancer):
        if enhancer is None:
            return None
        if not isinstance(enhancer, EnhancerProxyHandler):
            return enhancer
        return EnhancerProxyFactory.aware_source_enhancer(enhancer.get_target())

    @staticmethod
    def is_enhancer(enhancer):
        return isinstance(EnhancerProxyFactory.aware_source_enhancer(enhancer), LeetcodePythonDebugEnhancer)
