from flask import Flask, request
from flask_restful import Resource, Api
from pymongo import MongoClient
import hashlib

import config

app = Flask(__name__)
api = Api(app)

def getMongo():
	return MongoClient('mongodb://%s:%s@127.0.0.1' % (config.mongo['user'], config.mongo['pw']))['ow-buster']
def getSha512(s):
	return hashlib.sha512(str(config.salt + s).encode('utf-8')).hexdigest()
def verifyPhone(s):
	num = s.isnumeric()
	strlen = len(s)
	print(strlen)
	if num and strlen >= 10 and strlen <= 11 and s[0:3] == '010':
		return True
	return False

class Account(Resource):
	def post(self, phone):
		if verifyPhone(phone) is False:
			return { 'result': False, 'msg': '부적절한 전화번호 입니다.'}

		client = getMongo()
		result = client.smsList.find_one({'phoneNo': phone})
		
		pw = getSha512(request.form['password'])
		if result is None or result['password'] != pw:
			return { 'result': False, 'msg': '존재하지 않는 계정이거나 비밀번호가 일치하지 않는 계정입니다.'}
		if result['confirmed'] is False:
			return { 'result': False, 'msg': "인증이 필요한 계정입니다.\n배틀넷 ESukmean#3630으로 귓 주세요."}

		safe = {
			recvEvents: result['recvEvents'],
			enabled: result['enabled']
		}
		return result

	def put(self, phone):
		if verifyPhone(phone) is False:
			return { 'result': False, 'msg': "부적절한 전화번호 입니다."}

		client = getMongo()
		result = client.smsList.find_one({'phoneNo': phone})
		if result is not None:
			return { 'msg': "등록되었습니다.\n배틀넷 ESukmean#3630으로 귓 주세요.'"}

		pw = getSha512(request.form['password'])
		client.smsList.insert_one({
			'phoneNo': phone,
			'password': pw,
			'confirmed': False,
			'battleTag': request.form['battleTag'],
			'recvEvents': False,
   			'enabled': True
		})
		return { 'msg': "등록되었습니다.\n배틀넷 ESukmean#3630으로 귓 주세요.'"}



api.add_resource(Account, '/api/<string:phone>')

if __name__ == '__main__':
	app.run(debug=True, port=8085)