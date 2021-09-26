#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/9/23 2:42 下午
# @Author  : Hanley
# @File    : kafkaClient.py
# @Desc    :
from functools import partial

import ujson
from kafka import KafkaProducer

from libs.bolts import catch_exc, yaml_config
from libs.log import logging


def rr_select(N):
    last = N - 1
    while True:
        current = (last + 1) % N
        last = current
        yield current


class KafkaEntryPoint():
    LOG_TOPIC = "cactus_log"
    _init_flag = False

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(KafkaEntryPoint, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._init_flag:
            self.init()

    def init(self):
        self.producer = self.make_producer()
        self.partitions = list(self.producer.partitions_for(self.LOG_TOPIC))
        self.partition_selector = rr_select(len(self.partitions))
        self._init_flag = True

    def make_producer(self):
        kafka_config = yaml_config("KAFKA_CLUSTER")
        connect_config = {}
        if all([kafka_config["SASL_PLAIN_USERNAME"], kafka_config["SASL_PLAIN_PASSWORD"]]):
            connect_config.update(kafka_config)
        else:
            connect_config.update(bootstrap_servers=kafka_config["BOOTSTRAP_SERVERS"])
        connect_config["key_serializer"] = lambda v: ujson.dumps(v).encode('utf-8')
        connect_config["value_serializer"] = lambda v: ujson.dumps(v).encode('utf-8')
        connect_config["max_block_ms"] = 15000
        connect_config["batch_size"] = 0
        while True:
            try:
                producer = KafkaProducer(**connect_config)
                if not producer.bootstrap_connected():
                    logging.debug("will retry connect kafka")
                    continue
            except Exception as e:
                logging.warning(f"connect kafka cluster error {e}")
                continue
            logging.debug(f"connect kafka cluster "
                          f"{kafka_config['BOOTSTRAP_SERVERS']} successful")
            return producer

    @property
    def wrapper_log_send(self):
        return partial(self.producer.send, topic=self.LOG_TOPIC)

    @catch_exc()
    def log_send(self, value=None, key=None, headers=None, timestamp_ms=None):
        partition = self.partition_selector.__next__()
        return self.wrapper_log_send(
            key=key,
            headers=headers,
            value=value,
            partition=partition,
            timestamp_ms=timestamp_ms
        )

    @catch_exc()
    def close(self):
        self.producer.flush(15)
        self.producer.close(15)
