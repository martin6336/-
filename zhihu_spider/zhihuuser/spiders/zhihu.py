# -*- coding: utf-8 -*-
import json

from scrapy import Spider, Request
from zhihuuser.items import UserItem, RelationItem
import time  # 速度过快会封ip的，貌似只要在界面输入验证码就可以解除了
import random

class ZhihuSpider(Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    start_user = 'pa-chong-21'  # 起始页可以更换
    user_query = 'locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,answer_count,articles_count,pins_count,question_count,commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,message_thread_token,account_status,is_active,is_force_renamed,is_bind_sina,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics'
    follows_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user, include=self.user_query), self.parse_user)
        # yield Request(self.follows_url.format(user=self.start_user, include=self.follows_query, limit=20, offset=0),
        #               self.parse_follows)
        # yield Request(self.followers_url.format(user=self.start_user, include=self.followers_query, limit=20, offset=0),
        #               self.parse_followers)

    def parse_user(self, response):
        result = json.loads(response.text)
        item = UserItem()

        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item  # 用户信息
        time.sleep(random.uniform(0.5, 1))
        yield Request(
            self.follows_url.format(user=result.get('url_token'), include=self.follows_query, limit=20, offset=0),
            self.get_next_follow, meta={'latter': result.get('url_token')})

        yield Request(
            self.followers_url.format(user=result.get('url_token'), include=self.followers_query, limit=20, offset=0),
            self.get_next_follower, meta={'latter': result.get('url_token')})  # meta传导发起的token，便于形成网络

    def get_next_follow(self, response):
        yield Request(response.url, callback=self.parse_follows, meta={'latter': response.meta['latter']})
        results = json.loads(response.text)
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page, self.parse_follows, meta={'latter': response.meta['latter']})
            yield Request(next_page, callback=self.get_next_follow, meta={'latter': response.meta['latter']})

    def get_next_follower(self, response):
        yield Request(response.url, callback=self.parse_followers, meta={'latter': response.meta['latter']})
        results = json.loads(response.text)
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page, self.parse_followers, meta={'latter': response.meta['latter']})
            yield Request(response.url, callback=self.get_next_follower, meta={'latter': response.meta['latter']})

    def parse_follows(self, response):

        results = json.loads(response.text)
#         if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
#             next_page = results.get('paging').get('next')
#             yield Request(next_page,
#                           self.parse_follows)  # 回调自己去分析下一页,但是这个过程中可能有其他堆积的请求，所以可能不存在把一个人全分析完了在分析下一个人
#  两个if交换一下顺序就能爬完一个的follow再爬另一个，这个观点是错的
        if 'data' in results.keys():  # 有的可能没有关注或者粉丝
            for result in results.get('data'):  # get以列表形式返回
                time.sleep(random.uniform(0.5, 1))
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query),
                              self.parse_user)
                yield RelationItem(active=response.meta['latter'], un_active=result.get('url_token'))

    def parse_followers(self, response):
        results = json.loads(response.text)
        # if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
        #     next_page = results.get('paging').get('next')
        #     yield Request(next_page,
        #                   self.parse_followers)

        if 'data' in results.keys():
            for result in results.get('data'):
                time.sleep(random.uniform(0.5, 1))
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query),
                              self.parse_user)
                yield RelationItem(active=result.get('url_token'), un_active=response.meta['latter'])