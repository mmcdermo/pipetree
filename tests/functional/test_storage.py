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
import os
import unittest
from tests import isolated_filesystem
from pipetree.config import PipelineStageConfig
from pipetree.storage import LocalDirectoryArtifactProvider
from pipetree.exceptions import ArtifactSourceDoesNotExistError,\
    InvalidConfigurationFileError


class TestLocalDirectoryArtifactProvider(unittest.TestCase):
    def setUp(self):
        self.dirname = 'foo'
        self.filename = ['foo.bar', 'foo.baz']
        self.filedatas = ['foo bar baz', 'helloworld']
        self.fs = isolated_filesystem()
        self.fs.__enter__()
        self.stage_config = PipelineStageConfig("test_stage_name", {
            "type": "LocalDirectoryPipelineStage"
        })

        # Build directory structure
        os.makedirs(self.dirname)
        for name, data in zip(self.filename, self.filedatas):
            with open(os.path.join(os.getcwd(),
                                   self.dirname,
                                   name), 'w') as f:
                f.write(data)

    def tearDown(self):
        self.fs.__exit__(None, None, None)

    def test_load_nonexistant_dir(self):
        try:
            LocalDirectoryArtifactProvider(path='folder/',
                                           stage_config=self.stage_config)
            self.assertTrue(False, 'This was supposed to raise an exception')
        except ArtifactSourceDoesNotExistError:
            pass

    def test_load_file_data(self):
        provider = LocalDirectoryArtifactProvider(path=self.dirname,
                                                  stage_config=self.stage_config,
                                                  read_content=True)
        art = provider._yield_artifact(self.filename[0])
        self.assertEqual(art.payload.decode('utf-8'),
                         self.filedatas[0])

    def test_load_file_names(self):
        provider = LocalDirectoryArtifactProvider(path=self.dirname,
                                                  stage_config=self.stage_config)
        for loaded_name, name in zip(provider.yield_artifacts(),
                                     self.filename):
            self.assertEqual(loaded_name, os.path.join(os.getcwd(),
                                                       self.dirname,
                                                       name))

    def test_load_multiple_file_contents(self):
        provider = LocalDirectoryArtifactProvider(path=self.dirname,
                                                  stage_config=self.stage_config,
                                                  read_content=True)
        for art, data in zip(provider.yield_artifacts(),
                             self.filedatas):
            art_data = art.payload
            self.assertEqual(art_data.decode('utf-8'), data)
