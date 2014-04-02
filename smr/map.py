#!/usr/bin/env python
import os
import sys
import tempfile

from .shared import get_config
from .uri import get_download_method

def write_to_stderr(prefix, file_name):
    sys.stderr.write("{0}{1}\n".format(prefix, file_name))
    sys.stderr.flush()

def main():
    config = get_config()

    try:
        for uri in iter(sys.stdin.readline, ""):
            uri = uri.rstrip() # remove trailing linebreak
            temp_file, temp_filename = tempfile.mkstemp()
            dl = get_download_method(config, uri)
            try:
                dl(temp_filename)
                config.MAP_FUNC(temp_filename)
                write_to_stderr("+", uri)
            except (KeyboardInterrupt, SystemExit):
                sys.stderr.write("map worker {0} aborted\n".format(os.getpid()))
                sys.exit(1)
            except Exception as e:
                sys.stderr.write("{0}\n".format(e))
                write_to_stderr("!", uri)
            finally:
                os.close(temp_file)
                os.unlink(temp_filename)
    except (KeyboardInterrupt, SystemExit):
        sys.stderr.write("map worker {0} aborted\n".format(os.getpid()))
        sys.exit(1)
