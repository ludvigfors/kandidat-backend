import os
from IMM_database.database import session_scope, Image
import datetime

now = datetime.datetime.now()
image_datetime = "2020-04-05_21-45-09"

with session_scope() as session:
    count = len(session.query(Image).filter_by(file_name=image_datetime).all())


i = 0

