#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:21
# @Author  : Hanley
# @File    : library.py
# @Desc    : 公共方法文件

import base64
import configparser
import datetime
import fcntl
import filecmp
import hashlib
import os
import pathlib
import random
import re
import time
import traceback
import uuid
from functools import wraps, lru_cache
from math import radians
from math import sin, cos, asin, sqrt
from random import choice
from string import ascii_letters

import ujson
import xmltodict
import yaml
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from aiohttp import ClientSession, TCPConnector
from cryptography.fernet import Fernet
from requests import adapters
from requests.sessions import Session
from retry import retry

from library.constants import Constant
from library.initlog import logging


def str_now(): return time.strftime("%Y-%m-%d %X")


def datetime_now(): return datetime.datetime.now()


def perf_time(): return time.perf_counter()


def catch_exc(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(e)
            logging.error(traceback.format_exc())

    return wrapper


def singleton(cls):
    """
    类装饰器单例
    :param cls:
    :return:
    """
    _instance = {}

    @wraps(cls)
    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


class Common(object):

    @staticmethod
    def yaml_config(key=None, file_path=Constant.YAML_CONFIG):
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
        if key:
            return config.get(key)
        return config

    @staticmethod
    def ini_config(section=None, file_path=Constant.INI_CONFIG) -> dict:
        config = configparser.ConfigParser()
        config.read(file_path)
        if isinstance(section, str):
            section = section.lower()
        options = config.options(section)
        dict_result = {}
        for option in options:
            temp = config.get(section, option)
            dict_result.update({option: temp})
        return dict_result

    @staticmethod
    def random_string(length=10):
        return ''.join(choice(ascii_letters) for _ in range(length))

    @staticmethod
    def generate_random_id() -> str:
        now = datetime.datetime.now().strftime("%Y%m%d")
        unix = str(time.time()).replace('.', "")[-10:]
        rand_ind = random.randint(1000, 9999)
        return ''.join([now[-6:], unix, str(rand_ind)])

    @staticmethod
    def generate_uuid() -> str:
        _uuid1 = str(uuid.uuid1())
        return str(uuid.uuid3(uuid.NAMESPACE_DNS, _uuid1)).replace('-', '')

    @staticmethod
    def format_datetime(data):
        if isinstance(data, datetime.datetime):
            return data.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(data, datetime.date):
            return data.strftime("%Y-%m-%d")
        else:
            return data

    @staticmethod
    def validate_phone(phone_number: str) -> bool:
        mobile = r"13\d{9}|14\d{9}|15\d{9}|16\d{9}|17\d{9}|18\d{9}|19\d{9}"
        landline = r"^[0][1-9]{2,3}-[0-9]{5,10}$"

        mobile_pattern = re.compile(mobile)
        landline_pattern = re.compile(landline)

        def _check(p):
            return p.findall(phone_number)

        if len(phone_number) == 11 and "-" not in phone_number:
            return True if _check(mobile_pattern) else False
        else:
            return True if _check(landline_pattern) else False

    @staticmethod
    def cp_file(source_file, target_file):
        if filecmp.cmp(target_file, source_file):
            return
        with open(source_file, 'r') as sf:
            with open(target_file, 'w') as tf:
                fcntl.lockf(tf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                while True:
                    data = sf.read(4069)
                    if not data:
                        break
                    tf.write(data)

    @staticmethod
    def init_config_file(env: str):
        """
        项目配置文件环境切换
        :param env:
        :return:
        """
        if env not in ("prod", "dev", "local"):
            return
        FILE_MAP = {
            'prod': 'config_prod.yaml',
            'dev': "config_dev.yaml",
            'local': 'config_local.yaml'
        }
        source_file = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__))), FILE_MAP.get(env))
        target_file = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__))), 'config.yaml')
        not os.path.exists(target_file) and pathlib.Path(target_file).touch()

        Common.cp_file(source_file, target_file)

    @staticmethod
    def dict2xml(dict_data, root="xml") -> str:
        """
        字典转xml
        dict_data: 字典数据
        root：根结点标签
        """
        _dictXml = {root: dict_data}
        xmlstr = xmltodict.unparse(_dictXml, pretty=True)
        return xmlstr

    @staticmethod
    def xml2dict(xml_data) -> dict:
        """
        xml转dict
        xml_data: xml字符串
        return: dict字符串
        """
        data = xmltodict.parse(xml_data, process_namespaces=True)
        return dict(list(data.values())[0])

    @staticmethod
    @lru_cache()
    def distance_calc_auto(startloc, endloc) -> float:
        """
        # 手动精确计算
        :param startloc: 经度+','+维度
        :param endloc: 经度+','+维度
        :return:
        """
        startloc = startloc + ',' + endloc
        # 将十进制度数转化为弧度
        lon1, lat1, lon2, lat2 = map(
            radians, [float(i) for i in startloc.split(',')])
        # haversine公式
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        # 地球平均半径，单位为公里
        r = 6371
        dictance = '%.3f' % (r * c)
        return float(dictance)


