import psycopg2
import cPickle
import json
import urlparse
from zope.interface import implements

from scrapyd.interfaces import ISpiderQueue


class Psycopg2PriorityQueue(object):
    def __init__(self, config, table='scrapy_queue'):
        url = urlparse.urlparse(config.get('database_url'))
        # Remove query strings.
        path = url.path[1:]
        path = path.split('?', 2)[0]

        args = {
            'dbname': path,
            'user': url.username,
            'password': url.password,
            'host': url.hostname,
            'port': url.port,
        }
        conn_string = ' '.join('%s=%s' % item for item in args.items())
        self.table = table
        self.conn = psycopg2.connect(conn_string)
        q = "create table if not exists %s " \
            "(id SERIAL primary key, " \
            " priority real, " \
            " message text);" % table
        self._execute(q, results=False)
        self.conn.commit()

    def _execute(self, q, args=None, results=True):
        cursor = self.conn.cursor()
        cursor.execute(q, args)
        if results:
            try:
                results = list(cursor)
            except psycopg2.ProgrammingError:
                results = []
        cursor.close()
        return results

    def put(self, message, priority=0.0):
        args = (priority, self.encode(message))
        q = "insert into %s (priority, message) values (%%s,%%s);" % self.table
        self._execute(q, args, results=False)
        self.conn.commit()

    def pop(self):
        q = "select id, message from %s order by priority desc limit 1 for update;" \
            % self.table
        results = self._execute(q)
        if len(results) == 0:
            return
        mid, msg = results[0]
        q = "delete from %s where id=%%s;" % self.table
        self._execute(q, (mid,), results=False)
        self.conn.commit()
        return self.decode(msg)

    def remove(self, func):
        q = "select id, message from %s for update" % self.table
        n = 0
        for mid, msg in self._execute(q):
            if func(self.decode(msg)):
                q = "delete from %s where id=%%s" % self.table
                self._execute(q, (mid,), results=False)
                n += 1
        self.conn.commit()
        return n

    def clear(self):
        self._execute("delete from %s" % self.table, results=False)
        self.conn.commit()

    def __len__(self):
        q = "select count(*) from %s" % self.table
        result = self._execute(q)[0][0]
        self.conn.commit()
        return result

    def __iter__(self):
        q = "select message, priority from %s order by priority desc" % \
            self.table
        result = ((self.decode(x), y) for x, y in self._execute(q))
        self.conn.commit()
        return result

    def encode(self, obj):
        return obj

    def decode(self, text):
        return text


class PicklePsycopg2PriorityQueue(Psycopg2PriorityQueue):
    def encode(self, obj):
        return buffer(cPickle.dumps(obj, protocol=2))

    def decode(self, text):
        return cPickle.loads(str(text))


class JsonPsycopg2PriorityQueue(Psycopg2PriorityQueue):
    def encode(self, obj):
        return json.dumps(obj)

    def decode(self, text):
        return json.loads(text)


class Psycopg2SpiderQueue(object):
    implements(ISpiderQueue)

    def __init__(self, config, table='spider_queue'):
        self.q = JsonPsycopg2PriorityQueue(config, table)

    def add(self, name, **spider_args):
        d = spider_args.copy()
        d['name'] = name
        priority = float(d.pop('priority', 0))
        self.q.put(d, priority)

    def pop(self):
        return self.q.pop()

    def count(self):
        return len(self.q)

    def list(self):
        return [x[0] for x in self.q]

    def remove(self, func):
        return self.q.remove(func)

    def clear(self):
        self.q.clear()
