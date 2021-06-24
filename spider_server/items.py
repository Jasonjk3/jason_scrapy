# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboItem(scrapy.Item):
    """ 微博信息 """
    mongodb_spiders = ['weiboDetailV1']
    mongodb_collections = ['weibo_data']
    mongodb_action = 'update'

    id = scrapy.Field()  # 微博id
    weibo_url = scrapy.Field()  # 微博URL
    created_at = scrapy.Field()  # 微博发表时间
    like_num = scrapy.Field()  # 点赞数
    repost_num = scrapy.Field()  # 转发数
    comment_num = scrapy.Field()  # 评论数
    content = scrapy.Field()  # 微博内容
    user_id = scrapy.Field()  # 发表该微博用户的id
    tool = scrapy.Field()  # 发布微博的工具
    image_url = scrapy.Field()  # 图片
    video_url = scrapy.Field()  # 视频
    location = scrapy.Field()  # 定位信息
    origin_weibo = scrapy.Field()  # 原始微博，只有转发的微博才有这个字段
    crawled_at = scrapy.Field()  # 抓取时间戳


class WeiboTopicItem(scrapy.Item):
    """ 微博话题信息 """
    mongodb_spiders = ['weiboTopicSearchRedisV3']
    mongodb_collections = ['weibo_topic4']
    mongodb_action = 'update'
    primary_key = 'topic'
    kafka_topic = 'test'
    kafka_key = 'weibo_topic'

    id = scrapy.Field()  # 话题id
    topic = scrapy.Field()  # 话题名
    read_num = scrapy.Field()  # 阅读人数
    discussion_num = scrapy.Field()  # 讨论人数
    topic_lead = scrapy.Field()  # 话题导语
    tags = scrapy.Field()  # 话题标签
    top_item_id = scrapy.Field()  # 话题置顶微博
    top_item_username = scrapy.Field()  # 话题置顶微博用户名
    top_item_content = scrapy.Field()  # 话题置顶微博内容
    top_item_repost = scrapy.Field()  # 话题置顶微博转发数
    top_item_comment = scrapy.Field()  # 话题置顶微博评论数
    top_item_like = scrapy.Field()  # 话题置顶微博点赞数
    items_id = scrapy.Field()  # 话题下的微博Id
    datetime = scrapy.Field()  # 当天时间
    detail_url = scrapy.Field()  # url


class WeiboCommentsItem(scrapy.Item):
    """ 微博评论信息 """
    mongodb_spiders = ['weiboCommentsV2']
    mongodb_collections = ['weibo_comments4']
    mongodb_action = 'update'
    primary_key = 'comment_id'
    kafka_topic = 'test'
    kafka_key = 'weibo_comment'

    item_id = scrapy.Field()  # 微博id
    comment_id = scrapy.Field()  # 评论id
    createtime = scrapy.Field()  # 评论时间
    text = scrapy.Field()  # 评论内容
    uid = scrapy.Field()  # 用户id
    like_count = scrapy.Field()  # 评论用户点赞量
    # username = scrapy.Field()  # 用户名
    # following = scrapy.Field()  # 用户关注数
    # followed = scrapy.Field()  # 用户粉丝数
    # gender = scrapy.Field()  # 性别


class WeibUserItem(scrapy.Item):
    """ 微博用户信息 """
    mongodb_spiders = ['weiboUserDetailV3']
    mongodb_collections = ['weibo_users4']
    mongodb_action = 'update'
    primary_key = 'uid'
    kafka_topic = 'test'
    kafka_key = 'weibo_user'

    uid = scrapy.Field()  # 用户id
    url = scrapy.Field()  # url
    username = scrapy.Field()  # 用户名
    following = scrapy.Field()  # 用户关注数
    followed = scrapy.Field()  # 用户粉丝数
    gender = scrapy.Field()  # 性别
    location = scrapy.Field()  # 地区
    edu = scrapy.Field()  # 教育
    birthday = scrapy.Field()  # 生日
    post_num = scrapy.Field()  # 微博数


class BilibiliVideoDetailItem(scrapy.Item):
    bvid = scrapy.Field()
    oid = scrapy.Field()
    tag = scrapy.Field()
    title = scrapy.Field()
    play = scrapy.Field()
    pubdate = scrapy.Field()
    review = scrapy.Field()  # 评论
    favorites = scrapy.Field()
    duration = scrapy.Field()
    author = scrapy.Field()
    video_review = scrapy.Field()  # 弹幕
    like = scrapy.Field()
    coin = scrapy.Field()
    share = scrapy.Field()
    view = scrapy.Field()  # 正在观看人数
    comment_list = scrapy.Field()
    video_url = scrapy.Field()


class XimalayaDetailItem(scrapy.Item):
    """喜马拉雅"""

    mongodb_spiders = ['ximalayaDetail', 'ximalayaCategory']
    mongodb_collections = ['ximalaya_data']

    url = scrapy.Field()  # 网址
    id = scrapy.Field()  # FM id
    tags = scrapy.Field()  # 头部标签
    title = scrapy.Field()  # 标题
    score = scrapy.Field()  # 评分
    play_num = scrapy.Field()  # 播放量
    content = scrapy.Field()  # 内容简介
    number = scrapy.Field()  # 内容集数
    comments_num = scrapy.Field()  # 评论数
    up_name = scrapy.Field()  # 主播名
    up_fans_num = scrapy.Field()  # 主播粉丝数
    up_url = scrapy.Field()  # 主播链接
    up_content = scrapy.Field()  # 主播简介
    search_keywords = scrapy.Field()  # 相关关键词搜索


class IqiyiDetailItem(scrapy.Item):
    """爱奇艺"""
    # mongodb 配置
    mongodb_spiders = ['iqiyiDetail']  # 允许的爬虫范围
    mongodb_collections = ['iqiyi_data']  # 集合范围
    mongodb_action = 'update'  # insert or update

    url = scrapy.Field()  # 网址
    id = scrapy.Field()  # aid
    title = scrapy.Field()  # 标题
    hot_num = scrapy.Field()  # 视频热度
    categories = scrapy.Field()  # 分类
    description = scrapy.Field()  # 描述
    focus = scrapy.Field()  # 亮点
    period = scrapy.Field()  # 发布时间
    score = scrapy.Field()  # 评分
