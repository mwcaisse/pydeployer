import subprocess
import os
from zipfile import ZipFile

def build():
    #asume that we are already in the project root for now

    cwd = os.getcwd()
    subprocess.run("dotnet restore")

    #TODO: Make yarn portion configurable
    subprocess.run("yarn install", cwd=os.path.join(cwd, "CarTracker.Web"))

    #TODO: CHange back to the home directory
    subprocess.run("dotnet publish -C Release -o /srv/dotnet/cartracker/tmp/ -r linux-x64")

    return True


def package():
    zipfile = "CarTracker.pydist"
    create_zip_file("/srv/dotnet/cartracker/tmp/", zipfile)


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
            zip.write(file)


def main():
    build()
    package()


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