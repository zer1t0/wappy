import os
import logging
import requests
import argparse
import hashlib

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()

    source_group = parser.add_mutually_exclusive_group()

    source_group.add_argument(
        "-u", "--url",
        help="URL to retrieve the technologies file",
        default="https://raw.githubusercontent.com/AliasIO/wappalyzer/master/src/technologies.json"
    )

    source_group.add_argument(
        "-f", "--file",
        help="File with technologies regexps",
        type=argparse.FileType('rb'),
    )

    parser.add_argument(
        "-c", "--check",
        action="store_true",
        help="Just check if update is required, without update",
    )

    parser.add_argument(
        "-v",
        dest="verbosity",
        help="Verbosity",
        action="count",
        default=0,
    )

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    init_log(args.verbosity)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    target_file = os.path.join(script_dir, "technologies.json")

    current_md5 = get_file_md5(target_file)
    logger.info("Current file MD5: %s", current_md5)

    if args.file:
        content = args.file.read()
    else:
        try:
            res = requests.get(args.url)
            content = res.content
        except Exception as ex:
            logger.error("Error retrieving file from '%s': %s", args.url, ex)
            return -1

    new_md5 = md5(content)
    logger.info("New file MD5: %s", new_md5)

    if current_md5 != new_md5:
        if args.check:
            print("Update required")
        else:
            update_file(target_file, content)
            print("Update successful")
    else:
        print("No update required")


def init_log(verbosity=0, log_file=None):

    if verbosity == 1:
        level = logging.WARN
    elif verbosity == 2:
        level = logging.INFO
    elif verbosity > 2:
        level = logging.DEBUG
    else:
        level = logging.CRITICAL

    logging.basicConfig(
        level=level,
        filename=log_file,
        format="%(levelname)s:%(name)s:%(message)s"
    )


def update_file(filepath, content):
    with open(filepath, 'wb') as fo:
        fo.write(content)


def get_file_md5(filepath):
    with open(filepath, 'rb') as fi:
        return md5(fi.read())


def md5(content):
    md5_hash = hashlib.md5()
    md5_hash.update(content)
    return md5_hash.hexdigest()


if __name__ == '__main__':
    exit(main())
