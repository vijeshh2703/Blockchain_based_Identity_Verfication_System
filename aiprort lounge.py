import mysql.connector
from mysql.connector import Error
import hashlib

class AirportVerificationSystem:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = self._connect_to_database()

    def _connect_to_database(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if connection.is_connected():
                print("Connected to MySQL database")
                return connection
        except Error as e:
            print("Error connecting to MySQL database:", e)
            return None

    def _create_table(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    name VARCHAR(255),
                    dob VARCHAR(20),
                    passport_id VARCHAR(255) unique PRIMARY KEY
                )
            ''')
            self.connection.commit()
            cursor.close()
        except Error as e:
            print("Error creating table:", e)

    def add_user(self, name, dob, passport_id):
        try:
            cursor = self.connection.cursor()
            query = '''
                INSERT INTO users (name, dob, passport_id)
                VALUES (%s, %s, %s)
            '''
            data = (name, dob, passport_id)
            cursor.execute(query, data)
            self.connection.commit()
            cursor.close()
        except Error as e:
            print("Error adding user:", e)

    def _build_merkle_tree(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM users')
            data = cursor.fetchall()
            print("Fetched data from database:", data)
            hashed_data = [self._hash_user(user) for user in data]
            print("Hashed data:", hashed_data)
            # Build Merkle tree from hashed data
            merkle_root = self._build_tree(hashed_data)
            print("Merkle root:", merkle_root)
            return merkle_root
        except Error as e:
            print("Error building Merkle tree:", e)

    def _hash_user(self, user):
        name_hash = hashlib.sha256(user[0].encode()).hexdigest()
        dob_hash = hashlib.sha256(str(user[1]).encode()).hexdigest()
        passport_id_hash = hashlib.sha256(user[2].encode()).hexdigest()
        return hashlib.sha256((name_hash + dob_hash + passport_id_hash).encode()).hexdigest()

    def _build_tree(self, data):
        if len(data) == 1:
            return data[0]
        
        next_level = []
        for i in range(0, len(data)-1, 2):
            combined_data = data[i] + data[i+1]
            next_level.append(hashlib.sha256(combined_data.encode()).hexdigest())
        
        if len(data) % 2 != 0:
            next_level.append(data[-1])
        
        return self._build_tree(next_level)

    def verify_user(self, name, dob, passport_id):
        try:
            merkle_root = self._build_merkle_tree()
            user_hash = self._hash_user((name, dob, passport_id))
            print("user hash: ",user_hash)
            if merkle_root == user_hash:
                print("User verified.")
            else:
                print("User verification failed.")
        except Error as e:
            print("Error verifying user:", e)

    def decode_hash(self, hashed_data):
        return hashed_data.decode()

if __name__ == "__main__":
    # MySQL database configuration
    host = 'localhost'
    database = 'airport_verification'
    user = 'root'
    password = ''
    try:
        # Connect to MySQL database
        system = AirportVerificationSystem(host, database, user, password)
        # Create table if not exists
        system._create_table()
        # Add users to the system
        system.add_user("John", "1990101", "12345")
        # Verify a user's identity
        system.verify_user("John", "1990101", "12345")
    except Error as e:
        print("Error:", e)
    finally:
        # Close the MySQL connection
        if system:
            system.connection.close()