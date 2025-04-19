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

import inspect
import importlib.util

from typing import Any, get_args, Type, get_origin


class AssertUtil:

    @staticmethod
    def is_true(flag: bool, msg: str):
        if not flag or flag is False:
            raise AssertionError(msg)

    @staticmethod
    def non_null(obj: Any, msg: str):
        AssertUtil.is_true(obj is not None, msg)

    @staticmethod
    def not_empty(obj: Any, msg: str):
        AssertUtil.is_true(obj is not None and len(obj) > 0, msg)

    @staticmethod
    def not_blank(string: str, msg: str):
        AssertUtil.is_true(string is not None and string.strip() != '', msg)


class StringUtil:

    @staticmethod
    def is_blank(string: str) -> bool:
        return string is None or string.strip() == ''

    @staticmethod
    def is_empty(string: str) -> bool:
        return string is None or len(string) == 0


class ContainerUtil:

    @staticmethod
    def is_empty(obj: Any) -> bool:
        return obj is None or len(obj) == 0

    @staticmethod
    def not_empty(obj: Any) -> bool:
        return obj is not None and len(obj) > 0


class ModuleUtil:

    @staticmethod
    def load_module_from_file(file_path):
        return importlib.import_module(file_path)


class ClassUtil:

    @staticmethod
    def get_classes_from_module(module, class_filter=None):
        classes = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                if class_filter and not class_filter(obj):
                    continue
                classes.append(obj)
        return classes

    @staticmethod
    def load_class_from_file(module, class_name):
        AssertUtil.not_blank(class_name, "The class name cannot be blank.")
        return getattr(ModuleUtil.load_module_from_file(module), class_name)

    @staticmethod
    def load_class(full_class_path):
        AssertUtil.not_blank(full_class_path, "The full class path cannot be blank.")
        if full_class_path.find(".") == -1:
            return ClassUtil.load_class_from_file("", full_class_path)
        module, class_name = full_class_path.rsplit(".", 1)
        return ClassUtil.load_class_from_file(module, class_name)

    @staticmethod
    def instantiate_class(cls, config=None):
        AssertUtil.non_null(cls, "The class cannot be null.")
        config = config or {}
        return cls(**config)

    @staticmethod
    def instantiate_classes(classes, config=None):
        classes = [c for c in classes if c is not None]
        instances = []
        for c in classes:
            instances.append(ClassUtil.instantiate_class(c, config))
        return instances


class TypeUtil:

    @staticmethod
    def obtain_generic_argument_types(cur_type: Type):
        return get_args(cur_type)

    @staticmethod
    def obtain_raw_type_of_type(cur_type: Type):
        return get_origin(cur_type)


class OrderUtil:
    ASC_ORDER_CMP = {
        'key': lambda x: x.get_order(),
        'reverse': False
    }

    DESC_ORDER_CMP = {
        'key': lambda x: x.get_order(),
        'reverse': True
    }

    @staticmethod
    def asc_comparator():
        return OrderUtil.ASC_ORDER_CMP

    @staticmethod
    def desc_comparator():
        return OrderUtil.DESC_ORDER_CMP

    @staticmethod
    def order_sort(order_able_list, comparator=ASC_ORDER_CMP):
        AssertUtil.non_null(order_able_list, "The list cannot be null.")
        order_able_list.sort(**comparator)

    @staticmethod
    def asc_sort(order_able_list):
        return OrderUtil.order_sort(order_able_list, OrderUtil.asc_comparator())

    @staticmethod
    def desc_sort(order_able_list):
        return OrderUtil.order_sort(order_able_list, OrderUtil.desc_comparator())
