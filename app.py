from flask import Flask
from peewee import SqliteDatabase, PostgresqlDatabase
import psycopg2

app = Flask(__name__)

#define databases
#hw_db = SqliteDatabase('hw_db.db')
#data_db = SqliteDatabase('data_db.db')
hw_db = PostgresqlDatabase(
	database = 'hw_db',
	user = 'postgres',
	password = 'postgres',
	host = '127.0.0.1'
	)
