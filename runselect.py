import jinja2
import json
import sqlite3
import argparse

def generate_sql_query(json_config):
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
    sql_query = template.render(json_config)
    return sql_query

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('json_file', type=str)
    args = parser.parse_args()

    with open(args.json_file, 'r') as json_file:
        json_config = json.load(json_file)    

    sql_query = generate_sql_query(json_config)
    print("Generated SQL Query:", sql_query)

    conn = sqlite3.connect('mydatabase.sqlite')
    cursor = conn.cursor()

    cursor.execute(sql_query)
    results = cursor.fetchall()
    print("Query Results:\n", results)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()