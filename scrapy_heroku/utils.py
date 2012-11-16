from scrapyd.utils import get_project_list

from spiderqueue import Psycopg2SpiderQueue


def get_spider_queues(config):
    queues = {}
    for project in get_project_list(config):
        table = 'scrapy_%s_queue' % project
        queues[project] = Psycopg2SpiderQueue(config, table=table)
    return queues
