#!/usr/bin/env python3

import argparse
import os
import shutil

from builder import Builder
from database_deployer import FlywayDatabaseDeployer
from token_fetcher import TokenFetcher
from web_deployer import WebDeployer
from web_static_deployer import WebStaticDeployer
from util import extract_zipfile, get_directories_in_directory, load_json_file, load_config, pretty_string_to_bool


def build(options):
    config = load_config(options.config_file)
    tokens = TokenFetcher(config).fetch_build_tokens()

    #TODO: Why are we loading the conig here vs passing in the config file path?
    project_config = load_config(options.project_config)
    project_config["build_number"] = options.build_number
    if project_config:
        builder = Builder(project_config, tokens)
        builder.build()


def deploy(options):
    #Load the pydeployer config
    config = load_config(options.config_file)

    zipfile_name = os.path.basename(options.deploy_file)
    project_name = zipfile_name.split(".")[0].lower()  # TODO: only allow one dot for now

    staging_dir = os.path.join(os.getcwd(), project_name + "_pkg")
    os.makedirs(staging_dir)

    # Extract the zip file
    print("Deploy: Extracting zipfile {zipfile} to {staging_dir}".format(
        zipfile=options.deploy_file,
        staging_dir=staging_dir
    ))
    extract_zipfile(options.deploy_file, staging_dir)

    # Load up the metadata file
    metadata_file = os.path.join(staging_dir, "metadata.json")
    if os.path.isfile(metadata_file):
        metadata = load_json_file(metadata_file)
    else:
        raise Exception("Unable to load package metadata!")

    #Fetch the tokens
    # if there was a token file specified as a parameter use the tokens from there
    # otherwise use the token service
    if getattr(options, "tokens_file", None):
        tokens = load_json_file(options.tokens_file)
    else:
        tokens = TokenFetcher(config).fetch_deploy_tokens(metadata["uuid"])

    # Populate build tokens in tokens file if they exist
    build_tokens_file = os.path.join(staging_dir, "build_tokens.json")
    if os.path.isfile(build_tokens_file):
        build_tokens = load_json_file(build_tokens_file)
        tokens.update(build_tokens)

    # Run through each of the projects in the zip
    #   Have a config file or just use folder names?

    directories = get_directories_in_directory(staging_dir)
    print("Deploy: Parsing directories {0}".format(directories))

    # Store the dictionary for the output paths for each different target type
    target_outputs = {}

    # If output path is defined in the config, use it as the default output directory
    if "output_path" in config:
        target_outputs[None] = config["output_path"]

    # If targets have been specified in the config, load them
    if "targets" in config:
        target_outputs.update(config["targets"])

    def get_output_path_for_target(target):
        if target in target_outputs:
            return target_outputs[target]
        if None in target_outputs:
            return target_outputs[None]
        raise Exception("No output path defined for target {target}".format(target=target))

    for directory in directories:
        if directory == "database":
            print("Deploy: Starting deploying database.")

            project_config = metadata.get("database", {})
            scripts_directory = os.path.join(staging_dir, directory, project_config.pop("scriptDirectory", "scripts"))
            db_config = create_database_config(tokens, scripts_directory)

            deployer = FlywayDatabaseDeployer(db_config)
            # TODO: Do some sort of error handling? Otherwise we have no idea if database deploy was successful or not
            deployer.deploy()

            print("Deploy: Ended deploying database.")

        elif directory == "web":
            project_config = metadata.get("web", {})
            project_directory = os.path.join(staging_dir, directory)
            deploy_dir = os.path.join(get_output_path_for_target(project_config.get("target", directory)), project_name)

            deployer = WebDeployer(dict())
            deployer.deploy(project_directory, deploy_dir, tokens, project_name, project_config)

            print("Deploy: Ended deploying web.")

        elif directory == "web-static":
            project_config = metadata.get("web", {})
            project_directory = os.path.join(staging_dir, directory)
            if pretty_string_to_bool(project_directory.get("deploy_as_root", "false")):
                #If Deploy as Root is set, then we just deploy directly to the output directory
                deploy_dir = get_output_path_for_target(project_config.get("target", directory))
            else:
                deploy_dir = os.path.join(get_output_path_for_target(project_config.get("target", directory)), project_name)

            deployer = WebStaticDeployer(dict())
            deployer.deploy(project_directory, deploy_dir, tokens, project_name, project_config)


    # delete staging directory once done
    shutil.rmtree(staging_dir)


def create_database_config(tokens, scripts_directory):
    config = {
        "user": tokens.get("database_deploy_user") or tokens["database_user"],
        "password": tokens.get("database_deploy_password") or tokens["database_password"],
        "host": tokens["database_host"],
        "port": tokens["database_port"],
        "schema": tokens["database_schema"],
        "scripts_directory": scripts_directory
    }
    return config


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="build",
                        help="Command to execute: build, deploy. default: build")
    parser.add_argument("deploy_file", nargs="?", default=None,
                        help="File to deploy. Required if deploy is specified as command")
    parser.add_argument("-b", "--build-number", dest="build_number", default="0")
    parser.add_argument("-c", "--config-file", dest="config_file", default="/opt/pydeployer/conf/config.yaml",
                        help="Location of the pydeployer configuration file")
    parser.add_argument("-p", "--project-config", dest="project_config", default="config.yaml",
                        help="Location of the project's config file. default: config.yaml")
    parser.add_argument("-d", "--project-directory", dest="project_directory", default=None)
    parser.add_argument("-t", "--tokens-file", dest="tokens_file", default=None,
                        help="Path to the file containing the deployment tokens")
    parser.add_argument("-u", "--build-tokens-file", dest="build_tokens_file", default=None,
                        help="Path to the file containing the build tokens")

    args = parser.parse_args()

    if args.command == "build":
        build(args)
    elif args.command == "deploy":
        if not args.deploy_file:
            print("Deploy file is required.")
        else:
            deploy(args)
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
