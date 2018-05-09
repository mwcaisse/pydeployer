
import subprocess
import os


def build():
    #asume that we are already in the project root for now

    cwd = os.getcwd()
    subprocess.run("dotnet restore")

    #TODO: Make yarn portion configurable
    subprocess.run("yarn install", cwd=os.path.join(cwd, "CarTracker.Web"))

    #TODO: CHange back to the home directory
    subprocess.run("dotnet publish -C Release -o /srv/dotnet/cartracker/tmp/ -r linux-x64")

    return True

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