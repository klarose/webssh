from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Awaitable,
    Callable,
    ContextManager,
    Optional,
    ParamSpec,
)
import contextlib
import socket
import tornado.web

@dataclass
class RequestArgs:
    """
    Holds the arguments for a ssh request as received from a client. Standard arguments
    are always provided by name. The request itself passed in via request, so that
    plugins may access non-standard arguments as necessary.
    """
    hostname: str
    port: int
    username: str
    request: tornado.web.RequestHandler
    password: Optional[str] = None
    private_key: Optional[str] = None

class SocketBuilder(ABC):
    @abstractmethod
    def connect(self, args: RequestArgs)->socket.socket:
        """
        Connect to the host/port provided in the args using a custom transport (e.g.
        not necessarily raw tcp).

        Returns a socket or socket-like object.
        """
        pass
P = ParamSpec('P')

@contextlib.contextmanager
def default_error_handler(handler: tornado.web.RequestHandler):
    yield

@dataclass
class Plugins:
    socket_builder: Optional[SocketBuilder] = None
    # A set handler mappings to extend the webssh server with extra
    # behaviour (e.g. add metrics, healthchecks, etc). These use the same format
    # as normal tornado request matchers (e.g. tuples)
    handlers: list = field(default_factory=lambda: [])
    # Constructs a tornado application given a list of handlers, and settings as
    # kwargs.
    app_factory: Optional[Callable[..., tornado.web.Application]] = None
    # Modifies the connection start request in place. This can allow populating default
    # values, etc. It returns a set of overrides in a dict that will modify the values we
    # use in the request
    conn_start_updater: Optional[Callable[[tornado.web.RequestHandler], Awaitable[dict]]] = None

    # Can choose to handle an exc
    conn_error_handler: Callable[
        [tornado.web.RequestHandler],
        contextlib.AbstractContextManager
    ] = default_error_handler