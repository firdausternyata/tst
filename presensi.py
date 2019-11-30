import os
from pprint import pprint

from flask import Flask
from flask import render_template
from flask import request
from flask import json
import simplejson
from werkzeug.security import generate_password_hash, check_password_hash
from flaskext.mysql import MySQL

project_root = os.path.dirname(__name__)
template_path = os.path.join(project_root)

mysql = MySQL()
app = Flask(__name__,template_folder=template_path)
# mysql configuratoin
app.config['MYSQL_DATABASE_HOST']       = 'localhost'
app.config['MYSQL_DATABASE_USER']       = 'root'
app.config['MYSQL_DATABASE_PASSWORD']   = ''
app.config['MYSQL_DATABASE_DB']         = 'presensi'
mysql.init_app(app)

@app.route('/')
def main_world():
     return "Welcome to the Presensi Home."


@app.route('/show')
def show():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM presensi")
    data = cursor.fetchall()
    dataList = []
    if data is not None:
        for item in data:
            dataTempObj = {
                'id'       : item[0],
                'nik'      : item[1],
                'nama'     : item[2],
                'waktu_scan'	   : item[3]
            }
            dataList.append(dataTempObj)
        return json.dumps(dataList)
    else:
        return 'data kosong'


@app.route('/filter/<string:tahun>/<int:bulan>', methods=['GET'])
def filter(tahun,bulan):
	conn = mysql.connect()
	cursor = conn.cursor()
	a = '-'
	b = '-01'
	tanggal = tahun+a+str(bulan)+b
	cursor.execute("SELECT * FROM presensi WHERE waktu_scan<%s",(tanggal))
	data = cursor.fetchall()
	dataList = []
	if data is not None:
		for item in data:
			dataTempObj = {
				'id'       : item[0],
				'nik'      : item[1],
				'nama'     : item[2],
				'waktu_scan'	   : item[3]
			}
			dataList.append(dataTempObj)
		return json.dumps(dataList)
	else:
		return 'data kosong'

if __name__ == '__main__':
    app.run()
