from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Union
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
    password: Union[str, None] = None
    private_key: Union[str, None] = None

class SocketBuilder(ABC):
    @abstractmethod
    def connect(self, args: RequestArgs)->socket.socket:
        """
        Connect to the host/port provided in the args using a custom transport (e.g.
        not necessarily raw tcp).

        Returns a socket or socket-like object.
        """
        pass

@dataclass
class Plugins:
    socket_builder: Union[SocketBuilder, None] = None
    # A set handler mappings to extend the webssh server with extra
    # behaviour (e.g. add metrics, healthchecks, etc). These use the same format
    # as normal tornado request matchers (e.g. tuples)
    handlers: list = field(default_factory=lambda: [])
