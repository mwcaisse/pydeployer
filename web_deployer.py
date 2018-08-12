import os
import shutil
import subprocess

from token_replacer import replace_tokens_in_file
from util import get_all_file_paths, empty_directory


class WebDeployer:

    def __init__(self, config):
        self.config = config

    def deploy(self, staging_directory, deploy_directory, tokens, project_name, project_metadata):
        """

            - Apps directory
            - project name
            - Temp directory that contains the extracted package
            - tokens to translate the pyb files
            - name of the project

        :return:
        """

        service_name = project_metadata.get("serviceName", project_name)

        # End the service before we start the deploy
        print("WebDeploy: Stopping service...")
        self.stop_service(service_name)

        # make sure the publish directory exists, if it doesn't create it
        print("WebDeploy: Creating Publish directory")
        publish_directory = os.path.join(deploy_directory, "publish")
        if not os.path.exists(publish_directory):
            os.makedirs(publish_directory)

        # copy from the staging directory into the publish directory
        print("WebDeploy: Copying files to publish directory")
        shutil.rmtree(publish_directory)
        shutil.copytree(staging_directory, publish_directory)

        # create the run script
        run_file_path = self.create_run_script(deploy_directory, publish_directory,
                                               project_metadata, tokens)

        # Create the service file
        if not run_file_path:
            print("Creating service file without run path defined.")
        self.create_service_file(deploy_directory, publish_directory, service_name, run_file_path or "")

        # perform the tokenizer filling, if it throws an error, let it raise up..
        print("WebDeploy: Translating pyb files")
        self.translate_pyb_files(publish_directory, tokens)

        # Restart the service when we are done with deploy
        print("WebDeploy: Starting service...")
        self.start_service(service_name)

    def translate_pyb_files(self, staging_directory, tokens):
        pyb_files = get_all_file_paths(staging_directory, lambda filename: filename.endswith(".pyb"))
        for file in pyb_files:
            out_file = file.replace(".pyb", ".json")

            replace_tokens_in_file(file, tokens, out_file=out_file, delete_after=True)

    def create_run_script(self, deploy_directory, publish_directory, metadata, project_tokens):
        cont = True
        if "moduleName" not in metadata:
            print("Unable to create run script. No moduleName defined.")
            cont = False

        if "web_port" not in project_tokens:
            print("Unable to create run script. No web port defined.")
            cont = False

        if not cont:
            return

        tokens = {
            "port": project_tokens["web_port"],
            "publish_dir": publish_directory,
            "module_name": metadata["moduleName"]
        }
        template_file = self.get_template_file("run.sh.pyb")
        run_file = os.path.join(deploy_directory, "run.sh")
        replace_tokens_in_file(template_file, tokens, out_file=run_file, delete_after=False)

        subprocess.run("chmod a+x {0}".format(run_file), shell=True)

        return run_file

    def create_service_file(self, deploy_directory, publish_directory, service_name, run_script):
        tokens = {
            "project_name": service_name.title(),
            "publish_dir": publish_directory,
            "run_script": run_script
        }
        template_file = self.get_template_file("service.pyb")

        out_file = os.path.join(deploy_directory, "{0}.service".format(service_name))
        replace_tokens_in_file(template_file, tokens, out_file=out_file, delete_after=False)

    def get_template_file(self, name):
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates/{name}".format(name=name))

    def start_service(self, name):
        subprocess.run("sudo systemctl start {0}".format(name), shell=True)

    def stop_service(self, name):
        subprocess.run("sudo systemctl stop {0}".format(name), shell=True)
