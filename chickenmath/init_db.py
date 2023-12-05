import sqlite3

def initialize_database():
    try:
        conn = sqlite3.connect('chickenmath.db')
        cursor = conn.cursor()

        # Create table
        cursor.execute('''CREATE TABLE IF NOT EXISTS farm_data (
                          id INTEGER PRIMARY KEY,
                          eggs_per_week INT,
                          fertilization_rate REAL,
                          hatch_rate REAL)''')
        print("Table created successfully........")

        # Insert data if not exists
        cursor.execute('''INSERT INTO farm_data (id, eggs_per_week, fertilization_rate, hatch_rate)
                          SELECT 1, 5, 0.80, 0.85
                          WHERE NOT EXISTS (SELECT 1 FROM farm_data WHERE id = 1)''')
        print("Data inserted successfully........")

        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    initialize_database()
