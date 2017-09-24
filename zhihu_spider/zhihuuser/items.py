# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class UserItem(Item):
    # define the fields for your item here like:
    id = Field()
    name = Field()
    description = Field()
    url_token = Field()
    gender = Field()
    type = Field()

    answer_count = Field()
    favorited_count = Field()
    follower_count = Field()
    following_count = Field()
    thanked_count = Field()

    educations = Field()
    employments = Field()


class RelationItem(Item):
    active = Field()
    un_active = Field()