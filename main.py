from dotenv import load_dotenv
load_dotenv()
import jinja2
import json
import sqlite3
import pymysql
import os
import ssl

ca_path = "/etc/ssl/cert.pem"

ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=ca_path)


class DatabaseQuery:
    def __init__(self, json_config):
        self.json_config = json_config
    def generate_sql_query(self):
        template_str = """
        SELECT {{ fields | join(', ') }}
        FROM {{ table }}
        {% if conditions %}
        WHERE
            {% for key, value in conditions.items() %}
                {{ key }} = '{{ value }}'
                {% if not loop.last %} AND {% endif %}
            {% endfor %}
        {% endif %}
        """
        template = jinja2.Template(template_str)
        sql_query = template.render(self.json_config)
        return sql_query

    def execute_query(self):
        source_conn = sqlite3.connect('mydatabase.sqlite')
        destination_conn = pymysql.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USERNAME"),
            passwd=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME"),
            autocommit=True,
            ssl=ssl_context
        )
        
        cursor_source = source_conn.cursor()
        cursor_destination = destination_conn.cursor()

        # Create view in MySQL
        self.create_view_in_sqlite(cursor_source)

        cursor_destination.execute(f"SELECT * INTO {self.json_config.get('table_name')} FROM {self.json_config.get('view_name')};")

        source_conn.close()
        destination_conn.commit()
        destination_conn.close()

    def create_view_in_sqlite(self, cursor):
        view_name = self.json_config.get("view_name")
        
        if view_name:
            sql_query = self.generate_create_view_query(view_name)
            cursor.execute(sql_query)


    
    def generate_create_view_query(self, view_name):
        template_str = """
        CREATE VIEW {{ view_name }} AS {{ select_query }}
        """
        select_query = self.generate_sql_query()
        template = jinja2.Template(template_str)
        sql_query = template.render({"view_name": view_name, "select_query": select_query})
        print(sql_query)
        return sql_query


if __name__ == "__main__":
    with open(r'/Users/ravitejagorti/Desktop/DataAccessLayer-DAL/sample.json', 'r') as json_file:
        json_config = json.load(json_file)

    db_query = DatabaseQuery(json_config)
    db_query.execute_query()



# from dotenv import load_dotenv
# load_dotenv()
# import os
# import pymysql
# import ssl

# # Assuming you have the necessary environment variables set
# # DB_HOST, DB_USERNAME, DB_PASSWORD, and DB_NAME

# # Specify the path to your CA file
# ca_path = "/etc/ssl/cert.pem"

# # Create a custom SSL context
# ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=ca_path)

# # Establish a connection to the MySQL database using pymysql
# connection = pymysql.connect(
#     host=os.getenv("DB_HOST"),
#     user=os.getenv("DB_USERNAME"),
#     passwd=os.getenv("DB_PASSWORD"),
#     db=os.getenv("DB_NAME"),
#     autocommit=True,
#     ssl=ssl_context
# )

# try:
#     # Create a cursor to interact with the database
#     cursor = connection.cursor()

#     # Execute "SHOW TABLES" query
#     cursor.execute("SHOW TABLES")

#     # Fetch all the rows
#     tables = cursor.fetchall()

#     # Print out the tables
#     print("Tables in the database:")
#     for table in tables:
#         print(table[0])

# except pymysql.Error as e:
#     print("PyMySQL Error:", e)

# finally:
#     # Close the cursor and connection
#     cursor.close()
#     connection.close()
