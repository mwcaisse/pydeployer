import subprocess
import os
import json
import shutil
import time
import copy
import datetime
from util import create_zip_file
from token_replacer import translate_tokenized_files


class Builder:

    def __init__(self, config, tokens):
        self.config = config
        self.workspace_root = os.getcwd()
        self.tokens = tokens

    def build(self):
        #asume that we are already in the project root for now
        cwd = self.workspace_root
        root_directory = os.path.join(cwd, self.config["name"])
        build_directory = os.path.join(cwd, "build")

        #replace any tokenized build files
        translate_tokenized_files(root_directory, ".ptb", self.tokens)

        if not os.path.isdir(root_directory):
            print("Could not find project directory. Please make sure project name matches its directory name.")
            return False

        subprocess.run("dotnet restore", shell=True, cwd=root_directory)

        #meta data for the build
        metadata = {
            "uuid": self.config["uuid"],
            "name": self.config["name"],
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

                print("Building web project " + project["name"])
                print("Running: dotnet publish -c Release -o {0} -r linux-x64".format(os.path.join(build_directory, "web")))

                subprocess.run("dotnet publish -c Release -o {0} -r linux-x64"
                               .format(os.path.join(build_directory, "web")), shell=True,
                               cwd=os.path.join(root_directory, project["name"]))

                metadata["web"] = {
                    "moduleName": project.get("moduleName", project.get("name")),
                    "serviceName": project.get("serviceName", project.get("name"))
                }

            elif project.get("type") == "web-static":
                #TODO: We should share the package manager + webpack commands with web type project
                if project.get("packageManager") == "yarn":
                    subprocess.run("yarn install", shell=True,
                                   cwd=os.path.join(root_directory, project["name"]))

                if project.get("webpack", False):
                    subprocess.run("webpack", shell=True,
                                   cwd=os.path.join(root_directory, project["name"]))

                if not project.get("gulpCommand"):
                    print("Currently web-static only supports building with gulp. You must supply a gulp command.")
                    return False

                subprocess.run("gulp {target}".format(target=project.get("gulpCommand")), shell=True,
                               cwd=os.path.join(root_directory, project["name"]))

                shutil.copytree(os.path.join(root_directory, project["name"], project.get("distDirectory", "dist")),
                                os.path.join(build_directory, "web-static"))

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
        zipfile = "{0}-{1}.pydist".format(
            self.config["name"],
            self.config["build_version"])
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
            "build_version": self.config["build_version"]
        }

        with open(os.path.join(directory, "build_tokens.json"), "w") as tokens_file:
            json.dump(tokens, tokens_file)

        return tokens

    def save_metadata(self, directory, metadata):
        with open(os.path.join(directory, "metadata.json"), "w") as metadata_file:
            json.dump(metadata, metadata_file)



