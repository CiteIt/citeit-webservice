# Move a copy of this database settings file to the parent directory so that it is outside the main directory

DATABASE_TYPE = 'mysql'     
DATABASE_CONNECTION_TYPE = 'mysql+pymsql'    # mysql+pymysql | mysql+mysqlconnector (mysql8) | postgresql | sqlite | mssql+pyodbc | firebird+fdb | oracle
DATABASE_SERVER = 'localhost'
DATABASE_NAME = 'citeit_db'
DATABASE_USER = 'citeit_webuser'
DATABASE_PASSWORD = '************'
DATABASE_PORT = 3306

HASH_SALT = 'QckVAaHMFT@MZ3_vyQ4HAv'       # This salt is used in SHA-256 hashes