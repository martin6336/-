# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from zhihuuser.items import UserItem, RelationItem

# 记住要首先创建zhihu database，然后创建user和relation两个collection
class MongoPipeline(object):
    collection_user = 'user'
    collection_relation = 'relation'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):  # 从自己这个爬虫设置文件中获取uri和db， 这一步才是真正的初始化
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def _process_user(self, item):
        self.db[self.collection_user].update({'url_token': item['url_token']}, dict(item), True)
        return item

    def _process_relation(self, item):
        self.db[self.collection_relation].update({'url_token': item['active']}, dict(item), True)
        return item

    def process_item(self, item, spider):
        """
        处理item
        """
        if isinstance(item, UserItem):
            self._process_user(item)
        elif isinstance(item, RelationItem):
            self._process_relation(item)
        return item
