from mysql.connector import connect
from mysql.connector import Error
from mysql.connector import pooling
import argparse
import logging
import sys
import os

current_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_path))
if os.path.dirname(current_path) in sys.path:
    sys.path.remove(os.path.dirname(current_path))
sys.path.append(project_root)
from models.models import db, Member, Problem, Catagory

logging.root.name = "Mysql db manager"
logging.basicConfig(level=logging.INFO,
                format='[%(levelname)-7s] %(name)s - %(message)s',
                stream=sys.stdout)
class mysql_mgr:
    def __init__(self, db):
        self._mypool = None
        self._db = db

    def reset(self):
        self.connect()
        self.reset_database()

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
            cursor.execute(f"DROP DATABASE IF EXISTS {self._db}")
            cursor.execute(f"CREATE DATABASE {self._db}")
        self.connect_and_run(run)

    # Test & Debug
    def runSQLCmd(self, cmd):
        def run(cursor):
            cursor.execute(f"USE {self._db}")
            logging.info("Run the command in mysql : " + cmd)
            cursor.execute(cmd)
            logging.info(str(cursor.fetchall()))
        self.connect_and_run(run, True)

    def show(self):
        def run(cursor):
            cursor.execute("USE VLOG")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            logging.info("Tables : ")
            logging.info(tables)
            for table in tables:
                logging.info("Table : " + str(table[0]))
                cmd = "SELECT * FROM " + table[0]
                cursor.execute(cmd)
                info = cursor.fetchall()
                for x in info: logging.info(x)
        self.connect_and_run(run)

    def add_member(self, data):
        user = Member(name=data["name"], email=data["email"], password=data["password"])
        db.session.add(user)
        db.session.commit()

    def get_member(self, data):
        email = data.get('email')
        password = data.get('password')

        query = Member.query.filter_by(email=email)
        if password:
            query = query.filter_by(password=password)

        print(query.first())
        return query.first()

# The argument parser
def Argument():
    parser = argparse.ArgumentParser(description="Mysql db manager")
    list_of_mode = ["reset"]
    parser.add_argument('-d', '--db', type=str, required=True, help="specify the db name")
    parser.add_argument('-m', '--mode', type=str, choices=list_of_mode, default="init", help="specify the mode, current support = {}, default = init".format(list_of_mode))
    parser.add_argument('-s', '--show', default=False, action="store_true", help="show the current database")
    parser.add_argument('-c', '--command', type=str, help="run testing command in mydb")
    return parser.parse_args()

if __name__=="__main__":
    arg = Argument()
    flow = mysql_mgr(arg.db)

    if arg.mode=="reset":
        flow.reset()
    else:
        flow.init()

    if arg.show:
        flow.show()

    if arg.command != None:
        flow.runSQLCmd(arg.command)