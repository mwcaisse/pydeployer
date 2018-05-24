import subprocess


class FlywayDatabaseDeployer:

    def __init__(self, config):
        self.config = config

    def deploy(self):
        parameters = self.create_flyway_parameters()

        subprocess.run("flyway", self.translate_parameters(parameters))

    @staticmethod
    def translate_parameters(parameters):
        return " ".join(["-{key}={value}".format(key=key, value=value) for key, value in parameters.items()])

    def create_flyway_parameters(self):
        params = self.create_default_parameters()
        params.update({
            "user": self.config["user"],
            "password": self.config["password"],
            "url": "jdbc:mariadb://{host}:{port}/{schema}".format(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", "3306"),
                schema=self.config["schema"]
            ),
            "locations": "filesystem:{scriptsDirectory}".format(
                scriptsDirectory=self.config["scripts_directory"]
            )
        })

        self.copy_config_entry(params, self.config, "versionPrefix", "V")
        self.copy_config_entry(params, self.config, "versionSeparator", "_")
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
    def copy_config_entry(dest, source, key, default=None):
        if key in source:
            dest[key] = source[key]
        elif default:
            dest[key] = default