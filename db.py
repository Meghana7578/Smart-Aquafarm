import oracledb

oracledb.init_oracle_client(
    lib_dir=r"C:\Users\DELL\OneDrive\Documents\instantclient_23_26\instantclient_23_0"
)

connection = oracledb.connect(
    user="HARSHITA SEETHALAM",
    password="Harshita@333",
    dsn="localhost:1521/XE"
)

cursor=connection.cursor()
print("Connected Successfully")