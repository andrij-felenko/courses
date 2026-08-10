import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../../scripts"))
try:
    import svgkit
except ImportError:
    pass

def render():
    print("Rendering SVG for sigstruct-and-sgx-enclaves...")

if __name__ == "__main__":
    render()
