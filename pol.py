VERSION: str = '0.0.1'
NAME: str = 'Python3 One-Liner'

if __name__ == '__main__':
    import argparse
    import sys

    _parser = argparse.ArgumentParser()
    _parser.add_argument("-r", "--reimport", required=False,
                         help="Re-import from PIR database, i.e. do not do delta update, which is default behavior.",
                         action='count',
                         default=0)
    _parser.add_argument("--version",
                         help="Print version and exit.",
                         action='count',
                         default=0)
    _parser.add_argument("-v", "--verbose",
                         help="Increase logging verbosity.",
                         action='count',
                         default=0)

    args = _parser.parse_args()

    if args.version:
        print(f"{__file__} ({NAME}) {VERSION}")
        sys.exit(0)
