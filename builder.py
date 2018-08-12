import subprocess
import os
import json
import shutil
import time
import copy
from util import create_zip_file


class Builder:

    def __init__(self, config):
        self.config = config
        self.workspace_root = os.getcwd()

    def build(self):
        #asume that we are already in the project root for now
        cwd = self.workspace_root
        root_directory = os.path.join(cwd, self.config["name"])
        build_directory = os.path.join(cwd, "build")

        if not os.path.isdir(root_directory):
            print("Could not find project directory. Please make sure project name matches its directory name.")
            return False

        subprocess.run("dotnet restore", shell=True, cwd=root_directory)

        #meta data for the build
        metadata = {
            "uuid": self.config["uuid"]
        }

        # Perform any project specific build steps
        for project in self.config["subProjects"]:
            if project.get("type") == "web":
                if project.get("packageManager") == "yarn":
                    subprocess.run("yarn install", shell=True,
                                   cwd=os.path.join(root_directory, project["name"]))

                if project.get("webpack", False):
                    subprocess.run("webpack", shell=True,
                                   cwd=os.path.join(root_directory, project["name"]))

                subprocess.run("dotnet publish -c Release -o {0} -r linux-x64"
                               .format(os.path.join(build_directory, "web")), shell=True,
                               cwd=os.path.join(root_directory, project["name"]))

                metadata["web"] = {
                    "moduleName": project.get("moduleName", project.get("name"))
                }

            elif project.get("type") == "database":
                script_directory = os.path.join(root_directory, project.get("name"), project.get("scriptDirectory"))
                shutil.copytree(script_directory, os.path.join(build_directory, "database", "scripts"))

                database_metadata = copy.deepcopy(project)
                database_metadata["scriptDirectory"] = "scripts"
                metadata["database"] = database_metadata

        self.create_build_tokens(build_directory)
        self.save_metadata(build_directory, metadata)
        self.package(build_directory)

    def package(self, build_directory):
        zipfile = "{0}.pydist".format(self.config["name"])
        create_zip_file(build_directory, zipfile)

    def run_git_command(self, command):
        command = "git -C {0} {1}".format(self.workspace_root, command)
        res = subprocess.run(command, shell=True, cwd=self.workspace_root, stdout=subprocess.PIPE, encoding="UTF-8")
        return str(res.stdout).strip()

    def create_build_tokens(self, directory):
        tokens = {
            "build_date": int(time.time() * 1000),  # seconds to milliseconds
            "build_git_revision": self.run_git_command("rev-list --count HEAD"),
            "build_git_short_hash": self.run_git_command("rev-parse --short HEAD"),
            "build_git_long_hash": self.run_git_command("rev-parse HEAD"),
            "build_git_branch": "master",  # hard coding for life
            "build_number": self.config["build_number"],
        }

        with open(os.path.join(directory, "build_tokens.json"), "w") as tokens_file:
            json.dump(tokens, tokens_file)

    def save_metadata(self, directory, metadata):
        with open(os.path.join(directory, "metadata.json"), "w") as metadata_file:
            json.dump(metadata, metadata_file)



