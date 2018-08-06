import argparse
import os

from builder import Builder
from database_deployer import FlywayDatabaseDeployer
from token_fetcher import TokenFetcher
from web_deployer import WebDeployer
from util import extract_zipfile, get_directories_in_directory, load_config


def build(options):
    config = load_config(options.project_config)
    config["build_number"] = options.build_number
    if config:
        builder = Builder(config)
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
        metadata = load_config(metadata_file)

    #Fetch the tokens
    tokens = TokenFetcher(config).fetch_tokes(metadata["uuid"])

    # Populate build tokens in tokens file if they exist
    build_tokens_file = os.path.join(staging_dir, "build_tokens.json")
    if os.path.isfile(build_tokens_file):
        build_tokens = load_config(build_tokens_file)
        tokens.update(build_tokens)

    # Run through each of the projects in the zip
    #   Have a config file or just use folder names?

    directories = get_directories_in_directory(staging_dir)
    print("Deploy: Parsing directories {0}".format(directories))

    for directory in directories:
        if directory == "database":
            print("Deploy: Starting deploying database.")

            config_file = os.path.join(staging_dir, directory, "config.json")
            project_config = load_config(config_file)
            scripts_directory = os.path.join(staging_dir, directory, project_config.pop("scriptDirectory", "scripts"))
            db_config = create_database_config(tokens, scripts_directory)

            deployer = FlywayDatabaseDeployer(db_config)
            # TODO: Do some sort of error handling? Otherwise we have no idea if database deploy was successful or not
            deployer.deploy()

            print("Deploy: Ended deploying database.")

        elif directory == "web":
            staging_dir = os.path.join(staging_dir, directory)
            deploy_dir = os.path.join(config["output_path"], project_name)

            deployer = WebDeployer(dict())
            deployer.deploy(staging_dir, deploy_dir, tokens, project_name)


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
    parser.add_argument("-c", "--config-file", dest="config_file", default="/opt/pydeployer/config.json",
                        help="Location of the pydeployer configuration file")
    parser.add_argument("-p", "--project-config", dest="project_config", default="config.json",
                        help="Location of the project's config file. default: config.json")
    parser.add_argument("-d", "--project-directory", dest="project_directory", default=None)
    parser.add_argument("-t", "--tokens-file", dest="tokens_file", default=None,
                        help="Path to the file containing the deployment tokens")

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