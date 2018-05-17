import argparse
import json
import os

from builder import Builder


def load_config(config_file):
    if not os.path.isfile(config_file):
        print("Could not load config file: {0}.".format(config_file))
        return None
    with open(config_file) as config_file:
        config = json.load(config_file)

    return config


def build(options):
    config = load_config(options.config_file)
    if config:
        builder = Builder(load_config())
        builder.build()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="build", help="Command to execute: build, deploy. default: build")
    parser.add_argument("deploy_file", nargs="?", default=None, help="File to deploy. Required if deploy is specified as command")

    parser.add_argument("-c", "--config-file", dest="config_file", default="config.json",
                        help="Location of the project's config file. default: config.json")

    parser.add_argument("-o", "--output-path", dest="output_path", default="/opt/apps/")
    parser.add_argument("-p", "--project-directory", dest="project_directory", default=None)

    args = parser.parse_args()

    if args.command == "build":
        build(args)
    elif args.command == "deploy":
        if not args.deploy_file:
            print("Deploy file is required.")
        else:
            print("We no deploy for now")
    else:
        print("Unknown command: " + args.command)



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