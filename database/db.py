import pyodbc

def connect_to_mssql(server, database, username, password):
    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password}'
        )
        print("✅ Connexion réussie à la base de données.")
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return None

def get_shapes_from_ddb(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DesignDatabase.dbo.Shapes") # Modifier avec les données de la bdd
        rows = cursor.fetchall()
        
        shapes = []
        for row in rows:
            shapes.append(row)
        print("✅ Données extraites avec succès.")
        return shapes
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction des données : {e}")
        return None

# Configuration
server = '192.168.1.100'
database = 'AvevaE3D'
username = 'admin'
password = 'admin'

conn = connect_to_mssql(server, database, username, password)
if conn:
    shapes = get_shapes_from_ddb(conn)
    print(shapes)
    conn.close()
