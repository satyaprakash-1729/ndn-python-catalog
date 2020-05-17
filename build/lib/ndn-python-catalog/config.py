import yaml
from pkg_resources import resource_filename


def get_yaml(path):
    # if fall back to internal config file, so that repo can run without any external configs
    if path is None:
        path = resource_filename(__name__, 'ndn-python-catalog.conf')

    try:
        with open(path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f'could not find config file: {path}') from None
    return config
