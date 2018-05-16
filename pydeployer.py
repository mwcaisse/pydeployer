import json
import os

from builder import Builder


def load_config():
    if not os.path.isfile("config.json"):
        print("Could not load config file.")
        return None
    with open("config.json") as config_file:
        config = json.load(config_file)

    return config


def main():
    config = load_config()
    if config:
        builder = Builder(load_config())
        builder.build()


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