# +
import warnings
warnings.filterwarnings('ignore')

import os
os.chdir("../wrangle/interventions/")

os.system('python interventionsMerge.py')
os.system('python interventionsUpdate.py')
