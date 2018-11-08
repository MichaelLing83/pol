#! /usr/bin/env python
import logging
from enum import Enum
import re

VERSION: str = '0.0.2'
NAME: str = 'Python3 One-Liner'

DEFAULT_LOGGING_FORMAT: str = '%(relativeCreated)6d [%(processName)-10.10s]' \
                              '[%(name)10.10s][%(lineno)3d][%(levelname)4.4s] %(message)s'


def config_logging(verbosity: int):
    """
    Configure logging level from number of -v given in command line arguments.
    :param verbosity: integer, number of -v given in command line
    :return: None
    """

    _logging_lvls = [logging.DEBUG, logging.INFO,
                     logging.WARNING, logging.ERROR,
                     logging.FATAL, logging.CRITICAL]
    _log_lvl: int = len(_logging_lvls) - 1
    _log_lvl_idx: int = _log_lvl - verbosity
    if _log_lvl_idx < 0:
        _log_lvl_idx = 0

    logging.basicConfig(level=_logging_lvls[_log_lvl_idx],
                        format=DEFAULT_LOGGING_FORMAT)


class ContextVarNameE(Enum):
    LINE = '_l'
    LINE_NO = '_lno'
    BUFFER = '_buf'
    FILE_NAME = '_fn'
    FILE_PATH = '_fp'


class Context(dict):
    def __init__(self):
        super().__init__()
        for _var_name in ContextVarNameE:
            self[_var_name.value] = None
        self[ContextVarNameE.BUFFER] = {}
        self['re'] = re


if __name__ == '__main__':
    import argparse
    import sys
    import pathlib

    _parser = argparse.ArgumentParser()
    _parser.add_argument("-l", "--line", required=False,
                         help="Python 3 expression to run per input line.",
                         type=str,
                         default='pass')
    _parser.add_argument("--version",
                         help="Print version and exit.",
                         action='count',
                         default=0)
    _parser.add_argument("-v", "--verbose",
                         help="Increase logging verbosity.",
                         action='count',
                         default=0)
    _parser.add_argument('-rfp', '--read_file_paths',
                         help="Read file path from stdin, one per line.",
                         action='count',
                         default=0)

    args = _parser.parse_args()

    config_logging(args.verbose)

    _logger: logging.Logger = logging.getLogger()

    args.line = compile(args.line, filename='<string>', mode='exec')

    if args.version:
        print(f"{pathlib.Path(__file__).name} ({NAME}) {VERSION}")
        sys.exit(0)

    if args.read_file_paths:
        _logger.info(f"Read file path from stdin, one per line.")
        for _file_path in sys.stdin:
            _file_path = _file_path.strip()
            _logger.debug(f"_file_path={_file_path}")
            if not pathlib.Path(_file_path).exists():
                _logger.warning(f"{_file_path} does not exist!")
            elif not pathlib.Path(_file_path).is_file():
                _logger.warning(f"{_file_path} is not a file!")
            else:
                # new context for each file processed
                _context: Context = Context()
                _context[ContextVarNameE.FILE_PATH.value] = _file_path
                _context[ContextVarNameE.FILE_NAME.value] = pathlib.Path(_file_path).name
                _context[ContextVarNameE.LINE_NO.value] = 0
                with open(_file_path, 'r') as _f:
                    for line in _f:
                        _context[ContextVarNameE.LINE.value] = line
                        _logger.debug(f"_context={_context}")
                        exec(args.line, _context)
                        _context[ContextVarNameE.LINE_NO.value] += 1
    else:
        # read lines from stdin
        _context: Context = Context()
        _context[ContextVarNameE.FILE_NAME.value] = 'stdin'
        _context[ContextVarNameE.FILE_PATH.value] = ''
        for line in sys.stdin:
            _context[ContextVarNameE.LINE.value] = line
            exec(args.line, _context)
            _context[ContextVarNameE.LINE_NO.value] += 1
