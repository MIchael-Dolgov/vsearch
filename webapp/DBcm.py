import mysql.connector


class DataBaseError(Exception):
    pass


class ConnectionError(Exception):
    pass


class CredentialsError(Exception):
    pass


class SQLError(Exception):
    pass


class UseDataBase:
    """Диспетчер контекста"""

    def __init__(self, config: dict) -> None:
        """Принимаег аргумент для инициализации пользователя и сохраняет в виде атрибута"""
        self.configuration = config


    def __enter__(self) -> "Cursor":
        """Производит настройку соединения"""
        try:
            self.conn = mysql.connector.connect(**self.configuration)
            self.cursor = self.conn.cursor()
            return self.cursor
        except mysql.connector.errors.DatabaseError as err:
            raise DataBaseError(err)
        except mysql.connector.errors.InterfaceError as err:
            raise ConnectionError(err)
        except mysql.connector.errors.ProgrammingError as err:
            raise CredentialsError(err)

    
    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        """Закрывает соединение"""
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        if exc_type is mysql.connector.errors.ProgrammingError:
            raise SQLError(exc_value)
        elif exc_type:
            raise exc_type(exc_value)