import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
import numpy as np


DATABASEURI = "postgresql://ssr2182:1364@34.74.246.148/proj1part2"

engine = create_engine(DATABASEURI)
conn= engine.connect()

cursor= conn.execute("SELECT * FROM entertainment")
print(cursor.fetchall())
rows=len(cursor.fetchall())
cursor.close()
conn.close()
engine.dispose()