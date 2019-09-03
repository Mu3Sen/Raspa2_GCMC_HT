#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import random
import os
import Node
import mofs_calc_dir
import mofs_adsorption


args = sys.argv
path = args[1]
mode = args[2]
part = args[3]
#
print("Extracting Helium Void Fraction values")
mofs = os.listdir(path)
for mof in mofs:
    filepath = path + os.sep + "".join(mof)
    try:
       shpath =  mofs_adsorption.apply_pressure(filepath,mode,part)
    except FileNotFoundError:
        print(mof,"  Helium void Fraction was not found")
        continue 
#print(shpath)
#submit job
homepath = os.path.expanduser('~')
print("creating the batch scripts...")
Node.creat_workdir(homepath,mode,part)
#Node.split_job(mode,shpath,part)
print("Start submitting mof "+mode+" calculation work...")
submission = Node.submit_job(mode,shpath,part)
if submission is True:
    exit(0) 


