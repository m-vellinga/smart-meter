from pydantic import BaseSettings, AnyHttpUrl, SecretStr


class GeneralConfig(BaseSettings):
    SENTRY_DSN: str = None
    SERIAL_DEVICE: str = "/dev/ttyUSB0"

    class Config:
        env_file = ".env"


class InfluxConfig(BaseSettings):
    URL: AnyHttpUrl = None
    TOKEN: SecretStr = None
    ORG: str = None
    BUCKET: str = None

    @property
    def enabled(self):
        return all(
            [
                self.URL,
                self.TOKEN,
                self.ORG,
                self.BUCKET,
            ]
        )

    class Config:
        env_prefix = "INFLUX_"
        env_file = ".env"


general_config = GeneralConfig()
influx_config = InfluxConfig()
