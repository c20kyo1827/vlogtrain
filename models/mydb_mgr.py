from mysql.connector import connect
from mysql.connector import Error
from mysql.connector import pooling
import argparse
import logging
import sys
import os

# TODO
# 1. Use flask_sqlalchemy to modify
# 2. Create index
# 3. Use the inner join
# 4. Handle error when inserting/deleting error => connect_and_run()
#       Should throw exception?
#       Reuturn error message?

logging.root.name = "Mysql db manager"
logging.basicConfig(level=logging.INFO,
                format='[%(levelname)-7s] %(name)s - %(message)s',
                stream=sys.stdout)
class mydb_mgr:
    def __init__(self):
        self._mypool = None

    def reset(self):
        self.connect()
        self.reset_database()
        self.reset_table()

    def init(self):
        self.connect()

    def connect(self):
        self._mypool = pooling.MySQLConnectionPool(
            pool_name="my_py_pool",
            pool_size=3,
            pool_reset_session=True,
            host=os.getenv("MYSQL_HOST","localhost"),
            user=os.getenv("MYSQL_USER","root"),
            password=os.getenv("MYSQL_ROOT_PASSWD","root")
        )
        logging.info("Connection Pool Name - {}".format(self._mypool.pool_name))
        logging.info("Connection Pool Size - {}".format(self._mypool.pool_size))

    def connect_and_run(self, func, is_commit=False):
        if self._mypool==None:
            return
        result = None
        try:
            mydb = self._mypool.get_connection()
            if mydb.is_connected():
                mycursor = mydb.cursor()
                result = func(mycursor)

                if is_commit:
                    mydb.commit()

        except Error as e:
            mydb.rollback()
            logging.error("Error while connecting to MySQL using Connection pool : {}".format(e))
            logging.info("Rollback...")
        finally:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
            return result

    def reset_database(self):
        def run(cursor):
            cursor.execute("DROP DATABASE IF EXISTS website")
            cursor.execute("CREATE DATABASE website")
        self.connect_and_run(run)

    def reset_table(self):
        def run(cursor):
            cursor.execute("USE website")
            cursor.execute("DROP TABLE IF EXISTS attraction")
            cursor.execute("DROP TABLE IF EXISTS mrt")
            cursor.execute("DROP TABLE IF EXISTS category")
            cursor.execute("DROP TABLE IF EXISTS image")
            cursor.execute("DROP TABLE IF EXISTS member")
            cursor.execute("DROP TABLE IF EXISTS book")
            cursor.execute("DROP TABLE IF EXISTS order_data")
            # Attractions
            cursor.execute( \
                "CREATE TABLE attraction( \
                    id bigint NOT NULL, \
                    name varchar(255) NOT NULL, \
                    description TEXT NOT NULL, \
                    address TEXT NOT NULL, \
                    transport TEXT NOT NULL, \
                    lng FLOAT NOT NULL, \
                    lat FLOAT NOT NULL, \
                    PRIMARY KEY(id) \
                )" \
            )
            cursor.execute( \
                "CREATE TABLE mrt( \
                    id bigint AUTO_INCREMENT, \
                    name varchar(255) NOT NULL, \
                    attraction_id bigint NOT NULL, \
                    FOREIGN KEY(attraction_id) REFERENCES attraction(id), \
                    PRIMARY KEY(id) \
                )" \
            )
            cursor.execute( \
                "CREATE TABLE category( \
                    id bigint AUTO_INCREMENT, \
                    name varchar(255) NOT NULL, \
                    attraction_id bigint NOT NULL, \
                    FOREIGN KEY(attraction_id) REFERENCES attraction(id), \
                    PRIMARY KEY(id) \
                )" \
            )
            cursor.execute( \
                "CREATE TABLE image( \
                    id bigint AUTO_INCREMENT, \
                    url TEXT NOT NULL, \
                    attraction_id bigint NOT NULL, \
                    FOREIGN KEY(attraction_id) REFERENCES attraction(id), \
                    PRIMARY KEY(id) \
                )" \
            )
            # Member
            cursor.execute( \
                "CREATE TABLE member( \
                    id bigint AUTO_INCREMENT, \
                    name varchar(255) NOT NULL, \
                    email varchar(255) NOT NULL, \
                    password varchar(255) NOT NULL, \
                    PRIMARY KEY(id) \
                )" \
            )
            # Book
            # TODO
            #   1.Support multiple booking
            #   2.Refactor table design
            #   3.ORM
            cursor.execute( \
                "CREATE TABLE book( \
                    id bigint AUTO_INCREMENT, \
                    member_id bigint NOT NULL, \
                    attraction_id bigint NOT NULL, \
                    book_date date NOT NULL, \
                    book_time SET('morning', 'afternoon') NOT NULL, \
                    price bigint NOT NULL, \
                    FOREIGN KEY(member_id) REFERENCES member(id), \
                    FOREIGN KEY(attraction_id) REFERENCES attraction(id), \
                    PRIMARY KEY(id) \
                )" \
            )
            # Order
            cursor.execute( \
                "CREATE TABLE order_data( \
                    id bigint AUTO_INCREMENT, \
                    order_number varchar(255) NOT NULL, \
                    member_id bigint NOT NULL, \
                    attraction_id bigint NOT NULL, \
                    status bigint NOT NULL, \
                    contact_name varchar(255) NOT NULL, \
                    contact_email varchar(255) NOT NULL, \
                    contact_phone varchar(255) NOT NULL, \
                    book_date date NOT NULL, \
                    book_time SET('morning', 'afternoon') NOT NULL, \
                    price bigint NOT NULL, \
                    FOREIGN KEY(member_id) REFERENCES member(id), \
                    FOREIGN KEY(attraction_id) REFERENCES attraction(id), \
                    PRIMARY KEY(id) \
                )" \
            )
        self.connect_and_run(run)

    # Test & Debug
    def runSQLCmd(self, cmd):
        def run(cursor):
            cursor.execute("USE website")
            logging.info("Run the command in mysql : " + cmd)
            cursor.execute(cmd)
            logging.info(str(cursor.fetchall()))
        self.connect_and_run(run, True)
    
    def show(self):
        def run(cursor):
            cursor.execute("USE website")
            table = ["attraction", "mrt", "category", "image", "member"]
            for t in table:
                cmd = "SELECT * FROM " + t
                cursor.execute(cmd)
                member_info = cursor.fetchall()
                for x in member_info: logging.info(x)
        self.connect_and_run(run)

    # Main api
    # Set function
    def add_attraction_mrt(self, attractions):
        for info in attractions:
            def add_attraction(cursor):
                sql = "INSERT INTO attraction  \
                        (id, name, description, address, transport, lng, lat) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                val = ( 
                        info["id"], info["name"], \
                        info["description"], info["address"], \
                        info["transport"], \
                        info["lng"], info["lat"]
                    )
                cursor.execute("USE website")
                cursor.execute(sql, val)
            self.connect_and_run(add_attraction, True)

            def add_mrt(cursor):
                sql = "INSERT INTO mrt  \
                        (name, attraction_id) VALUES (%s, %s)"
                val = ( info["mrt"], info["id"] )
                cursor.execute("USE website")
                cursor.execute(sql, val)
            if info["mrt"] != None:
                self.connect_and_run(add_mrt, True)

            def add_category(cursor):
                sql = "INSERT INTO category  \
                        (name, attraction_id) VALUES (%s, %s)"
                val = ( info["category"], info["id"] )
                cursor.execute("USE website")
                cursor.execute(sql, val)
            self.connect_and_run(add_category, True)

            for img in info["images"]:
                def add_image(cursor):
                    sql = "INSERT INTO image  \
                            (url, attraction_id) VALUES (%s, %s)"
                    val = ( img, info["id"] )
                    cursor.execute("USE website")
                    cursor.execute(sql, val)
                
                self.connect_and_run(add_image, True)

    def add_member(self, name, email, password):
        def run(cursor):
            sql = "INSERT INTO member (name, email, password) VALUES (%s, %s, %s)"
            val = (name, email, password)
            cursor.execute("USE website")
            cursor.execute(sql, val)
        self.connect_and_run(run, True)

    def delete_book_all(self, member_id):
        def run(cursor):
            # TODO
            # Support multiple booking
            sql = "DELETE FROM book WHERE member_id = %s"
            val = (member_id, )
            cursor.execute("USE website")
            cursor.execute(sql, val)
        self.connect_and_run(run, True)

    def delete_book_by_id(self, book_id, member_id):
        def run(cursor):
            # TODO
            # Support multiple booking
            sql = "DELETE FROM book WHERE id = %s AND member_id = %s"
            val = (book_id, member_id)
            cursor.execute("USE website")
            cursor.execute(sql, val)
        self.connect_and_run(run, True)

    def add_book(self, member_id, attraction_id, date, time, price):
        def run(cursor):
            # TODO
            # Support multiple booking
            sql = "INSERT INTO book (member_id, attraction_id, book_date, book_time, price) VALUES (%s, %s, %s, %s, %s)"
            val = (member_id, attraction_id, date, time, price)
            cursor.execute("USE website")
            cursor.execute(sql, val)
        # TODO
        # Check the column exists or not => exist not to delete
        self.delete_book_all(member_id) # Should be remove after supporting multiple booking
        self.connect_and_run(run, True)

    def add_order(self, order_number, member_id, attraction_id, name, email, phone, date, time, price, status):
        def run(cursor):
            sql = "INSERT INTO order_data (order_number, member_id, attraction_id, contact_name, contact_email, contact_phone, book_date, book_time, price, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (order_number, member_id, attraction_id, name, email, phone, date, time, price, status)
            cursor.execute("USE website")
            cursor.execute(sql, val)
        self.connect_and_run(run, True)

    # Get function
    def get_attractions_by_page_keyword(self, page, keyword):
        def run(cursor):
            cursor.execute("USE website")
            limit = 12
            offset = limit*int(page)
            if keyword==None:
                sql = "SELECT * FROM attraction LIMIT %s,%s"
                val = (offset, limit)
                
            else:
                sql = "SELECT * FROM attraction LEFT JOIN mrt ON mrt.attraction_id=attraction.id WHERE attraction.name LIKE CONCAT('%', %s, '%') OR mrt.name=%s LIMIT %s,%s"
                val = (keyword, keyword, offset, limit)
            cursor.execute(sql, val)
            return cursor.fetchall()
        return self.connect_and_run(run)

    def get_attraction(self, id):
        def run(cursor):
            cursor.execute("USE website")
            sql = "SELECT * FROM attraction WHERE id=%s"
            val = (id, )
            cursor.execute(sql, val)
            return cursor.fetchall()
        return self.connect_and_run(run)

    def get_mrts(self):
        def run(cursor):
            cursor.execute("USE website")
            cursor.execute("SELECT mrt.name, \
                                COUNT(*) 'count' \
                            FROM mrt \
                            GROUP BY mrt.name \
                            ORDER BY count DESC, mrt.name")
            return cursor.fetchall()
        return self.connect_and_run(run)

    def get_mrt_by_id(self, id):
        def run(cursor):
            cursor.execute("USE website")
            sql = "SELECT * FROM mrt WHERE attraction_id=%s"
            val = (id, )
            cursor.execute(sql, val)
            return cursor.fetchall()
        return self.connect_and_run(run)

    def get_category_by_id(self, id):
        def run(cursor):
            cursor.execute("USE website")
            sql = "SELECT * FROM category WHERE attraction_id=%s"
            val = (id, )
            cursor.execute(sql, val)
            return cursor.fetchall()
        return self.connect_and_run(run)
    
    def get_images_by_id(self, id):
        def run(cursor):
            cursor.execute("USE website")
            sql = "SELECT * FROM image WHERE attraction_id=%s"
            val = (id, )
            cursor.execute(sql, val)
            return cursor.fetchall()
        return self.connect_and_run(run)
    
    def get_member(self, email, password=None):
        def run(cursor):
            if password==None:
                sql = "SELECT id, email, name FROM member WHERE email = %s"
                val = (email, )
            else:
                sql = "SELECT id, email, name FROM member WHERE email = %s AND password = %s"
                val = (email, password)
            cursor.execute("USE website")
            cursor.execute(sql, val)
            return cursor.fetchall()
        return self.connect_and_run(run)
    
    def get_booking(self, member_id):
        # TODO
        # Support multiple booking
        def run(cursor):
            sql = "SELECT tableB.*, tableA.name, tableA.address, tableI.url FROM book tableB\
                    LEFT JOIN image tableI \
                        ON tableI.attraction_id=tableB.attraction_id \
                    LEFT JOIN attraction tableA \
                        ON tableA.id=tableB.attraction_id \
                    WHERE tableB.member_id=%s LIMIT 1"
            val = (member_id, )
            cursor.execute("USE website")
            cursor.execute(sql, val)
            return cursor.fetchall()
        return self.connect_and_run(run)
    
    def get_order(self, member_id, order_number):
        # TODO
        # Support multiple booking
        def run(cursor):
            sql = "SELECT * FROM order_data WHERE member_id = %s AND order_number = %s"
            val = (member_id, order_number)
            cursor.execute("USE website")
            cursor.execute(sql, val)
            return cursor.fetchall()
        return self.connect_and_run(run)

# The argument parser
def Argument():
    parser = argparse.ArgumentParser(description="Mysql db manager")
    list_of_mode = ["reset"]
    parser.add_argument('-m', '--mode', type=str, choices=list_of_mode, default="init", help="specify the mode, current support = {}, default = init".format(list_of_mode))
    parser.add_argument('-s', '--show', default=False, action="store_true", help="show the current database")
    parser.add_argument('-c', '--command', type=str, help="run testing command in mydb")
    return parser.parse_args()

if __name__=="__main__":
    flow = mydb_mgr()
    arg = Argument()

    if arg.mode=="reset":
        flow.reset()
    else:
        flow.init()

    if arg.show:
        flow.show()

    if arg.command != None:
        flow.runSQLCmd(arg.command)