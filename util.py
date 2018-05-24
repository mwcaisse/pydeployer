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
        full_path = os.path.join(directory, file)
        if os.path.isdir(full_path):
            if relative:
                directories.append(file)
            else:
                directories.append(full_path)

    return directories


def get_files_matching_pattern(directory, pattern, relative=True):
    files = []

    pattern = re.compile(pattern)
    for file_name in os.listdir(directory):
        full_path = os.path.join(directory, file_name)
        if os.path.isfile(full_path) and pattern.match(file_name):
            if relative:
                files.append(file_name)
            else:
                files.append(full_path)

    return files
