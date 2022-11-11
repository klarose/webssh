import logging
import tornado.web
import tornado.ioloop

from tornado.options import options
from webssh import handler
from webssh.handler import IndexHandler, WsockHandler, NotFoundHandler
from webssh.plugins import Plugins
from webssh.settings import (
    get_app_settings,  get_host_keys_settings, get_policy_setting,
    get_ssl_context, get_server_settings, check_encoding_setting
)

_servers = []

def make_handlers(loop, options, plugins: Plugins):
    host_keys_settings = get_host_keys_settings(options)
    policy = get_policy_setting(options, host_keys_settings)

    handlers = plugins.handlers.copy()
    handlers.extend([
        (r'/', IndexHandler, dict(loop=loop, policy=policy,
                                  host_keys_settings=host_keys_settings,
                                  plugins=plugins)),
        (r'/ws', WsockHandler, dict(loop=loop))
    ])

    return handlers


def make_app(handlers, settings, plugins: Plugins):
    settings.update(default_handler_class=NotFoundHandler)
    if plugins.app_factory:
        return plugins.app_factory(handlers, **settings)

    return tornado.web.Application(handlers, **settings)


def app_listen(app, port, address, server_settings):
    server = app.listen(port, address, **server_settings)
    if not server_settings.get('ssl_options'):
        server_type = 'http'
    else:
        server_type = 'https'
        handler.redirecting = True if options.redirect else False
    logging.info(
        'Listening on {}:{} ({})'.format(address, port, server_type)
    )

    return server

def run_server(options, plugins: Plugins):
    check_encoding_setting(options.encoding)
    loop = tornado.ioloop.IOLoop.current()
    app = make_app(
        make_handlers(loop, options, plugins),
        get_app_settings(options),
        plugins
    )
    ssl_ctx = get_ssl_context(options)
    server_settings = get_server_settings(options)
    server = app_listen(app, options.port, options.address, server_settings)
    _servers.append(server)
    if ssl_ctx:
        server_settings.update(ssl_options=ssl_ctx)
        server = app_listen(app, options.sslport, options.ssladdress, server_settings)
        _servers.append(server)
    loop.start()

def get_servers():
    """
    Returns the tornado http servers started by run_server.
    """
    return _servers

def main():
    options.parse_command_line()
    run_server(options, Plugins())


if __name__ == '__main__':
    main()
