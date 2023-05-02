# -*- coding:utf-8 -*-
import json
import os
import re
import sys
import random
import time

from core.config import settings
from libs import awdb
from logs.logger import logger

# file_path = r'utils/awdb/ipplus360.awdb'
# file_path = r'../utils/awdb'
file_path = settings.ROOT_DIR + '/libs/awdb'
db_name = r'ipplus360.awdb'


def ipv4_check(check_ip):
	iftrueIp = re.match(r'(([01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5])\.){3}([01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5])', check_ip)
	if iftrueIp:
		return check_ip
	else:
		return None

def get_random_ip():
	return ".".join([str(x) for x in [random.randrange(0, 255),
									  random.randrange(0, 255),
									  random.randrange(0, 255),
									  random.randrange(0, 255)]])


def read_ip_detail(check_ip):
	# co_filepath = sys._getframe().f_code.co_filename
	# head, tail = os.path.split(co_filepath)
	# os.chdir(head)
	# # print(os.getcwd())
	# os.chdir(file_path)
	# # print(os.getcwd())
	#
	# db_path = os.getcwd() + '/' + db_name
	db_path = file_path + '/' + db_name
	# print(db_path)
	check_ipv4 = ipv4_check(check_ip)
	# print(check_ipv4)
	if check_ipv4 is not None:
		reader = awdb.open_database(db_path)
		try:
			(record, prefix_len) = reader.get_with_prefix_len(check_ip)
			# print((record, prefix_len))
			accuracy = record.get("accuracy", b'') if sys.version_info[0] == 3 else record.get("accuracy", '')
			areacode = record.get("areacode", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("areacode", '')
			asnumber = record.get("asnumber", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("asnumber", '')
			city = record.get("city", b"").decode("utf-8") if sys.version_info[0] == 3 else record.get("city", "")
			continent = record.get("continent", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("continent", '')
			country = record.get("country", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("country", '')
			isp = record.get("isp", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("isp", '')
			latwgs = record.get("latwgs", b"").decode("utf-8") if sys.version_info[0] == 3 else record.get("latwgs", "")
			lngwgs = record.get("lngwgs", b"").decode("utf-8") if sys.version_info[0] == 3 else record.get("lngwgs", "")
			owner = record.get("owner", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("owner", '')
			province = record.get("province", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("province", '')
			radius = record.get("radius", b"").decode("utf-8") if sys.version_info[0] == 3 else record.get("radius", "")
			source = record.get("source", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("source", '')
			timezone = record.get("timezone", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("timezone", '')
			zipcode = record.get("zipcode", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("zipcode", '')

			result = {
				'accuracy': accuracy,
				'areacode': areacode,
				'asnumber': asnumber,
				'city': city,
				'continent': continent,
				'country': country,
				'isp': isp,
				'latwgs': latwgs,
				'lngwgs': lngwgs,
				'owner': owner,
				'province': province,
				'radius': radius,
				'source': source,
				'timezone': timezone,
				'zipcode': zipcode,
				'location': lngwgs,
			}
			# result = json.loads(get_json)
			logger.info(result)
			return {'result': result, 'msg':'success'}
		except Exception as e:
			logger.error(e)
			return {'result': e, 'msg':'fail'}
	else:
		logger.error('invalid ip <' + check_ip + '>')
		# return {'error': 'invalid ip <' + check_ip + '>'}
		return {'result': 'invalid ip <' + check_ip + '>', 'msg': 'fail'}


def main():
	# 如需解析其他字段，请根据test.py 提供的字段解析样例进行解析
	filename = file_path
	reader = awdb.open_database(filename)
	ip = '2001:DB8:0:23:8:800:200C:417A'
	# ip = '1.8.153.255'
	# ip = '118.200.27.196'
	(record, prefix_len) = reader.get_with_prefix_len(ip)
	print(record)
	if "." in ip:
		continent = record.get("continent", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("continent", '')
		country = record.get("country", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("country", '')
		zipcode = record.get("zipcode", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("zipcode", '')
		timezone = record.get("timezone", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("timezone", '')
		accuracy = record.get("accuracy", b'') if sys.version_info[0] == 3 else record.get("accuracy", '')
		source = record.get("source", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("source", '')
		owner = record.get("owner", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("owner", '')
		lngwgs = record.get("lngwgs", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("lngwgs", '')
		print("continent:" + continent)
		print("country:" + country)
		print("zipcode:" + zipcode)
		print("timezone:" + timezone)
		print("accuracy:" + accuracy)
		print("source:" + source)
		print("owner:" + owner)

		multiAreas = record.get("multiAreas", {})
		if multiAreas:
			for area in multiAreas:
				prov = area.get("prov", b"").decode("utf-8") if sys.version_info[0] == 3 else area.get("prov", "")
				city = area.get("city", b"").decode("utf-8") if sys.version_info[0] == 3 else area.get("city", "")
				district = area.get("district", b"").decode("utf-8") if sys.version_info[0] == 3 else area.get(
					"district", "")
				latwgs = area.get("latwgs", b"").decode("utf-8") if sys.version_info[0] == 3 else area.get("latwgs", "")
				lngwgs = area.get("lngwgs", b"").decode("utf-8") if sys.version_info[0] == 3 else area.get("lngwgs", "")
				latbd = area.get("latbd", b"").decode("utf-8") if sys.version_info[0] == 3 else area.get("latbd", "")
				lngbd = area.get("lngbd", b"").decode("utf-8") if sys.version_info[0] == 3 else area.get("lngbd", "")
				radius = area.get("radius", b"").decode("utf-8") if sys.version_info[0] == 3 else area.get("radius", "")
				print("prov:" + prov)
				print("city:" + city)
				print("district:" + district)
				print("latwgs:" + latwgs)
				print("lngwgs:" + lngwgs)
				print("latbd:" + latbd)
				print("lngbd:" + lngbd)
				print("radius:" + radius)
				print('---')


	elif ":" in ip:
		province = record.get("province", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("province", '')
		city = record.get("city", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("city", '')
		source = record.get("source", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("source", '')
		areacode = record.get("areacode", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("areacode", '')
		country = record.get("country", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("country", '')
		latwgs = record.get("latwgs", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("latwgs", '')
		isp = record.get("isp", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("isp", '')
		lngwgs = record.get("lngwgs", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("lngwgs", '')
		zipcode = record.get("zipcode", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("zipcode", '')
		owner = record.get("owner", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("owner", '')
		asnumber = record.get("asnumber", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("asnumber", '')
		latbd = record.get("latbd", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("latbd", '')
		timezone = record.get("timezone", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("timezone", '')
		lngbd = record.get("lngbd", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("lngbd", '')
		continent = record.get("continent", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("continent", '')
		accuracy = record.get("accuracy", b'').decode("utf-8") if sys.version_info[0] == 3 else record.get("accuracy", '')
		print("continent:" + continent)
		print("country:" + country)
		print("zipcode:" + zipcode)
		print("timezone:" + timezone)
		print("accuracy:" + accuracy)
		print("source:" + source)
		print("owner:" + owner)
		print("prov:" + province)
		print("city:" + city)
		print("latwgs:" + latwgs)
		print("lngwgs:" + lngwgs)
		print("latbd:" + latbd)
		print("lngbd:" + lngbd)
		print('---')

	else:
		print("不合法地址")

	print("record:", record)


if __name__ == '__main__':
	# main()
	# check_result = read_ip_detail('118.220.27.196')
	check_result = read_ip_detail('127.0.0.1')


