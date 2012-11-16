from zope.interface import implements

from scrapyd.interfaces import ISpiderScheduler

from .spiderqueue import Psycopg2SpiderQueue
from .utils import get_project_list


class Psycopg2SpiderScheduler(object):
    implements(ISpiderScheduler)

    def __init__(self, config, **pg_args):
        self.config = config
        self.pg_args = pg_args
        self.update_projects()

    def schedule(self, project, spider_name, **spider_args):
        q = self.queues[project]
        q.add(spider_name, **spider_args)

    def list_projects(self):
        return self.queues.keys()

    def update_projects(self):
        self.queues = {}
        for project in get_project_list(self.config):
            table = 'scrapy_%s_queue' % project
            self.queues[project] = Psycopg2SpiderQueue(table, **self.pg_args)
