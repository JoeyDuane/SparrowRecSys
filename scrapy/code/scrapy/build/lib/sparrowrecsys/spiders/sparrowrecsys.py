import scrapy
import logging
import unicodedata
import time
from sparrowrecsys.items import MovieItem
from scrapy.http import Request
from bs4 import BeautifulSoup


class SparrowRecSysSpider(scrapy.Spider):
    name = 'sparrowrecsys'
    allowed_domains = ['imdb.com']
    start_urls = ['https://www.imdb.com/title/tt0000000']  # 初始URL（可根据需求修改）

    def __init__(self, *args, **kwargs):
        super(SparrowRecSysSpider, self).__init__(*args, **kwargs)
        self.movie_dct = {}
        self.white_lst = []
        self.url = 'https://www.imdb.com/title/'
        self.movie_csv_path = '/mnt/data/links.csv'
        self.poster_save_path = '/mnt/data/info'
        self.info_save_path = '/mnt/data/poster'

    def start_requests(self):
        # 读取已处理的白名单
        self.get_white_lst()
        # 获取电影ID
        self.get_movie_id()

        for movie_id, imdb_id in self.movie_dct.items():
            if movie_id in self.white_lst:
                continue
            url = f'{self.url}tt{imdb_id}'
            yield Request(url, callback=self.parse, meta={'movie_id': movie_id, 'imdb_id': imdb_id})

    def get_white_lst(self):
        '''读取白名单'''
        try:
            with open('white_list/white_list', 'r') as fb:
                self.white_lst = [line.strip() for line in fb.readlines()]
        except FileNotFoundError:
            self.white_lst = []

    def get_movie_id(self):
        '''获取电影id和imdb id'''
        try:
            with open(self.movie_csv_path, 'r') as fb:
                for line in fb.readlines()[1:]:  # 跳过表头
                    line = line.strip().split(',')
                    self.movie_dct[line[0]] = line[1]
        except FileNotFoundError:
            self.movie_dct = {}

    def parse(self, response):
        movie_id = response.meta['movie_id']
        imdb_id = response.meta['imdb_id']

        item = MovieItem()
        item['movie_id'] = movie_id
        item['name'] = self.get_name(response)
        item['poster_url'] = self.get_poster_url(response)
        item['duration'] = self.get_duration(response)
        item['genres'], item['release_date'] = self.get_genres_and_release_date(response)
        item['summary'] = self.get_summary(response)
        item['director'], item['writer'], item['stars'] = self.get_cast_and_crew(response)

        # 更新白名单
        self.update_white_lst(movie_id)

        yield item

    def get_name(self, response):
        '''获取电影名称'''
        name = response.css('h1::text').get().strip()
        return unicodedata.normalize('NFKC', name)

    def get_poster_url(self, response):
        '''获取海报URL'''
        poster_url = response.css('.poster img::attr(src)').get()
        return poster_url or ''

    def get_duration(self, response):
        '''获取电影时长'''
        duration = response.css('.subtext time::text').get()
        return duration.strip() if duration else ''

    def get_genres_and_release_date(self, response):
        '''获取电影类型和发布日期'''
        subtext = response.css('.subtext')
        genres = subtext.css('a::text').getall()[:-1]  # 去掉最后的发布日期
        release_date = subtext.css('a::text').getall()[-1] if subtext else ''
        return '|'.join(genres), release_date.strip()

    def get_summary(self, response):
        '''获取电影简介'''
        summary = response.css('.summary_text::text').get().strip()
        return unicodedata.normalize('NFKC', summary)

    def get_cast_and_crew(self, response):
        '''获取导演，编剧和演员'''
        case_dict = {'D': [], 'W': [], 'S': []}
        for item in response.css('.credit_summary_item'):
            role = item.css('h4::text').get().strip()
            people = item.css('a::text').getall()
            if role.startswith('Director'):
                case_dict['D'].extend(people)
            elif role.startswith('Writer'):
                case_dict['W'].extend(people)
            elif role.startswith('Star'):
                case_dict['S'].extend(people)

        return '|'.join(case_dict['D']), '|'.join(case_dict['W']), '|'.join(case_dict['S'])

    def update_white_lst(self, movie_id):
        '''更新白名单'''
        with open('white_list/white_list', 'a+') as fb:
            fb.write(movie_id + '\n')

