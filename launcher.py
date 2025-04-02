import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.ui.menu import run_menu

def main():
    try:
        run_menu()
    except SystemExit:
        os._exit(0)  # Forcefully terminate the script
    except Exception as e:
        print(f"Error: {e}")
        os._exit(1)  # Exit with error status

if __name__ == "__main__":
    main()
