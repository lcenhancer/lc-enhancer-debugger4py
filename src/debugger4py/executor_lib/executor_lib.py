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

import ast
from collections import OrderedDict
from typing import Type, Dict, Any, List, Tuple, Optional, Union

from src.debugger4py.base_lib import AssertUtil, StringUtil, TreeNode, ListNode, Order


class PythonFunction:
    def __init__(self, func):
        AssertUtil.non_null(func, "The func cannot be null.")
        self.func = func
        self.func_name = func.__name__
        doc_pi = PythonFunction.__py_func_parse_doc__(func.__doc__)
        sign_pi = PythonFunction.__py_func_parse_signature__(func)

        def select_not_any_type(type1, type2):
            if type1 is None:
                return type2
            if type2 is None:
                return type1
            if type1 is Any:
                return type2
            return type1

        for p_n in sign_pi[0]:
            if p_n in doc_pi[0]:
                sign_pi[0][p_n] = select_not_any_type(sign_pi[0][p_n], doc_pi[0][p_n])

        self.parameter_info = sign_pi[0]
        self.return_type = select_not_any_type(sign_pi[1], doc_pi[1])

    def invoke(self, args):
        return self.func(*args)

    def invoke_with_kwargs(self, args, kwargs):
        return self.func(*args, **kwargs)

    @staticmethod
    def __py_func_parse_signature__(func):
        import inspect
        func_sign = inspect.signature(func)
        base_param_info = OrderedDict()
        for parameter_obj in func_sign.parameters.values():
            ptype = parameter_obj.annotation
            if str(ptype) == "<class 'inspect._empty'>":
                ptype = Any
            base_param_info[parameter_obj.name] = ptype
        rtype = func_sign.return_annotation
        if str(rtype) == "<class 'inspect._empty'>":
            rtype = Any
        return base_param_info, rtype

    @staticmethod
    def __py_func_parse_doc__(doc: str):
        base_param_info = {}
        rtype = None
        if not StringUtil.is_blank(doc):
            left, right, pos = 0, 0, 0
            while True:
                pos = left
                left = doc.find(":type", left)
                if left == -1:
                    break
                left += 6
                right = doc.find(":", left)
                if right == -1:
                    break
                val_name = doc[left: right]
                right += 2
                left = right
                right = doc.find("\n", left)
                if right == -1:
                    break
                type_name = doc[left: right]
                base_param_info[val_name] = type_name
                left = right + 1
            left = pos
            left = doc.find(":rtype: ", left)
            if left != -1:
                left += 8
                right = doc.find("\n", left)
                if right != -1:
                    rtype = doc[left:right]
            for name in base_param_info:
                base_param_info[name] = PythonFunction.__py_func_parse_type__(base_param_info[name])
        if rtype is not None:
            rtype = PythonFunction.__py_func_parse_type__(rtype)
        else:
            rtype = Any
        return base_param_info, rtype

    @staticmethod
    def __py_func_parse_type__(type_str: str) -> Type:
        allowed_types: Dict[str, Any] = {
            'List': List,
            'Dict': Dict,
            'Tuple': Tuple,
            'Optional': Optional,
            'Union': Union,
            'Any': Any,
            'int': int,
            'str': str,
            'float': float,
            'bool': bool,
            'TreeNode': TreeNode,
            'ListNode': ListNode
        }

        try:
            tree = ast.parse(type_str, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Invalid type syntax: {e}")

        def _parse_node_(node) -> Any:
            if isinstance(node, ast.Name):
                if node.id in allowed_types:
                    return allowed_types[node.id]
                raise ValueError(f"Unsupported type: {node.id}")

            elif isinstance(node, ast.Subscript):
                value_type = _parse_node_(node.value)

                if isinstance(node.slice, ast.Index):
                    slice_node = node.slice.value
                elif isinstance(node.slice, ast.Tuple):
                    slice_node = node.slice
                else:
                    slice_node = node.slice

                if isinstance(slice_node, ast.Tuple):
                    args = tuple(_parse_node_(e) for e in slice_node.elts)
                else:
                    args = (_parse_node_(slice_node),)

                return value_type[args]

            elif isinstance(node, ast.Constant):
                return node.value

            elif isinstance(node, ast.BinOp):
                if isinstance(node.op, ast.BitOr):
                    left = _parse_node_(node.left)
                    right = _parse_node_(node.right)
                    return Union[left, right]

            raise ValueError(f"Unsupported AST node: {type(node).__name__}")

        try:
            result = _parse_node_(tree.body)
        except KeyError as e:
            raise ValueError(f"Undefined type: {e}")

        return result


class LeetcodeInvoker(Order):
    def __init__(self, invoker_id: int, order: int, py_function: PythonFunction, matching_friendly: bool = True):
        AssertUtil.non_null(py_function, "The func cannot be null.")
        self.id = invoker_id
        self.order = order
        self.py_function = py_function
        self.matching_friendly = matching_friendly

    def get_id(self):
        return self.id

    def get_parameter_cnt(self):
        p_l = len(self.py_function.parameter_info.keys())
        if p_l > 0 and 'self' in self.py_function.parameter_info and self.matching_friendly:
            return p_l - 1
        return p_l

    def get_parameter_types(self):
        pi = self.py_function.parameter_info
        if self.matching_friendly and 'self' in pi:
            pi = pi.copy()
            del pi['self']
        return pi.values()

    def get_parameters(self):
        pi = self.py_function.parameter_info
        if self.matching_friendly and 'self' in pi:
            pi = pi.copy()
            del pi['self']
        return pi

    def get_invoker_name(self):
        return self.py_function.func_name

    def get_return_type(self):
        return self.py_function.return_type

    def invoke(self, args):
        return self.py_function.invoke(args)

    def get_order(self) -> int:
        return self.order

    def is_suitable(self, suitable_type):
        suitable_type_full_name = f"{suitable_type.__module__}.{suitable_type.__qualname__}"
        func_full_name = f"{self.py_function.func.__module__}.{self.py_function.func.__qualname__}"
        idx = func_full_name.rfind(".")
        if idx != -1:
            func_full_name = func_full_name[:idx]
        return suitable_type_full_name == func_full_name


class LeetcodeExecutor:
    def __init__(self, instance, executor: LeetcodeInvoker):
        self.instance = instance
        self.candidate_invokers = []
        self.executor = executor
        if executor is not None:
            self.candidate_invokers.append(executor)

    def execute(self, input_obj):
        AssertUtil.non_null(self.executor, "The leetcode executor cannot be null.")
        __invoke_params__ = [self.instance] if self.instance is not None else []
        __invoke_params__.extend(input_obj)
        return self.executor.invoke(__invoke_params__)

    def get_instance(self):
        return self.instance

    def set_instance(self, instance):
        self.instance = instance

    def get_executor(self):
        return self.executor

    def set_executor(self, executor: LeetcodeInvoker):
        self.executor = executor

    def get_candidate_invokers(self):
        return self.candidate_invokers

    def get_return_type(self):
        return self.executor.get_return_type()


class LeetcodeInvokerFactory:
    INVOKER_ID_GENERATOR = 1

    @staticmethod
    def __gen_id__():
        cur_id = LeetcodeInvokerFactory.INVOKER_ID_GENERATOR
        LeetcodeInvokerFactory.INVOKER_ID_GENERATOR += 1
        return cur_id

    @staticmethod
    def get_leetcode_invoker(func, order: int = None) -> LeetcodeInvoker:
        cur_id = LeetcodeInvokerFactory.__gen_id__()
        if order is None:
            order = cur_id
        return LeetcodeInvoker(cur_id, order, PythonFunction(func))


class LeetcodeExecutorFactory:

    @staticmethod
    def get_leetcode_executor(object_instance, *leetcode_invokers):
        AssertUtil.non_null(object_instance, "The instance cannot be null.")
        primary_invoker = leetcode_invokers[0] if len(leetcode_invokers) > 0 else None
        executor = LeetcodeExecutor(object_instance, primary_invoker)
        for i in range(1, len(leetcode_invokers), 1):
            leetcode_invoker = leetcode_invokers[i]
            if leetcode_invoker is not None:
                executor.get_candidate_invokers().append(leetcode_invoker)
        return executor

    @staticmethod
    def copy_by_leetcode_executor(object_instance):
        AssertUtil.non_null(object_instance, "The instance cannot be null.")
        AssertUtil.is_true(isinstance(object_instance, LeetcodeExecutor),
                           "The instance is not a LeetcodeExecutor instance."
                           )
        copied_instance = LeetcodeExecutor(object_instance.get_instance(), object_instance.get_executor())
        copied_instance.candidate_invokers.extend(object_instance.get_candidate_invokers())
        return copied_instance


class LeetcodeExecutorProcessor:

    @staticmethod
    def process(executor, input_obj):
        AssertUtil.non_null(executor, "The executor cannot be null.")
        AssertUtil.is_true(isinstance(executor, LeetcodeExecutor), "The executor is not a LeetcodeExecutor.")
        return executor.execute(input_obj)
