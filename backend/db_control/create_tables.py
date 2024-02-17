import platform
print(platform.uname())

from db_control.mymodels import Base #, User, Comment
from db_control.connect import engine

print("Creating tables >>> ")
Base.metadata.create_all(bind=engine)