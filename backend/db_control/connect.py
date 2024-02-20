# uname() error回避
import platform
print(platform.uname())

from sqlalchemy import create_engine
import sqlalchemy

import os
main_path = os.path.dirname(os.path.abspath(__file__))
path = os.chdir(main_path)
print(path)

user = 'user'
password = 'password'
host = 'host'
database_name = 'database_name'
engine = sqlalchemy.create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database_name}')