@singleton
class Encrypt(object):

    # base64加密
    @staticmethod
    def b64_encrypt(data: (str, bytes)) -> str:
        if isinstance(data, str):
            data = data.encode('utf-8')
        enb64_str = base64.b64encode(data)
        return enb64_str.decode('utf-8')

    # base64解密
    @staticmethod
    def b64_decrypt(data: str) -> str:
        deb64_str = base64.b64decode(data)
        return deb64_str.decode('utf-8')

    # base64对url加密
    @staticmethod
    def url_b64_encrypt(data: str) -> str:
        enb64_str = base64.urlsafe_b64encode(data.encode('utf-8'))
        return enb64_str.decode("utf-8")

    # base64对url解密
    @staticmethod
    def url_b64_decrypt(data: str) -> str:
        deb64_str = base64.urlsafe_b64decode(data)
        return deb64_str.decode("utf-8")

    # hashlib md5加密
    @staticmethod
    def hash_md5_encrypt(data: (str, bytes), salt=None) -> str:
        if isinstance(data, str):
            data = data.encode('utf-8')
        md5 = hashlib.md5()
        if salt:
            if isinstance(salt, str):
                salt = salt.encode('utf-8')
            md5.update(salt)
        md5.update(data)
        return md5.hexdigest()

    # hashlib sha1加密
    @staticmethod
    def hash_sha1_encrypt(data: (str, bytes), salt=None) -> str:
        if isinstance(data, str):
            data = data.encode('utf-8')
        md5 = hashlib.sha1()
        if salt:
            if isinstance(salt, str):
                salt = salt.encode('utf-8')
            md5.update(salt)
        md5.update(data)
        return md5.hexdigest()

    # hashlib sha256加密
    @staticmethod
    def hash_sha256_encrypt(data: (str, bytes), salt=None) -> str:
        if isinstance(data, str):
            data = data.encode('utf-8')
        md5 = hashlib.sha256()
        if salt:
            if isinstance(salt, str):
                salt = salt.encode('utf-8')
            md5.update(salt)
        md5.update(data)
        return md5.hexdigest()

    @staticmethod
    def generate_secret(block_size=16):
        return base64.encodebytes(
            get_random_bytes(
                block_size)).strip().decode()

    @staticmethod
    def generate_fernet_key():
        return Fernet.generate_key()

    @staticmethod
    def build_sign(dict_param: dict) -> str:
        """
        生成字典参数签名
        """
        param_list = sorted(dict_param.keys())
        string = ""
        for param in param_list:
            if dict_param[param]:
                string += f"{param}={dict_param[param]}&"
        md5_sign = Encrypt.hash_md5_encrypt(string)
        return md5_sign.upper()

    # Crypto AES加密
    @staticmethod
    @catch_exc
    def crypto_encrypt(data: (str, bytes), secret: str, block_size=16) -> str:
        def _pad(pending_bytes) -> bytes:
            if len(pending_bytes) % 16 != 0:
                plaintext = pad(pending_bytes, block_size)
                return _pad(plaintext)
            else:
                plaintext = pending_bytes
            return plaintext

        if isinstance(data, str):
            data = data.encode('utf-8')
        cipher = AES.new(secret.encode('utf-8'), AES.MODE_ECB)
        encrypt_plaintext = _pad(data)
        msg = cipher.encrypt(encrypt_plaintext)
        return msg.hex()

    # Crypto AES解密
    @staticmethod
    @catch_exc
    def crypto_decrypt(data: str, secret: str, block_size=16) -> str:
        decipher = AES.new(secret.encode('utf-8'), AES.MODE_ECB)
        msg_dec = decipher.decrypt(bytes.fromhex(data))
        result = unpad(msg_dec, block_size).decode()
        return result

    @staticmethod
    def make_encrypt(parameter: dict, secret: str, sign_key='encrypt') -> dict:
        """
        支付加密
        :param parameter: 支付请求参数
        :param secret: 密钥
        :param sign_key: 加密字段名
        encrypt（加密字符）
        :return: 携带加密后parameter
        """
        _sign = Encrypt.build_sign(parameter)
        encrypt_sign = Encrypt.crypto_encrypt(_sign, secret)
        parameter.setdefault(sign_key, encrypt_sign)
        return parameter

    @staticmethod
    def make_decrypt(parameter: dict, secret: str,
                     sign_key='encrypt') -> tuple:
        """
        支付解密
        :param parameter: 支付请求参数（携带encrypt）
        :param secret: 密钥
        :param sign_key: 加密字段名
        :return:
        """
        decrypt_encrypt = parameter.pop(sign_key, "")
        _sign = Encrypt.build_sign(parameter)
        decrypt = Encrypt.crypto_decrypt(decrypt_encrypt, secret)
        if decrypt != _sign:
            return False, parameter
        return True, parameter

    @staticmethod
    @catch_exc
    def encrypt_fernet(key, data):
        '''
        Fernet 加密
        :param key:
        :param data:
        :return:
        '''
        f = Fernet(key)
        cookies_json = ujson.dumps(data)
        token = f.encrypt(cookies_json.encode())
        cookies_json = token.decode()
        return cookies_json

    @staticmethod
    @catch_exc
    def decrypt_fernet(key, data):
        '''
        Fernet 解密
        :param key:
        :param data:
        :return:
        '''
        f = Fernet(key)
        cookie_json = f.decrypt(data.encode()).decode()
        cookies_data = ujson.loads(cookie_json)
        return cookies_data


