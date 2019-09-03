#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shutil
import os
import sys
import re
args = sys.argv
path = args[1]
files_list = os.listdir(path)
for file in files_list:
    filename, suffix = os.path.splitext(file)
    for patnum in (range(65,91) or range(91,123)):
        pat = r"^"+chr(patnum)
        pattren = re.compile(pat)
        matchcif = pattren.match(filename)
       # print(matchcif)
        if matchcif is not None:
            filepath = path+"/part_"+"".join(chr(patnum))
            print("Moving  "+ file + "  to  " + filepath + "...")
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            srcfile = path+ "/" +file
            desfile = filepath+"/"+file
            shutil.move(srcfile,desfile)
