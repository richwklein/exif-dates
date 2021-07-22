import argparse
import os
import subprocess
from datetime import datetime, timedelta
from datetime import date
from datetime import time

FILE_EXTENSIONS = ("mp4", "lrv", "jpg", "thm")
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "{} %H:%M:%S".format(DATE_FORMAT)
GET_DATE_PROCESS = 'exiftool -d "{0}" -CreateDate -S -s "{1}"'
DEFAULT_TIME = time(12,0,0)
SET_DATE_PROCESS = 'exiftool -AllDates="{0}" -TrackCreateDate="{0}" -TrackModifyDate="{0}" -MediaCreateDate="{0}" -MediaModifyDate="{0}" -overwrite_original "{1}";'

""" 
directory="$1";
echo "Processing '$directory'";
date_change="$2";
echo "Change '$date_change'";
 
find "$directory" \( -iname "*.mp4" -o -iname "*.lrv" -o -iname "*.jpg" -o -iname "*.thm" \) -type f -execdir sh -c '
    image=$1;
    echo "$image ";
    old_date=`exiftool -d "%a %b %d %T %Z %Y" -CreateDate -S -s "$image"`;
    echo -e "\t$old_date";
    new_date=`date -d "$old_date $date_change"`;
    echo -e "\t$new_date";
    formated_date=`date "+%Y:%m:%d %H:%M:%S %Z" -d "$new_date"`;
    echo -e "\t$formated_date";
    exiftool "-AllDates=$formated_date" "-TrackCreateDate=$formated_date" "-TrackModifyDate=$formated_date" "-MediaCreateDate=$formated_date" "-MediaModifyDate=$formated_date" -overwrite_original "$image";
' _ '{}' \;
"""

def process_file(path, new_date, time_delta, dry_run):
    print("Processing: {}".format(path))

    # Get the original date
    output = subprocess.check_output(GET_DATE_PROCESS.format(DATETIME_FORMAT, path), stderr=subprocess.STDOUT, shell=True)
    created_exif = output.rstrip().decode("utf-8")
    try:
        created_datetime = datetime.strptime(created_exif, DATETIME_FORMAT)
    except Exception as e:
        created_datetime = None

    if created_datetime is None:
        new_datetime = datetime.combine(new_date, DEFAULT_TIME)
    else:
        new_datetime = datetime.combine(new_date, created_datetime.time()) + timedelta(seconds=time_delta*60)

    print("Setting date from: {} to: {}".format(created_datetime, new_datetime))
    if not dry_run:
        output = subprocess.check_output(SET_DATE_PROCESS.format(new_datetime.strftime(DATETIME_FORMAT), path), stderr=subprocess.STDOUT, shell=True)
        print(output.rstrip().decode("utf-8"))


def process_media(directory, new_date, time_delta, dry_run):
    print("Scanning for media in: {}".format(directory))

    for root, dirs, files in os.walk(directory, topdown = True):
        for name in files:
            extension = name.split(".")[-1]
            if extension.lower() in FILE_EXTENSIONS:
                path = os.path.join(directory, root, name)
                process_file(path, new_date, time_delta, dry_run)


def main():
    parser = argparse.ArgumentParser(description='Process a directory of images and update the exif dates.')
    parser.add_argument('directory', type=str, help='Full path to the directory to process.')
    parser.add_argument('--date', type=str, help='New date in the YYYY-MM-DD format.', default=datetime.now().strftime(DATE_FORMAT))
    parser.add_argument('--delta', type=int, help='Time delta in minutes.', default=0)
    parser.add_argument('--dry', action="store_true")
    
    args = parser.parse_args()
    new_date = datetime.strptime(args.date, DATE_FORMAT).date()

    print("Setting new dates to '{}' with time delta {}".format(new_date, args.delta))

    process_media(args.directory, new_date, args.delta, args.dry)


if __name__ == "__main__":
    # execute only if run as a script
    main()

    