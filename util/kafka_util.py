#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/4/18 9:15 下午
# @Author  : Hanley
# @File    : kafka_util.py
# @Desc    :

import random
from functools import partial

import ujson
from kafka import KafkaProducer


class KafkaEntryPoint():
    LOG_TOPIC = "yunqipei_log"

    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=[
                "192.168.191.131:9092",
                "192.168.191.13:9092",
                "192.168.191.47:9092"
            ],
            key_serializer=lambda v: ujson.dumps(v).encode('utf-8'),
            value_serializer=lambda v: ujson.dumps(v).encode('utf-8'),
            max_block_ms=5000,
            sasl_mechanism="PLAIN",
            security_protocol="SASL_PLAINTEXT",
            sasl_plain_username="yunqipei",
            sasl_plain_password="jtOfbXTPURhVZ"
        )

    @property
    def log_partition_list(self) -> list:
        return list(self.producer.partitions_for(self.LOG_TOPIC))

    @property
    def wrapper_log_send(self):
        return partial(self.producer.send, topic=self.LOG_TOPIC)

    def log_send(self, value=None, key=None, headers=None, timestamp_ms=None):
        if len(self.log_partition_list) > 1:
            partition = random.choice(self.log_partition_list)
        else:
            partition = 0
        self.wrapper_log_send(
            key=key,
            headers=headers,
            value=value,
            partition=partition,
            timestamp_ms=timestamp_ms
        )
