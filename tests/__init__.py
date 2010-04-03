# do the most basic pip test here, just to make sure we're working with the right codebase.
import os, sys
_pip_path = os.path.join(os.path.dirname(__file__), os.path.pardir, 'pippl')
sys.path = [os.path.join(_pip_path, 'tests'), _pip_path] + sys.path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir, 'pippl', 'tests'))
from test_basic import test_correct_pip_version
