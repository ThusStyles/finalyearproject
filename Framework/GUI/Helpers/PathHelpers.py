import sys
import os

base_dir = ''

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
elif __file__:
    base_dir = os.path.dirname(__file__)
    base_dir = os.path.abspath(os.path.join(base_dir, '../..'))

class PathHelpers():

    @staticmethod
    def getPath(filename):
        print(base_dir)
        return os.path.join(base_dir, filename)