#! /usr/bin/env python
import logging

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


def build_var_dict(_line_no: int,
                   _buffer: dict,
                   _fname: str,
                   _fpath: str) -> dict:
    return {
        '_line_no': _line_no,
        '_buffer': _buffer,
        '_fname': _fname,
        '_fpath': _fpath,
    }


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

    _line_no: int = 0
    _buffer: dict = dict()
    _fname: str = str(sys.stdin)
    _fpath: str = _fname
    _var_dict: dict = {
        '_line_no': _line_no,
        '_buffer': _buffer,
        '_fname': _fname,
        '_fpath': _fpath,
    }
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
                _fpath = _file_path
                _fname = pathlib.Path(_file_path).name
                _line_no = 0
                with open(_file_path, 'r') as _f:
                    for line in _f:
                        _var_dict['line'] = line
                        exec(args.line, build_var_dict(_line_no, _buffer, _fname, _fpath))
                        _line_no += 1
    else:
        # read lines from stdin
        for line in sys.stdin:
            _var_dict['line'] = line
            exec(args.line, build_var_dict(_line_no, _buffer, _fname, _fpath))
            _line_no += 1
