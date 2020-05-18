from .sqlite import SqliteStorage


def create_storage(config):
    db_type = config['db_type']
    try:
        if db_type == 'sqlite3':
            db_path = config[db_type]['path']
            ret = SqliteStorage(db_path)
        else:
            raise NameError()

    except NameError:
        raise NotImplementedError(f'Unsupported database backend: {db_type}')
    
    return ret
