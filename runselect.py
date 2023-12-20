import jinja2
import json
import sqlite3
import argparse

class DatabaseQuery:
    def __init__(self, json_config):
        self.json_config = json_config

    def generate_sql_query(self):
        template_str = """
        SELECT {{ fields }}
        FROM {{ table }}
        {% if conditions %}
        WHERE
            {% for key, condition in conditions.items() %}
                {% if condition is string %}
                    {{ key }} = '{{ condition }}'
                {% else %}
                    {{ key }} {{ condition.operator }} {{ condition.value }}
                {% endif %}
                {% if not loop.last %} AND {% endif %}
            {% endfor %}
        {% endif %}
        """
        template = jinja2.Template(template_str)
        sql_query = template.render(self.json_config)
        return sql_query

    def execute_query(self):
        sql_query = self.generate_sql_query()
        print("Generated SQL Query:", sql_query)

        conn = sqlite3.connect('mydatabase.sqlite')
        cursor = conn.cursor()
        cursor.execute(sql_query, self.json_config.get('conditions', {}))
        results = cursor.fetchall()
        print("Query Results:", results)

        conn.commit()
        conn.close()

def main():
    parser = argparse.ArgumentParser(description='Database Query CLI')
    parser.add_argument('json_file', type=str, help='Path to the JSON configuration file')
    args = parser.parse_args()

    with open(args.json_file, 'r') as json_file:
        json_config = json.load(json_file)

    db_query = DatabaseQuery(json_config)
    db_query.execute_query()

if __name__ == "__main__":
    main()
