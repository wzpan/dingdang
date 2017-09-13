# -*- coding:utf-8 -*-
import requests
import json
import logging
import sys
reload(sys)
sys.setdefaultencoding('utf8')

WORDS = ["JIATINGZHUSHOU","ZHUSHOU"]
SLUG = "homeassistant"

def handle(text,mic,profile,wxbot=None):
	"""
    Responds to user-input, typically speech text
    Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
        wxbot -- wechat bot instance
    """
	mic.say(u"开始家庭助手控制")
	mic.say(u'请在滴一声后说明内容')
	input = mic.activeListen(MUSIC=True)
	while not input:
		mic.say(u"请重新说")
		input = mic.activeListen(MUSIC=True)
	hass(input,mic,profile)
		
def hass(text,mic,profile):
	logger = logging.getLogger(__name__)
	if ( SLUG not in profile ) or ( not profile[SLUG].has_key('url') ) or ( not profile[SLUG].has_key('port') ) or ( not profile[SLUG].has_key('password') ):
		mic.say(u"主人，配置有误")
		return
	url = profile[SLUG]['url']
	port = profile[SLUG]['port']
	password = profile[SLUG]['password']
	headers = {'x-ha-access': password,'content-type': 'application/json'}
	r = requests.get(url+":"+port+"/api/states",headers=headers)
	r_jsons = r.json()
	#print(r_jsons)
	devices = []
	for r_json in r_jsons:
		entity_id = r_json['entity_id']
		domain = entity_id.split(".")[0]
		#print(domain)
		if domain not in ["group","automation","script"]:
			entity = requests.get(url+":"+port+"/api/states/"+entity_id,headers=headers).json()
			devices.append(entity)
	for device in devices:
		name = device["attributes"]["friendly_name"]
		state = device["state"]
		#print(name)
		if name in text:
			#print(name)
			if device["entity_id"].split(".")[0] == "sensor" or not isAction(text):
				try:
					measurement = device["attributes"]["unit_of_measurement"]
				except Exception , e:
					pass
				#print(measurement)
				if 'measurement' in locals().keys():
					mic.say(text + "状态是" + state + measurement)
				else:
					mic.say(text + "状态是" + state)
			elif device["entity_id"].split(".")[0] == "switch" and isAction(text):
				#print(name)
				try:
					if any(word in text for word in [u"开始",u"打开",u"开启"]):
						newState = "turn_on"
						#print(name)
					elif any(word in text for word in [u"停止",u"结束",u"退出"]):
						newState = "turn_off"
					payload = json.dumps({"entity_id":device["entity_id"]})
					request = requests.post(url+":"+port+"/api/services/switch/"+newState,headers=headers,data=payload)
					if format(request.status_code) == "200" or format(request.status_code) == "201":
						mic.say(u"执行成功")
					else:
						mic.say(u"对不起,执行失败")
						print(format(request.status_code))
				except Exception , e:
					pass
			break
	else:
		mic.say(u"对不起,指令不存在")

def isAction(text):
	return any(word in text for word in ["打开","停止","结束","开始"])

def isValid(text):
	return any(word in text for word in [u"开启家庭助手",u"开启助手",u"打开家庭助手",u"打开助手",u"家庭助手"])
