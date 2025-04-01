import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.ui.menu import run_menu

if __name__ == "__main__":
    run_menu()