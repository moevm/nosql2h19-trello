import os


pid = os.fork()

if pid > 0:
    os.system('sudo mongod')

else:
    os.system('python3 manage.py runserver')