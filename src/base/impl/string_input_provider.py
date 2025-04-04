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

import io

from src.base.impl.base_buffer_reader_input_provider import BaseBufferReaderInputProvider


class StringInputProvider(BaseBufferReaderInputProvider):

    def __init__(self, string: str, encoding: str = 'utf-8'):
        byte_data = string.encode(encoding)
        bytes_io = io.BytesIO(byte_data)
        bytes_io.seek(0)
        super().__init__(io.TextIOWrapper(bytes_io, encoding=encoding))
