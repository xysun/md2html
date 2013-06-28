# TODO: allow options

from markdown import markdown
from renderers import Mkd_html

import sys

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 md2html [input_file] [output_file]", file = sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        src = f.read()

    out = markdown(src, Mkd_html())
    
    with open(sys.argv[2], 'w') as f:
        f.write(out)

if __name__ == '__main__':
    main()
