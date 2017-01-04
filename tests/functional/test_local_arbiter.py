# MIT License

# Copyright (c) 2016 Morgan McDermott & John Carlyle

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
import json
import asyncio
import os.path
from tests import isolated_filesystem
from collections import OrderedDict

from pipetree.artifact import Artifact
from pipetree.config import PipelineStageConfig
from pipetree.exceptions import *

from pipetree.arbiter import LocalArbiter


class AioTestCase(unittest.TestCase):
    # noinspection PyPep8Naming
    def __init__(self, methodName='runTest', loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self._function_cache = {}
        super(AioTestCase, self).__init__(methodName=methodName)

    def coroutine_function_decorator(self, func):
        def wrapper(*args, **kw):
            return self.loop.run_until_complete(func(*args, **kw))
        return wrapper

    def __getattribute__(self, item):
        attr = object.__getattribute__(self, item)
        if asyncio.iscoroutinefunction(attr):
            if item not in self._function_cache:
                self._function_cache[item] = \
                  self.coroutine_function_decorator(attr)
            return self._function_cache[item]
        return attr


class TestLocalArbiter(AioTestCase):
    def setUp(self):
        self.config_filename = 'pipetree.json'
        self.testfile_name = 'testfile'
        self.testfile_contents = "Testfile Contents"
        self.fs = isolated_filesystem()
        self.fs.__enter__()

        with open(os.path.join(".", self.testfile_name), 'w') as f:
            json.dump(self.testfile_contents, f)

        with open(os.path.join(".", self.config_filename), 'w') as f:
            json.dump(self.generate_pipeline_config(), f)

        pass

    def tearDown(self):
        self.fs.__exit__(None, None, None)

    def generate_pipeline_config(self):
        return OrderedDict([(
            'StageA', {
                'type': 'LocalFilePipelineStage',
                'filepath': self.testfile_name
            }),
            ('StageB', {
                'inputs': ['StageA'],
                'type': 'ExecutorPipelineStage',
                'execute': 'package.file.function'
            })]
        )


    def test_basic_fucntionality(self):
        arbiter = LocalArbiter(os.path.join(".", self.config_filename))
        arbiter.run_event_loop(close_after=5.0)
        pass
