#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import random
import os
import node
import mofs_calc_dir
import mofs_adsorption

args = sys.argv
filepath = args[1]
mode = args[2]
part = args[3]
# MOFs step 1
print("Creating the calculation directory...")
work_dir = mofs_calc_dir.calc_directory(filepath)
for mofpath in work_dir:
    filename = mofs_calc_dir.find_cif(mofpath)
    os.chdir(mofpath)
    shpath = mofs_calc_dir.calc_propery(mofpath,mode,part)
# submit step 1 job
homepath = os.path.expanduser('~')
print("creating the batch scripts...")
node.creat_workdir(homepath,mode,part)
node.split_job(mode,shpath,part)
print("Start submitting mof "+mode+" calculation work...")
submission = node.submit_job(mode,shpath,part)
if submission is True:
    exit(0) 