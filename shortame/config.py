from dynaconf import Dynaconf

settings = Dynaconf(
    root_path="../",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
    load_dotenv=True
)
