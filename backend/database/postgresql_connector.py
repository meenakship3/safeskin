import psycopg2
import os

# Defining database connection parameters
db_params = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT"),
}
try:
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
except (Exception, psycopg2.Error) as error:
    print(f"Error connecting to the database: {error}")
else:
    print("Connected successfully!")

# finally:
#     if connection:
#         cursor.close()
#         connection.close()
#         print("Database connection closed.")
