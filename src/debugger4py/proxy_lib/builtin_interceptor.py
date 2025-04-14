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

from abc import ABCMeta, abstractmethod

from src.debugger4py.base_lib import AssertUtil, Order


class ProxyPointParameterView:

    def __init__(self, type_arr, arg_arr):
        AssertUtil.non_null(type_arr, "The type_arr cannot be null.")
        arg_arr = [] if arg_arr is None else arg_arr
        AssertUtil.is_true(len(type_arr) == len(arg_arr),
                           "The length of type_arr does not match the length of the arg_arr."
                           )
        self.type_arr = type_arr
        self.arg_arr = arg_arr
        self.size = len(self.type_arr)

    def get_size(self):
        return self.size

    def get_parameter_type(self, pos: int):
        AssertUtil.is_true(pos is not None and 0 < pos < self.size, "Illegal parameter position.")
        return self.type_arr[pos]

    def get_parameter(self, pos: int):
        AssertUtil.is_true(pos is not None and 0 < pos < self.size, "Illegal parameter position.")
        return self.arg_arr[pos]

    def set_parameter(self, pos: int, val):
        AssertUtil.is_true(pos is not None and 0 < pos < self.size, "Illegal parameter position.")
        if val is not None:
            AssertUtil.is_true(isinstance(val, self.get_parameter_type(pos)), "Illegal parameter value type.")
        self.arg_arr[pos] = val


class ProxyPointInterceptor(Order, metaclass=ABCMeta):

    def on_before(self, enhancer, param_view: ProxyPointParameterView): pass

    def on_after(self, enhancer, result_obj):
        return result_obj

    @abstractmethod
    def intercept_point(self) -> str: pass
