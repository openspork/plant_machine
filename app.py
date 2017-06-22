from flask import Flask
from peewee import SqliteDatabase

app = Flask(__name__)

#define databases
hw_db = SqliteDatabase('hw_db.db')
data_db = SqliteDatabase('data_db.db')
