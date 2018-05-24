import argparse
import json
import os
import shutil
import subprocess

from builder import Builder
from database_deployer import FlywayDatabaseDeployer
from token_replacer import replace_tokens_in_file
from util import extract_zipfile, get_directories_in_directory, empty_directory, get_files_matching_pattern


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
        builder = Builder(config)
        builder.build()


def load_tokens(tokens_file):
    return load_config(tokens_file)


def deploy(options):
    # Load in tokens from a file for now, before our token service is built out
    tokens = load_tokens(options.tokens_file)

    zipfile_name = os.path.basename(options.deploy_file)
    project_name = zipfile_name.split(".")[0].decode("utf-8")  # TODO: only allow one dot for now

    staging_dir = project_name + "_pkg"
    os.makedirs(staging_dir)

    # Extract the zip file
    extract_zipfile(staging_dir, options.deploy_file)

    # Run through each of the projects in the zip
    #   Have a config file or just use folder names?

    for directory in get_directories_in_directory(staging_dir):
        if directory == "database":
            config_file = os.path.join(staging_dir, directory, "config.json")
            project_config = load_config(config_file)
            scripts_directory = os.path.join(staging_dir, directory, project_config.pop("scriptDirectory", "scripts"))
            config = create_database_config(tokens, scripts_directory)

            deployer = FlywayDatabaseDeployer(config)
            # TODO: Do some sort of error handling? Otherwise we have no idea if database deploy was successful or not
            deployer.deploy()

        elif directory == "web":

            # lets check if output-path/project-name/publish exists
            publish_dir = os.path.join(options.output_path, project_name, "publish")
            os.makedirs(publish_dir)

            # end service?
            subprocess.run("sudo systemctl stop {0}".format(project_name), shell=True)

            # Clean out what is currently in publish dir
            empty_directory(publish_dir)

            # Copy project to publish dir
            shutil.copytree(os.path.join(staging_dir, project_name), publish_dir)

            # populate token files
            pyb_files = get_files_matching_pattern(publish_dir, "*.pyb")
            for file in pyb_files:
                out_file = file.replace(".pyb", ".json")
                replace_tokens_in_file(file, tokens, out_file=out_file, delete_after=True)

            # restart service?
            subprocess.run("sudo systemctl start {0}".format(project_name), shell=True)

            pass


def create_database_config(tokens, scripts_directory):
    config = {
        "user": tokens.get("database_deploy_user") or tokens["database_user"],
        "password": tokens.get("database_deploy_password") or tokens["database_password"],
        "host": tokens["database_host"],
        "port": tokens["database_port"],
        "schema": tokens["database_schema"],
        "scripts_directory": tokens["scripts_directory"]
    }
    return config



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="build",
                        help="Command to execute: build, deploy. default: build")
    parser.add_argument("deploy_file", nargs="?", default=None,
                        help="File to deploy. Required if deploy is specified as command")

    parser.add_argument("-c", "--config-file", dest="config_file", default="config.json",
                        help="Location of the project's config file. default: config.json")

    parser.add_argument("-o", "--output-path", dest="output_path", default="/opt/apps/")
    parser.add_argument("-p", "--project-directory", dest="project_directory", default=None)
    parser.add_argument("-t", "--tokens-file", dest="tokens_file", default=None,
                        help="Path to the file containing the deployment tokens")

    args = parser.parse_args()

    if args.command == "build":
        build(args)
    elif args.command == "deploy":
        if not args.deploy_file:
            print("Deploy file is required.")
        else:
            deploy()
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