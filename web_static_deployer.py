import os
import shutil

class WebStaticDeployer:

    def __init__(self, config):
        self.config = config

    def deploy(self, staging_directory, deploy_directory, tokens, project_name, project_metadata):
        """

        :param staging_directory: Directory that the built files are staged in
        :param deploy_directory: Directory to deploy the build to
        :param tokens: The tokens for the application to apply
        :param project_name: The name of the project
        :param project_metadata: Configuration/metadata associated with the project
        :return:
        """

        # make sure the deploy directory exists, if it doesn't create it
        print("WebStaticDeploy: Creating Deploy directory")
        if not os.path.exists(deploy_directory):
            os.makedirs(deploy_directory)

        # Simply clear the deploy directory then copy everything from the staging directory to the deploy directory
        shutil.rmtree(deploy_directory)
        shutil.copytree(staging_directory, deploy_directory)
