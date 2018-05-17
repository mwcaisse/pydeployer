import os
import shutil

from token_replacer import replace_tokens_in_file
from util import get_all_file_paths, empty_directory


class WebDeployer:

    def __init__(self, config):
        self.config = config

    def deploy(self, staging_directory, deploy_directory, tokens):
        """

            - Apps directory
            - project name
            - Temp directory that contains the extracted package
            - tokens to translate the pyb files

        :return:
        """

        # perform the tokenizer filling, if it throws an error, let it raise up..
        self.translate_pyb_files(staging_directory)

        # make sure the publish directory exists, if it doesn't create it
        publish_directory = os.path.join(deploy_directory, "publish")
        if not os.path.exists(publish_directory):
            os.makedirs(publish_directory)

        # copy from the staging directory into the publish directory
        empty_directory(publish_directory)
        shutil.copytree(staging_directory, publish_directory)

    def translate_pyb_files(self, staging_directory, tokens):
        pyb_files = get_all_file_paths(staging_directory, lambda filename: filename.endswith(".pyb"))
        for file in pyb_files:
            out_file = file.replace(".pyb", ".json")

            replace_tokens_in_file(file, tokens, out_file=out_file, delete_after=True)

