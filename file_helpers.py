import os
import default_parsers
from zipfile import ZipFile
from datetime import datetime
import logging

tilde = os.environ['HOME']

def interpret_tilde(filename):
    if filename[0] == '~':
        filename = tilde + filename[1:]
    return filename


def file_exists(filename):
    return os.path.isfile(interpret_tilde(filename))


def file_is_writeable(filename):
    """
    * Check if it is possible to create / write to a file with given filename
    * Returns True if file doesn't already exist
    """
    filename = interpret_tilde(filename)
    if file_exists(filename):
        return os.access(filename, os.W_OK)
    # file doesn't exist
    return True


def file_is_readable(filename):
    """
    * Return True if file exists and can be read
    * Returns False if file doesn't exist
    """
    filename = interpret_tilde(filename)
    if file_exists(filename):
        return os.access(filename, os.R_OK)
    # file doesn't exist
    return False


def get_file_extension(filename : str):
    period_index = -1
    for i, letter in enumerate(filename):
        if letter == '.':
            period_index = i
    if period_index == -1:
        return ''
    return filename[period_index:]


def get_filename_wo_ext(filename : str):
    splitted = filename.split('.')
    if len(splitted) > 1:
        splitted.pop()
    return '.'.join(splitted)


def read_first_line(filename):
    if not file_is_readable(filename):
        raise default_parsers.UserInputException(f'File "{filename}" does not exist or this program does not have permission to read it')
    with open(filename, "r") as f:
        return f.readline().rstrip("\n")


def unzip_file(directory, filepath_w_ext, filename):
    '''
    :param directory:        directory to which files will be unzipped
    :param filepath_w_ext:   filepath of zipped file
    :param filename:         desired filename to be applied to all files

    e.g. zipped file "zipped_file" contains files (abc.txt  and  xyz.csv)  and :param filename: is "foo"

    then this function unzips the file, placing the following unzipped files in :param directory:
      foo.txt  and  foo.csv

    To be used in scenarios where we expect only one file to be in the zipped file.
    But, in the case of multiple files, it still works because we uniquely name files by their extension.

    If there are multiple files with the same extension, their original filename is appended to uniquely identify them.
    '''
    og_mtimes = dict({})
    directory = interpret_tilde(directory)
    # filepath = directory + filename_with_ext
    with ZipFile(filepath_w_ext, 'r') as zipdata:
        logging.critical(f"Unzipping  {filepath_w_ext}")
        # List of files in archive
        zipinfos = zipdata.infolist()
        # Get ZipInfo objects which are files and not folders or Mac OSX stuff
        actual_files = get_actual_filenames(zipinfos)

        if len(zipinfos) > len(actual_files):
            logging.warning(f"At least one file from zip file was excluded")

        # Keep track of file extensions which appear more than once
        duplicate_exts = get_duplicate_extensions(actual_files)

        for zipinfo in actual_files:
            extension = get_file_extension(zipinfo.filename)
            orig_filename = get_filename_wo_ext(zipinfo.filename)
            zipinfo.filename = filename
            if extension in duplicate_exts:
                zipinfo.filename +=  f'_DLed-as_{orig_filename}'
            zipinfo.filename += extension

            ######
            og_mtimes[directory + zipinfo.filename] = zipinfo.date_time
            ######
            zipdata.extract(zipinfo, path=directory)
            logging.info(f"Extracted <{zipinfo.filename}> to directory {directory}")
    return og_mtimes
        

def revert_og_mtimes(mtimes : dict):
    """
    :param mtimes: maps filepath to its original mtime
    """
    for filepath in mtimes:
        atime = os.path.getatime(filepath)
        y,mo,d,h,mi,s = mtimes[filepath]
        og_epoch_mtime = int(datetime(y,mo,d,h,mi,s).strftime('%s'))
        os.utime(filepath, (atime, og_epoch_mtime))
        logging.info(f"Reverted mtime of file {filepath}")


def get_actual_filenames(zipinfos : list):
    actual_files = []
    for zipinfo in zipinfos:
        name = zipinfo.filename
        if not (zipinfo.is_dir() or '/' in name):
            actual_files.append(zipinfo)
        else:
            logging.warning(f"Excluded file <{name}> from archive")
    return actual_files


def get_duplicate_extensions(zipinfos : list):
    exts_seen = set({})
    dup_exts = set({})
    for zipinfo in zipinfos:
        name = zipinfo.filename  
        ext = get_file_extension(name)
        if ext in exts_seen:
            dup_exts.add(ext)
        exts_seen.add(ext)
    return dup_exts
