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

from typing import Any
from pathlib import Path


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
        AssertUtil.is_true(string is not None and string.strip() == '', msg)


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
        module_name = Path(file_path).stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


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
    def instantiate_class(cls, config=None):
        AssertUtil.non_null(cls, "The class cannot be null.")
        config = config or {}
        return cls(**config)

    @staticmethod
    def instantiate_classes(classes, config=None):
        AssertUtil.not_empty(classes, "The classes cannot be empty.")
        classes = [c for c in classes if c is not None]
        instances = []
        for c in classes:
            instances.append(ClassUtil.instantiate_class(c, config))
        return instances
