import subprocess
import os
import json
import shutil
from zipfile import ZipFile


class Deployer:

    def __init__(self, config):
        self.config = config

    def build(self):
        #asume that we are already in the project root for now
        cwd = os.getcwd()
        root_directory = os.path.join(cwd, self.config["name"])
        build_directory = os.path.join(cwd, "build")

        subprocess.run("dotnet restore", shell=True, cwd=root_directory)

        # Perform any project specific build steps
        for project in self.config["subProjects"]:
            if project.get("type") == "web":
                if project.get("packageManager") == "yarn":
                    subprocess.run("yarn install", shell=True,
                                   cwd=os.path.join(root_directory, project["name"]))

                subprocess.run("dotnet publish -c Release -o {0} -r linux-x64"
                               .format(os.path.join(build_directory, "web")), shell=True,
                               cwd=os.path.join(root_directory, project["name"]))

            elif project.get("type") == "database":
                script_directory = os.path.join(root_directory, project.get("name"), project.get("scriptDirectory"))
                shutil.copytree(script_directory, os.path.join(build_directory, "database", "scripts"))

        self.package(build_directory)

    def package(self, build_directory):
        zipfile = "{0}.pydist".format(self.config["name"])
        create_zip_file(build_directory, zipfile)


def get_all_file_paths(directory):
    file_paths = []

    for root, directories, files in os.walk(directory):
        for filename in files:
            file_paths.append(os.path.join(root, filename))

    return file_paths


def create_zip_file(directory, zip_name):
    """ Creates a zipfile of the given directory """

    with ZipFile(zip_name, "w") as zip:
        for file in get_all_file_paths(directory):
            zip.write(file, os.path.relpath(file, directory))


def load_config():
    with open("config.json") as config_file:
        config = json.load(config_file)

    return config


def main():
    deployer = Deployer(load_config())
    deployer.build()


if __name__ == "__main__":
    main()

"""

    - Create a installation/deployment package
        -Output of the compile / build
            -Run the build
            -Copy build output to the resulting zipfile
        -Skeleton config file
        -Database scripts to update

    - Application to perform the deployment
        - Stop the currently running application
        - Copy the build output to the destination
        - Create any needed config files
        - Deploy the database
        - Start the currently running application

    - Web Application to store the configuration
        - Stores the configuration for the application
            - Database connection info
            - API Keys
            - Any environment dependent config
        - API Endpoints to fetch the configuration keys
            -Certificate authentication?
        - UI to add projects and their environment config


    -- Running the build
        - Need to define the build steps / how to actually do the build
        - Different types of projects
            -Web project that needs to download dependencies / perform post processing
            -.NET Projects that need to be built

"""