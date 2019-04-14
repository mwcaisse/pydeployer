import os
import json
import shutil
import yaml
from zipfile import ZipFile


def load_json_file(config_file):
    if not os.path.isfile(config_file):
        print("Could not load config file: {0}.".format(config_file))
        return None
    with open(config_file) as config_file:
        config = json.load(config_file)

    return config

def load_config(config_file):
    if not os.path.isfile(config_file):
        print("Could not load config file: {0}.".format(config_file))
        return None
    with open(config_file) as config_file:
        config = yaml.safe_load(config_file)

    return config


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
        if file.startswith("."):
            # Ignore hidden files
            continue

        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def copytree(src, dest):
    """
        Copies the contents of the source directory into the dest directory. Dest directory must already exist
    :param src:
    :param dest:
    :return:
    """
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)


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

def pretty_string_to_bool(s):
    if isinstance(s, bool):
        return s # If it is already a bool, return its value
    if isinstance(s, int):
        return bool(int)
    if isinstance(s, str):
        s = s.lower()
        if s in {"true", "t", "y", "yes"}:
            return True
        return False

    return False # If it isn't a type we know how to deal with, return False
