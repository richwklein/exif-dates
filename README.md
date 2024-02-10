# exif-dates

This is a python script for updating the <abbr title="Exchangeable image file format">EXIF</abbr> dates on a directory of media files. The script is a simple wrapper around the command line [ExifTool](https://exiftool.org/).

The exif dates script scans the desired directory finding all *mp4*, *lrv*, *jpg*, and *thm* files. It thens extracts the CreateDate from the EXIF metadata of those files and gets the timestamp from them. It adds the desired delta to the time and then sets all the metadata dates to the new date with updated timestamp.

## Executing

Put all the files you want to update in a directory making a backup of them. Then call the script from the commandline. First call it with the `dry` argument to see what the new dates will be without actually doing the update.

```shell
python exif_dates.py --directory="/videos" --date="2024-02-10" --delta=60 --dry
```

Adjust the arguments as needed then drop the `dry` to do the actual update.

Valid arguments are:

- directory: Full path to the directory to process.
- date: New date in the YYYY-MM-DD format.
- delta: Time delta in minutes.
- dry: Execute as a dry run with no updates.
