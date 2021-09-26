#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/23 2:02 下午
# @Author  : Hanley
# @File    : encrypt.py
# @Desc    :
import base64
import hashlib

import ujson
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from cryptography.fernet import Fernet

from libs.bolts import catch_exc


class Encrypt(object):

    @staticmethod
    def pad(s):
        AES_BLOCK_SIZE = 16  # Bytes
        return s + (AES_BLOCK_SIZE - len(s) % AES_BLOCK_SIZE) * \
               chr(AES_BLOCK_SIZE - len(s) % AES_BLOCK_SIZE)

    @staticmethod
    def unpad(s):
        return s[:-ord(s[len(s) - 1:])]

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
        return Fernet.generate_key().upper().decode()

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

    @staticmethod
    @catch_exc()
    def aes_encrypt(key: str, data: str) -> str:
        '''
        AES的ECB模式加密方法
        :param key: 密钥
        :param data:被加密字符串（明文）
        :return:密文
        '''
        key = key.encode('utf8')
        # 字符串补位
        data = Encrypt.pad(data)
        cipher = AES.new(key, AES.MODE_ECB)
        # 加密后得到的是bytes类型的数据，使用Base64进行编码,返回byte字符串
        result = cipher.encrypt(data.encode())
        encodestrs = base64.b64encode(result)
        enctext = encodestrs.decode('utf8')
        return enctext

    @staticmethod
    @catch_exc()
    def aes_decrypt(key: str, data: str) -> str:
        '''
        :param key: 密钥
        :param data: 加密后的数据（密文）
        :return:明文
        '''
        key = key.encode('utf8')
        data = base64.b64decode(data)
        cipher = AES.new(key, AES.MODE_ECB)
        # 去补位
        text_decrypted = Encrypt.unpad(cipher.decrypt(data))
        text_decrypted = text_decrypted.decode('utf8')
        return text_decrypted

    @staticmethod
    @catch_exc()
    def set_fernet_token(key, data):
        '''
        加密cookies
        :param token:
        :param cookies:
        :return:
        '''
        f = Fernet(key)
        cookies_json = ujson.dumps(data)
        token = f.encrypt(cookies_json.encode())
        cookies_json = token.decode()
        return cookies_json

    @staticmethod
    @catch_exc()
    def get_fernet_token(key, data):
        '''
        解密cookies
        :param token:
        :param cookies:
        :return:
        '''
        f = Fernet(key)
        cookie_json = f.decrypt(data.encode()).decode()
        cookies_data = ujson.loads(cookie_json)
        if isinstance(cookies_data, str):
            cookies_data = ujson.loads(cookies_data)
        return cookies_data
