#!/usr/bin/env python
# coding: utf-8
# +
import os

os.chdir("../collect/")
os.system('python cases.py')

os.chdir("../wrangle/cases/")
os.system('python mergeHR.py')
os.system('python top30.py')

# -


