from os import environ

from twisted.application.service import Application
from twisted.application.internet import TimerService, TCPServer
from twisted.web import server
from twisted.python import log

from scrapyd.interfaces import (IEggStorage, IPoller, ISpiderScheduler,
    IEnvironment)
from scrapyd.launcher import Launcher
from scrapyd.eggstorage import FilesystemEggStorage
from scrapyd.environ import Environment
from scrapyd.website import Root

from .scheduler import Psycopg2SpiderScheduler
from .poller import Psycopg2QueuePoller


def application(config):
    app = Application("Scrapyd")
    http_port = int(environ.get('PORT', config.getint('http_port', 6800)))
    config.cp.set('scrapyd', 'database_url', environ.get('DATABASE_URL'))

    poller = Psycopg2QueuePoller(config)
    eggstorage = FilesystemEggStorage(config)
    scheduler = Psycopg2SpiderScheduler(config)
    environment = Environment(config)

    app.setComponent(IPoller, poller)
    app.setComponent(IEggStorage, eggstorage)
    app.setComponent(ISpiderScheduler, scheduler)
    app.setComponent(IEnvironment, environment)

    launcher = Launcher(config, app)
    timer = TimerService(5, poller.poll)
    webservice = TCPServer(http_port, server.Site(Root(config, app)))
    log.msg("Scrapyd web console available at http://localhost:%s/ (HEROKU)"
        % http_port)

    launcher.setServiceParent(app)
    timer.setServiceParent(app)
    webservice.setServiceParent(app)

    return app
