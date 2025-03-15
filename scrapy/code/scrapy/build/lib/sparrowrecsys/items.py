import scrapy

class MovieItem(scrapy.Item):
    movie_id = scrapy.Field()         # 电影ID
    name = scrapy.Field()             # 电影名称
    poster_url = scrapy.Field()       # 海报URL
    duration = scrapy.Field()         # 电影时长
    genres = scrapy.Field()           # 电影类型
    release_date = scrapy.Field()     # 发行日期
    summary = scrapy.Field()          # 简介
    director = scrapy.Field()         # 导演
    writer = scrapy.Field()           # 编剧
    stars = scrapy.Field()            # 演员












