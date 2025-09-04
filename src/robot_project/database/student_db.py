import mysql.connector
from typing import Union, Literal

class StudentDatabase:

    def __init__(self, db_config):
        
        self.db_config = db_config
        self.db_connection = None  # Aquí se guardará la conexión una vez abierta
        self.connect_to_DB()

    def connect_to_DB(self):
        if self.db_connection is None or not self.db_connection.is_connected():
            try:
                self.db_connection = mysql.connector.connect(**self.db_config)
                print("✅ Conexión a base de datos exitosa.")
            except mysql.connector.Error as e:
                print("❌ Error al conectar a la base de datos:", e)
                self.db_connection = None
        else:
            print("ℹ️ Ya existe una conexión activa.")
        return self.db_connection
    
    def get_connection(self):
        if self.db_connection is None or not self.db_connection.is_connected():
            self.connect_to_DB()
        return self.db_connection

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
    
    def get_student_info(self, student_code: int, field: Literal['student_code', 'student_name', 'student_age', 'student_email', 'student_points']) -> Union[str, int, None]:
        """
        Obtiene información de un estudiante basado en el código y el campo especificado.
        
        :param conn: Conexión a la base de datos.
        :param student_code: Código del estudiante a consultar.
        :param field: El nombre del campo a obtener ('student_name', 'student_age', 'student_email', 'student_points', etc.)
        :return: El valor del campo solicitado o None si no se encuentra.
        """
        conn = self.get_connection()
        # Asegurarnos de que el campo solicitado es válido
        valid_fields = ['student_name', 'student_age', 'student_email', 'student_points']
        if field not in valid_fields:
            raise ValueError(f"El campo '{field}' no es válido. Los campos válidos son: {', '.join(valid_fields)}.")
        
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT {field} FROM students WHERE student_code = %s"
        cursor.execute(query, (student_code,))
        row = cursor.fetchone()
        cursor.close()
        
        return row[field] if row else None
            

    def update_student_info(self, student_code: int, field: Literal['student_code', 'student_name', 'student_age', 'student_email', 'student_points'], field_value: Union[str, int, None] = None) -> bool:

        """
        Actualiza la información de un estudiante en la base de datos.
        :param conn: Conexión a la base de datos.
        :param student_code: Código del estudiante a actualizar.
        :param field: Parámetro que se desea actualizar (nombre, edad, puntos, etc.).
        :param field_value: Valor nuevo para el parámetro. Si es None, se aplica el valor predeterminado.
        :return: Retorna True si la actualización fue exitosa, False si no se encontró al estudiante.
        """
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM students WHERE student_code = %s", (student_code,))
        row = cursor.fetchone()
        success = False

        if row and field in ['student_name', 'student_age', 'student_email', 'student_points']:
            try:
                # Diccionario con el tipo esperado para cada campo
                expected_types = {
                    'student_name': str,
                    'student_age': int,
                    'student_email': str,
                    'student_points': (str, type(None))
                }

                # Validación de tipo
                expected_type = expected_types[field]
                if not isinstance(field_value, expected_type):
                    raise TypeError(f"El valor de '{field}' debe ser de tipo {expected_type.__name__}")

                # Lógica especial para incrementar puntos
                if field == 'student_points' and field_value is None:
                    modified_value = row['student_points'] + 10
                else:
                    modified_value = field_value

                # Ejecutar la actualización
                cursor.execute(f"UPDATE students SET {field} = %s WHERE student_code = %s", (modified_value, student_code))
                conn.commit()
                success = True

            except TypeError as e:
                print(f"Error: {e}")
                raise
            finally:
                cursor.close()
        else:
            print("Error: Campo inválido.")

        return success
