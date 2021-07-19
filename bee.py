
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from Bee.util import resources

res_dir = os.path.join(os.path.dirname(__file__), "res")
    
resources.set_base_path(res_dir)

def main():
    from Bee.gui import main
    main.run()

if __name__ == '__main__':
    main()
