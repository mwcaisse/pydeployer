import subprocess


class FlywayDatabaseDeployer:

    def __init__(self, config):
        self.config = config

    def deploy(self):
        parameters = self.create_flyway_parameters()

        subprocess.run("flyway {params} {command}".format(
            params=self.translate_parameters(parameters),
            command="migrate"), shell=True)

    @staticmethod
    def translate_parameters(parameters):
        return " ".join(["-{key}={value}".format(key=key, value=value) for key, value in parameters.items()])

    def create_flyway_parameters(self):
        params = self.create_default_parameters()
        params.update({
            "user": self.config["user"],
            "password": "{0}".format(self.config["password"]),
            "url": "jdbc:mariadb://{host}:{port}/{schema}".format(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", "3306"),
                schema=self.config["schema"]
            ),
            "locations": "filesystem:{scriptsDirectory}".format(
                scriptsDirectory=self.config["scripts_directory"]
            )
        })

        self.copy_config_entry(self.config, "versionPrefix", params, "sqlMigrationPrefix" "V")
        self.copy_config_entry(self.config, "versionSeparator", params, "sqlMigrationSeparator" "V")
        return params

    @staticmethod
    def create_default_parameters():
        return {
            "installedBy": "pydeploy",
            "cleanDisabled": "true",
            "sqlMigrationSeparator": "_",
            "sqlMigrationPrefix": "V",
            "baselineVersion": "0001",
            "ignoreMissingMigrations": "true",
            "url": "",
            "user": "",
            "password": ""
        }

    @staticmethod
    # TODO MOve this to a config utils file at some point?
    def copy_config_entry(source, src_key, dest, dest_key=None, default=None):
        if not dest_key:
            dest_key = src_key
        if src_key in source:
            dest[dest_key] = source[src_key]
        elif default:
            dest[dest_key] = default
