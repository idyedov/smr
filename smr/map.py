#!/usr/bin/env python
import boto
from boto.s3.key import Key
import logging
import os
import sys
import tempfile

from .shared import get_config, configure_logging

def main():
    if len(sys.argv) < 2:
        sys.stderr.write("usage: smr-map config.py\n")
        sys.exit(1)

    config = get_config(sys.argv[1])
    configure_logging(config)

    try:
        s3conn = boto.connect_s3(config.AWS_ACCESS_KEY, config.AWS_SECRET_KEY)
        bucket = s3conn.get_bucket(config.S3_BUCKET_NAME)
        for file_name in sys.stdin:
            k = Key(bucket)
            file_name = file_name.rstrip() # remove trailing linebreak
            k.key = file_name
            temp_file, temp_filename = tempfile.mkstemp()
            tries = 0
            while True:
                try:
                    k.get_contents_to_filename(temp_filename)
                except Exception as e:
                    tries += 1
                    if tries >= config.DOWNLOAD_RETRIES:
                        logging.error("could not download file %s after %d tries", file_name, tries)
                        raise e
                else:
                    break
            try:
                config.MAP_FUNC(temp_filename)
            finally:
                os.close(temp_file)
                os.unlink(temp_filename)
    except (KeyboardInterrupt, SystemExit):
        logging.error("map worker %d aborted", os.getpid())
        sys.exit(1)
