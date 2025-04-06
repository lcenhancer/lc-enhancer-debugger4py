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

from collections import deque
from typing import Type, Mapping, List

from src.debugger4py.base_lib import TreeNode, ListNode
from src.debugger4py.printer_lib.printer_lib import BaseOutputPrintStrategy


class BinaryTreePrintingStrategy(BaseOutputPrintStrategy):

    def get_acceptable_type(self) -> Type:
        return TreeNode

    def get_order(self) -> int:
        return 0

    def print_output(self, output: TreeNode, strategies_map: Mapping[Type, List[BaseOutputPrintStrategy]]) -> str:
        res = ['[']
        if output:
            val_list = []
            queue = deque([output])
            while queue:
                level_size = len(queue)
                for _ in range(level_size):
                    node = queue.popleft()
                    if node:
                        val_list.append(node.val)
                        queue.append(node.left)
                        queue.append(node.right)
                    else:
                        val_list.append(None)

            while val_list and val_list[-1] is None:
                val_list.pop()
            res.append(','.join('null' if v is None else str(v) for v in val_list))
        res.append(']')
        return ''.join(res)


class SinglyLinkedListPrintingStrategy(BaseOutputPrintStrategy):
    def get_acceptable_type(self) -> Type:
        return ListNode

    def get_order(self) -> int:
        return 0

    def print_output(self, obj: ListNode, strategies_map: Mapping[Type, List[BaseOutputPrintStrategy]]) -> str:
        res = ['[']
        pointer = obj
        while pointer:
            res.append(pointer.val)
            res.append(',')
            pointer = pointer.next
        if res and res[-1] == ',':
            res.pop()
        res.append(']')
        return ''.join(map(str, res))
