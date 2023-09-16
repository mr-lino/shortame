from os import environ

from dynaconf import Dynaconf

settings = Dynaconf(
    root_path="../",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
    load_dotenv=True,
)


def get_redis_host_and_port():
    return {"host": settings.redis_host, "port": settings.redis_port}
