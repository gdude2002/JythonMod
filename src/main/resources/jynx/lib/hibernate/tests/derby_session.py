from jynx.lib.hibernate import*
from jynx.lib.util.table import Table as SQLTable

from com.ziclix.python.sql import zxJDBC
derbyConn = zxJDBC.connect("jdbc:derby:hiberynxdb",
                           "kay",
                           "",
                           "org.apache.derby.jdbc.EmbeddedDriver")
cursor = derbyConn.cursor()

try:
    cursor.execute("create table Course(COURSE_ID int PRIMARY KEY, COURSE_NAME varchar(80) NOT NULL)")
    cursor.execute("insert into Course values (101,'Learning Jython')")
    cursor.execute("select * from AddressType")
    SQLTable.display(cursor)
    derbyConn.commit()
    cursor.close()
except zxJDBC.Error, e:
    cursor.execute("select * from ExtendedLife")
    SQLTable.display(cursor)
    derbyConn.commit()
    cursor.close()

derbyConn.close()


