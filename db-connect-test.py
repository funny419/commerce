import pymysql

# MaridDB Connection
connection = pymysql.connect(
    host='funnyserver',
    user='funny',
    password='strim100',
    db='commerce'
)

try:
    with connection.cursor() as cursor:
        sql = "SHOW TABLES"
        cursor.execute(sql)
        result = cursor.fetchall()
        for table in result:
            print(table)
finally:
    connection.close()