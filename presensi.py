import os
from pprint import pprint

from flask import Flask
from flask import render_template
from flask import request
from flask import json, jsonify, request, make_response
import simplejson
from werkzeug.security import generate_password_hash, check_password_hash
from flaskext.mysql import MySQL
import jwt
import datetime
from functools import wraps

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

app.config['SECRET_KEY'] = 'thisisthesecretkey'

def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = request.args.get('token')   #htttp://127.0.0.1:5000/route?token=xxxxxxxxxxxxxxx
		
		if not token:
			return jsonify({'message' : 'Token is missing'}), 403
		
		try:
			data = jwt.decode(token, app.config['SECRET_KEY'])
		except:
			return jsonify({'message' : 'Token is invalid'}), 403
		
		return f(*args, **kwargs)
	
	return decorated

@app.route('/')
def main_world():
     return "Welcome to the Presensi Home."

@app.route('/login')
def login():
	auth = request.authorization
	
	if auth and auth.password == 'admin':
		token = jwt.encode({'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
		
		return jsonify({'token' : token.decode('UTF-8')})
		
	return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

@app.route('/show')
@token_required
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


@app.route('/filter/tahun=<string:tahun>bulan=<int:bulan>', methods=['GET'])
@token_required
def filter(tahun,bulan):
	conn = mysql.connect()
	cursor = conn.cursor()
	a = '-'
	b = '-01'
	c = bulan+1
	tanggal = tahun+a+str(bulan)+b
	tanggal2 = tahun+a+str(c)+b
	cursor.execute("SELECT * FROM presensi WHERE waktu_scan BETWEEN %s AND %s",(tanggal,tanggal2))
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

