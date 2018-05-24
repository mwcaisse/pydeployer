import os
import re
import shutil
from zipfile import ZipFile


def get_all_file_paths(directory, condition=None):
    file_paths = []

    for root, directories, files in os.walk(directory):
        for filename in files:
            if not condition or condition(filename):
                file_paths.append(os.path.join(root, filename))

    return file_paths


def create_zip_file(directory, zip_name):
    """ Creates a zipfile of the given directory """

    with ZipFile(zip_name, "w") as zip:
        for file in get_all_file_paths(directory):
            zip.write(file, os.path.relpath(file, directory))


def extract_zipfile(zip_file, destination):
    """ Extracts the given zipfile to the given directory"""
    with ZipFile(zip_file, "r") as zip:
        zip.extractall(destination)


def empty_directory(directory):
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def get_directories_in_directory(directory, relative=True):
    directories = []

    for file in os.listdir(directory):
        if os.path.isdir(file):
            path = file
            if relative:
                path = os.path.relpath(path, directory)
            directories.append(path)

    return directories


def get_files_matching_pattern(directory, pattern):
    files = []

    pattern = re.compile(pattern)
    for file in os.listdir(directory):
        if os.path.isfile(file) and pattern.match(file):
            files.append(os.path.relpath(file, directory))

    return files
