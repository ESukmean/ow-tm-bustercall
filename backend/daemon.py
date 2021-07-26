import requests 
import time
from pymongo import MongoClient
import config

last = None

def getMongo():
	return MongoClient('mongodb://%s:%s@127.0.0.1' % (config.mongo['user'], config.mongo['pw']))['ow-buster']

def notify():
	def sendSMS_coolsms(toList, msg):
		import sys
		from sdk.api.message import Message
		from sdk.exceptions import CoolsmsException

		cool = Message(config.coolsms['key'], config.coolsms['secret'])
		params = dict()
		params['type'] = 'sms' # Message type ( sms, lms, mms, ata )
		params['to'] = ','.join(toList) # Recipients Number '01000000000,01000000001'
		params['from'] = '01098000336' # Sender number
		params['text'] = msg # Message

		print('send', params)
		try:
			response = cool.send(params)
			print("Success Count : %s" % response['success_count'])
			print("Error Count : %s" % response['error_count'])

			if "error_list" in response:
				print("Error List : %s" % response['error_list'])

		except CoolsmsException as e:
			print("Error Code : %s" % e.code)
			print("Error Message : %s" % e.msg)

	def sendSMS_ncloud(toList, msg):
		def make_signature(uri):
			import sys
			import os
			import hashlib
			import hmac
			import base64
			import requests
			import time


			timestamp = int(time.time() * 1000)
			timestamp = str(timestamp)

			access_key = config.ncloud['accesskey']			# access key id (from portal or Sub Account)
			secret_key = config.ncloud['secretkey']			# secret key (from portal or Sub Account)
			secret_key = bytes(secret_key, 'UTF-8')

			method = "POST"

			message = method + " " + uri + "\n" + timestamp + "\n" + access_key
			message = bytes(message, 'UTF-8')
			signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
			return {
				'x-ncp-apigw-timestamp': timestamp,
				'x-ncp-iam-access-key': access_key,
				'x-ncp-apigw-signature-v2': signingKey,
				'Content-type': 'application/json'
			}

		import requests
		req_body = {
			"type": "SMS",
			"contentType": "COMM",
			"countryCode": "82",
			"from": "01098000336",
			"content": msg,
			"messages": list(map(lambda num: {'to': num}, toList)),
		}

		import requests, json 
		uri = "/sms/v2/services/{}/messages".format(config.ncloud['serviceid'])
		header = make_signature(uri)
		try:
			if requests.post('https://sens.apigw.ntruss.com' + uri, headers=header, data=json.dumps(req_body)).status_code != 202:
				return sendSMS_coolsms(toList, msg) #정상 처리가 안되면 coolsms 백업 사용	
		except:
			return sendSMS_coolsms(toList, msg) #오류 발생시 coolsms 백업 사용

	def getSendList():
		client = getMongo()
		result = client.smsList.find({'enabled': True})

		return tuple(map(lambda x: x['phoneNo'], result))


	to = getSendList()
	sendSMS_ncloud(to, "[ESukmeans] 오버워치 난장판 모드가 활성화 되었습니다.\n문의: ESukmean#3630")
	
def checkOWAcade():
	try:
		resp = requests.get('https://overwatcharcade.today/api/v1/overwatch/today')
		if resp.ok is False:
			return False

		result = resp.json()
		return result

	except:
		return False

def containTM(apiJson):
	if 'data' not in apiJson:
		return False

	apiJson = apiJson['data']
	if 'modes' not in apiJson:
		return False

	return 'Total Mayhem' in map(lambda x: x['name'], apiJson['modes'])
	# return 'No Limits' in map(lambda x: x['name'], apiJson['modes'].values())

def isUpdatedToday(apiJson):
	if 'is_today' not in apiJson:
		return True

	return apiJson['is_today'] == True

accurate = 0 # -2 절대 아님 / -1 아닐수도 / 0 중립 / 1 그럴수도 / 2 TM날 / 3 TM 전송까지 완료
isTM = None


while True:
	time.sleep(10)

	resp = checkOWAcade()
	if resp is False:
		time.sleep(30)
		continue
	
	print('TM', containTM(resp), accurate)
	if isUpdatedToday(resp) is False:
		time.sleep(7)

	elif containTM(resp):
		accurate = max(accurate, 0) # 혹시 "아님 상태" 라면 중립으로 빼 줘야함
		accurate = min(accurate + 1, 4) # 최대 기어는 3

		if isTM is None:
			isTM = True
		elif accurate == 2 and isTM is False:
			isTM = True

			notify()
		
		if accurate < 2:
			time.sleep(10) # 아직 레벨3단계 까지는 가지 않은 상태. (검증 필요상태)

		else:
			time.sleep(900 * accurate) # 2단계시 30분, 3단계시 45분

	else:
		accurate = max(accurate - 1, -2)

		if accurate == -2:
			isTM = False
	
		time.sleep(60)
