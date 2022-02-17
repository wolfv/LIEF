#!/usr/bin/env python
import itertools
import logging
import os
import random
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import TestCase
from subprocess import Popen
import re

import lief
from utils import get_sample, is_linux, is_x86_64

lief.logging.set_level(lief.logging.LOGGING_LEVEL.INFO)

class TestLargeBss(TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)

    def test_all(self):
        binary_name = "544ca2035a9c15e7756ed8d8067d860bd3157e4eeaa39b4ee932458eebe2434b.elf"
        target: lief.ELF.Binary = lief.parse(get_sample("ELF/{}".format(binary_name)))
        bss = target.get_section(".bss")
        self.assertEqual(bss.virtual_address, 0x65a3e0)
        self.assertEqual(bss.size, 0x1ccb6330)
        self.assertEqual(bss.file_offset, 0x05a3e0)
        self.assertEqual(len(bss.content), 0)

        target.add_library("libcap.so.2")
        # Add segment
        new_segment = lief.ELF.Segment()
        new_segment.type = lief.ELF.SEGMENT_TYPES.LOAD
        new_segment.content = [0xCC] * 0x50
        target.add(new_segment)

        tmp_dir = tempfile.mkdtemp(prefix="lief_", suffix='_{}'.format(self.__class__.__name__))
        self.logger.debug("temp dir: {}".format(tmp_dir))
        output = "{}/{}.built".format(tmp_dir, binary_name)
        target.write(output)

        if is_linux() and is_x86_64():
            st = os.stat(output)
            os.chmod(output, st.st_mode | stat.S_IEXEC)

            p = Popen(output, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, _ = p.communicate()
            self.logger.debug(stdout.decode("utf8"))
            self.assertTrue(len(stdout) > 0)

        # Check that the written binary contains our modifications
        new: lief.ELF.Binary = lief.parse(output)
        self.assertEqual(new.get_library("libcap.so.2").name, "libcap.so.2")


if __name__ == '__main__':

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    root_logger.addHandler(ch)

    unittest.main(verbosity=2)
