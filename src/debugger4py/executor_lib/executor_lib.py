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
        return self.func(**args)

    def invoke0(self, *args, **kwargs):
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
    def __init__(self, invoker_id: int, order: int, py_function: PythonFunction):
        AssertUtil.non_null(py_function, "The func cannot be null.")
        self.id = invoker_id
        self.order = order
        self.py_function = py_function

    def get_id(self):
        return self.id

    def get_parameter_cnt(self):
        return len(self.py_function.parameter_info)

    def get_parameter_types(self):
        return self.py_function.parameter_info.values()

    def get_parameters(self):
        return self.py_function.parameter_info

    def get_invoker_name(self):
        return self.py_function.func_name

    def get_return_type(self):
        return self.py_function.return_type

    def invoke(self, args):
        return self.py_function.invoke(args)

    def get_order(self) -> int:
        return self.order


class LeetcodeExecutor:
    def __init__(self, instance, executor: LeetcodeInvoker):
        self.instance = instance
        self.candidate_invokers = []
        self.executor = executor
        if executor is not None:
            self.candidate_invokers.append(executor)

    def exec(self, input_obj):
        AssertUtil.non_null(self.executor, "The leetcode executor cannot be null.")
        return self.executor.invoke(input_obj)

    def get_instance(self):
        return self.instance

    def get_executor(self):
        return self.executor

    def set_executor(self, executor: LeetcodeInvoker):
        self.executor = executor

    def get_candidate_invokes(self):
        return self.candidate_invokers

    def get_return_type(self):
        return self.executor.get_return_type()
