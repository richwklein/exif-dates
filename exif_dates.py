import argparse
import glob
import os
import logging
import subprocess
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from datetime import date
from datetime import time

FILE_EXTENSIONS = ("mp4", "lrv", "jpg", "thm")
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "{} %H:%M:%S".format(DATE_FORMAT)
GET_DATE_PROCESS = 'exiftool -d "{0}" -CreateDate -S -s "{1}"'
DEFAULT_TIME = time(12,0,0)
SET_DATE_PROCESS = 'exiftool -AllDates="{0}" -TrackCreateDate="{0}" -TrackModifyDate="{0}" -MediaCreateDate="{0}" -MediaModifyDate="{0}" -overwrite_original "{1}";'

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def insensitive_glob(directory, ext):
    """
    Implements a case insensitive glob to find files of a given extension in a directory.
    """
    def either(c):
        return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c
    return glob.glob('{0}/*.{1}'.format(directory, ''.join(map(either, ext))))


def has_exiftool():
    """
    Check to see if the commandline exiftool can be executed.
    """
    return shutil.which("exiftool") is not None


def process_file(path, new_date, time_delta, dry_run):
    """
    Extracts the dates from the file. It then merges the new date with the old date's timedelta 
    and overwrites all the exif dates. 
    """
    logging.info("Processing: {}".format(path))

    # Get the original date by pulling the CreateDate tag in the desired format
    output = subprocess.check_output(GET_DATE_PROCESS.format(DATETIME_FORMAT, path), stderr=subprocess.STDOUT, shell=True)
    created_exif = output.rstrip().decode("utf-8")
    try:
        created_datetime = datetime.strptime(created_exif, DATETIME_FORMAT)
    except Exception as e:
        created_datetime = None

    # Calculate the new date and time
    if created_datetime is None:
        new_datetime = datetime.combine(new_date, DEFAULT_TIME)
    else:
        new_datetime = datetime.combine(new_date, created_datetime.time()) + timedelta(seconds=time_delta*60)

    # Replace the all the known date tags with new ones and overwrite the file
    logging.info("Setting date from: {} to: {}".format(created_datetime, new_datetime))
    if not dry_run:
        output = subprocess.check_output(SET_DATE_PROCESS.format(new_datetime.strftime(DATETIME_FORMAT), path), stderr=subprocess.STDOUT, shell=True)
        logging.debug(output.rstrip().decode("utf-8"))


def process_files(directory, new_date, time_delta, dry_run):
    """
    Scan the given directory for the files we are interested in.
    """
    logging.info("Scanning for media in: {}".format(directory))

    for ext in FILE_EXTENSIONS:
        for path in insensitive_glob(directory, ext):
            process_file(path, new_date, time_delta, dry_run)


def main():
    """
    Parse the command line arguments and execute if the exiftool is found. 
    """
    parser = argparse.ArgumentParser(description='Process a directory of images and update the exif dates.')
    parser.add_argument('directory', type=str, help='Full path to the directory to process.')
    parser.add_argument('--date', type=str, help='New date in the YYYY-MM-DD format.', default=datetime.now().strftime(DATE_FORMAT))
    parser.add_argument('--delta', type=int, help='Time delta in minutes.', default=0)
    parser.add_argument('--dry', help="Execute as a dry run with no updates.", action="store_true")
    
    if not has_exiftool():
        sys.exit("exiftool was not found")
    
    args = parser.parse_args()
    new_date = datetime.strptime(args.date, DATE_FORMAT).date()

    logging.info("Setting new dates to '{}' with time delta {}".format(new_date, args.delta))

    process_files(args.directory, new_date, args.delta, args.dry)
    sys.exit(0)

if __name__ == "__main__":
    # execute only if run as a script
    main()

    