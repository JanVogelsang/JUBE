#!/usr/bin/env python
# JUBE Benchmarking Environment
# Copyright (C) 2008-2016
# Forschungszentrum Juelich GmbH, Juelich Supercomputing Centre
# http://www.fz-juelich.de/jsc/jube
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Step related tests"""

from __future__ import (print_function,
                        unicode_literals,
                        division)

import re

import unittest
import shutil
import os
import jube2.step

class TestOperation(unittest.TestCase):

    """Operation test class"""

    def setUp(self):
        self.currWorkDir=os.getcwd()
        self.operation=jube2.step.Operation('/usr/bin/echo Test', stdout_filename='stdout',
            stderr_filename='stderr', work_dir='.', error_filename='error')
        self.parameter_dict={
            'param': 'p1', 
            'jube_benchmark_id': '0', 
            'jube_benchmark_padid': '000000', 
            'jube_benchmark_name': 'do_log_test', 
            'jube_benchmark_home': self.currWorkDir, 
            'jube_benchmark_rundir': self.currWorkDir+'/bench_run/000000', 
            'jube_benchmark_start': '2022-07-12T16:23:32', 
            'jube_step_name': 'execute', 
            'jube_step_iterations': '1', 
            'jube_step_cycles': '1', 
            'jube_wp_cycle': '0', 
            'jube_wp_id': '0', 
            'jube_wp_padid': '000000', 
            'jube_wp_iteration': '0', 
            'jube_wp_relpath': 'bench_run/000000/000000_execute/work', 
            'jube_wp_abspath': self.currWorkDir+'/bench_run/000000/000000_execute/work', 
            'jube_wp_envstr': '', 
            'jube_wp_envlist': ''}
        self.work_dir="bench_run/000000/000000_execute/work"
        self.environment={'TEST': 'test'}

    def test_operation_execution(self):
        """Test operation execution"""
        if os.path.exists(os.path.join(self.currWorkDir,'bench_run')):
            shutil.rmtree(os.path.join(self.currWorkDir,'bench_run')) 
        os.makedirs(self.currWorkDir+'/bench_run/000000/000000_execute/work')
        self.operation.execute(self.parameter_dict, self.work_dir, environment=self.environment)
        self.assertTrue(os.path.exists(self.currWorkDir+'/bench_run/000000/000000_execute/work/stdout'))
        self.assertTrue(os.path.exists(self.currWorkDir+'/bench_run/000000/000000_execute/work/stderr'))
        self.assertTrue(os.stat(self.currWorkDir+'/bench_run/000000/000000_execute/work/stderr').st_size == 0)
        stdoutFileHandle=open(self.currWorkDir+'/bench_run/000000/000000_execute/work/stdout', mode='r')
        line=stdoutFileHandle.readline()
        self.assertTrue(line=='Test\n')
        line=stdoutFileHandle.readline()
        self.assertTrue(line=='')
        stdoutFileHandle.close()
        shutil.rmtree(os.path.join(self.currWorkDir,'bench_run'))

    def test_do_log_creation(self):
        """Test do log creation"""
        if os.path.exists(os.path.join(self.currWorkDir,'do_log')):
            os.remove(os.path.join(self.currWorkDir,'do_log')) 
        self.operation.storeToDoLog(do="echo Test1", work_dir=self.currWorkDir+'/bench_run', env=self.environment, shell='/bin/sh')
        self.operation.storeToDoLog(do="echo $TEST", work_dir=self.currWorkDir+'/bench_run', env=self.environment, shell='/bin/sh')
        self.assertTrue(os.path.exists(os.path.join(self.currWorkDir,'do_log')))

        # Check the content of the do_log file manually, which should look like the following:
        #   #!/bin/sh
        #   
        #   set TEST='test'
        #   
        #   echo Test1
        #   echo $TEST

        dologFileHandle=open(os.path.join(self.currWorkDir,'do_log'), mode='r')
        line=dologFileHandle.readline()
        self.assertTrue(line=='#!/bin/sh\n')
        line=dologFileHandle.readline()
        self.assertTrue(line=='\n')
        line=dologFileHandle.readline()
        self.assertTrue(line=="set TEST='test'\n")
        line=dologFileHandle.readline()
        self.assertTrue(line=="\n")
        line=dologFileHandle.readline()
        self.assertTrue(line=="echo Test1\n")
        line=dologFileHandle.readline()
        self.assertTrue(line=="echo $TEST\n")
        line=dologFileHandle.readline()
        self.assertTrue(line=='')
        dologFileHandle.close()

        os.remove(os.path.join(self.currWorkDir,'do_log')) 


if __name__ == "__main__":
    unittest.main()