class SyncClientSession(Session):
    """
    sync request client
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(SyncClientSession, cls).__new__(cls)
        return cls._instance

    def __init__(self, time_out=2, pool_num=10,
                 pool_max_size=50, max_retries=3):
        super(SyncClientSession, self).__init__()
        self._time_out = time_out
        self._pool_num = pool_num
        self._pool_max_size = pool_max_size
        self._max_retries = max_retries
        self.mount("http://", adapters.HTTPAdapter(
            pool_connections=self._pool_num,
            pool_maxsize=self._pool_max_size,
            max_retries=self._max_retries
        ))
        self.mount("https://", adapters.HTTPAdapter(
            pool_connections=self._pool_num,
            pool_maxsize=self._pool_max_size,
            max_retries=self._max_retries
        ))

    def request(self, method, url, headers=None, timeout=None, **kwargs):
        timeout = timeout or self._time_out
        headers = headers or {}
        if not headers.get("X-Request-ID"):
            headers["X-Request-ID"] = uuid.uuid4().hex
        return super().request(
            method, url, headers=headers, timeout=timeout, **kwargs)


class AsyncClientSession:
    """
    async aiohttp client
    """
    __slots__ = (
        "session",
    )

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(AsyncClientSession, cls).__new__(cls)
        return cls._instance

    async def init_session(self, **kwargs) -> ClientSession:
        """
        aiohttp client session
        :return:
        """
        tcp_connector = TCPConnector(
            keepalive_timeout=15,
            limit=600,
            limit_per_host=300,
            **kwargs
        )
        self.session = ClientSession(connector=tcp_connector)
        return self.session

    @retry(tries=3, logger=logging)
    async def request(self, method, url, **kwargs):
        return await self.session.request(method, url, **kwargs)

    @retry(tries=3, logger=logging)
    async def fetch_json(self, method, url, **kwargs):
        async with self.session.request(method, url, **kwargs) as response:
            return await response.json()

    async def close(self):
        await self.session.close()
