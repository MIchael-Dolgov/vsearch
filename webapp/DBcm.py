import mysql.connector


class UseDataBase:
    """Диспетчер контекста"""

    def __init__(self, config: dict) -> None:
        """Принимаег аргумент для инициализации пользователя и сохраняет в виде атрибута"""
        self.configuration = config


    def __enter__(self) -> "Cursor":
        """Производит настройку соединения"""
        self.conn = mysql.connector.connect(**self.configuration)
        self.cursor = self.conn.cursor()
        return self.cursor

    
    def __exit__(self, exc_type, exc_value, exc_trace) -> None:
        """Закрывает соединение"""
        self.conn.commit()
        self.cursor.close()
        self.conn.close()