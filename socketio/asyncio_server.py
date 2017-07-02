import asyncio

import engineio

from . import asyncio_manager
from . import packet
from . import server


class AsyncServer(server.Server):
    """A Socket.IO server for asyncio.

    This class implements a fully compliant Socket.IO web server with support
    for websocket and long-polling transports, compatible with the asyncio
    framework on Python 3.5 or newer.

    :param client_manager: The client manager instance that will manage the
                           client list. When this is omitted, the client list
                           is stored in an in-memory structure, so the use of
                           multiple connected servers is not possible.
    :param logger: To enable logging set to ``True`` or pass a logger object to
                   use. To disable logging set to ``False``.
    :param json: An alternative json module to use for encoding and decoding
                 packets. Custom json modules must have ``dumps`` and ``loads``
                 functions that are compatible with the standard library
                 versions.
    :param async_handlers: If set to ``True``, event handlers are executed in
                           separate threads. To run handlers synchronously,
                           set to ``False``. The default is ``False``.
    :param kwargs: Connection parameters for the underlying Engine.IO server.

    The Engine.IO configuration supports the following settings:

    :param async_mode: The asynchronous model to use. See the Deployment
                       section in the documentation for a description of the
                       available options. Valid async modes are "aiohttp". If
                       this argument is not given, an async mode is chosen
                       based on the installed packages.
    :param ping_timeout: The time in seconds that the client waits for the
                         server to respond before disconnecting.
    :param ping_interval: The interval in seconds at which the client pings
                          the server.
    :param max_http_buffer_size: The maximum size of a message when using the
                                 polling transport.
    :param allow_upgrades: Whether to allow transport upgrades or not.
    :param http_compression: Whether to compress packages when using the
                             polling transport.
    :param compression_threshold: Only compress messages when their byte size
                                  is greater than this value.
    :param cookie: Name of the HTTP cookie that contains the client session
                   id. If set to ``None``, a cookie is not sent to the client.
    :param cors_allowed_origins: List of origins that are allowed to connect
                                 to this server. All origins are allowed by
                                 default.
    :param cors_credentials: Whether credentials (cookies, authentication) are
                             allowed in requests to this server.
    :param engineio_logger: To enable Engine.IO logging set to ``True`` or pass
                            a logger object to use. To disable logging set to
                            ``False``.
    """
    def __init__(self, client_manager=None, logger=False, json=None,
                 async_handlers=False, **kwargs):
        if client_manager is None:
            client_manager = asyncio_manager.AsyncManager()
        super().__init__(client_manager=client_manager, logger=logger,
                         binary=False, json=json,
                         async_handlers=async_handlers, **kwargs)

    def is_asyncio_based(self):
        return True

    def attach(self, app, socketio_path='socket.io'):
        """Attach the Socket.IO server to an application."""
        self.eio.attach(app, socketio_path)

    async def emit(self, event, data=None, room=None, skip_sid=None,
                   namespace=None, callback=None, **kwargs):
        """Emit a custom event to one or more connected clients.

        :param event: The event name. It can be any string. The event names
                      ``'connect'``, ``'message'`` and ``'disconnect'`` are
                      reserved and should not be used.
        :param data: The data to send to the client or clients. Data can be of
                     type ``str``, ``bytes``, ``list`` or ``dict``. If a
                     ``list`` or ``dict``, the data will be serialized as JSON.
        :param room: The recipient of the message. This can be set to the
                     session ID of a client to address that client's room, or
                     to any custom room created by the application, If this
                     argument is omitted the event is broadcasted to all
                     connected clients.
        :param skip_sid: The session ID of a client to skip when broadcasting
                         to a room or to all clients. This can be used to
                         prevent a message from being sent to the sender.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the event is emitted to the
                          default namespace.
        :param callback: If given, this function will be called to acknowledge
                         the the client has received the message. The arguments
                         that will be passed to the function are those provided
                         by the client. Callback functions can only be used
                         when addressing an individual client.
        :param ignore_queue: Only used when a message queue is configured. If
                             set to ``True``, the event is emitted to the
                             clients directly, without going through the queue.
                             This is more efficient, but only works when a
                             single server process is used. It is recommended
                             to always leave this parameter with its default
                             value of ``False``.

        Note: this method is a coroutine.
        """
        namespace = namespace or '/'
        self.logger.info('emitting event "%s" to %s [%s]', event,
                         room or 'all', namespace)
        await self.manager.emit(event, data, namespace, room, skip_sid,
                                callback, **kwargs)

    async def send(self, data, room=None, skip_sid=None, namespace=None,
                   callback=None, **kwargs):
        """Send a message to one or more connected clients.

        This function emits an event with the name ``'message'``. Use
        :func:`emit` to issue custom event names.

        :param data: The data to send to the client or clients. Data can be of
                     type ``str``, ``bytes``, ``list`` or ``dict``. If a
                     ``list`` or ``dict``, the data will be serialized as JSON.
        :param room: The recipient of the message. This can be set to the
                     session ID of a client to address that client's room, or
                     to any custom room created by the application, If this
                     argument is omitted the event is broadcasted to all
                     connected clients.
        :param skip_sid: The session ID of a client to skip when broadcasting
                         to a room or to all clients. This can be used to
                         prevent a message from being sent to the sender.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the event is emitted to the
                          default namespace.
        :param callback: If given, this function will be called to acknowledge
                         the the client has received the message. The arguments
                         that will be passed to the function are those provided
                         by the client. Callback functions can only be used
                         when addressing an individual client.
        :param ignore_queue: Only used when a message queue is configured. If
                             set to ``True``, the event is emitted to the
                             clients directly, without going through the queue.
                             This is more efficient, but only works when a
                             single server process is used. It is recommended
                             to always leave this parameter with its default
                             value of ``False``.

        Note: this method is a coroutine.
        """
        await self.emit('message', data, room, skip_sid, namespace, callback,
                        **kwargs)

    async def close_room(self, room, namespace=None):
        """Close a room.

        This function removes all the clients from the given room.

        :param room: Room name.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the default namespace is used.

        Note: this method is a coroutine.
        """
        namespace = namespace or '/'
        self.logger.info('room %s is closing [%s]', room, namespace)
        await self.manager.close_room(room, namespace)

    async def disconnect(self, sid, namespace=None):
        """Disconnect a client.

        :param sid: Session ID of the client.
        :param namespace: The Socket.IO namespace to disconnect. If this
                          argument is omitted the default namespace is used.

        Note: this method is a coroutine.
        """
        namespace = namespace or '/'
        if self.manager.is_connected(sid, namespace=namespace):
            self.logger.info('Disconnecting %s [%s]', sid, namespace)
            self.manager.pre_disconnect(sid, namespace=namespace)
            await self._send_packet(sid, packet.Packet(packet.DISCONNECT,
                                                       namespace=namespace))
            await self._trigger_event('disconnect', namespace, sid)
            self.manager.disconnect(sid, namespace=namespace)

    async def handle_request(self, *args, **kwargs):
        """Handle an HTTP request from the client.

        This is the entry point of the Socket.IO application. This function
        returns the HTTP response body to deliver to the client.

        Note: this method is a coroutine.
        """
        return await self.eio.handle_request(*args, **kwargs)

    def start_background_task(self, target, *args, **kwargs):
        """Start a background task using the appropriate async model.

        This is a utility function that applications can use to start a
        background task using the method that is compatible with the
        selected async mode.

        :param target: the target function to execute. Must be a coroutine.
        :param args: arguments to pass to the function.
        :param kwargs: keyword arguments to pass to the function.

        The return value is a ``asyncio.Task`` object.

        Note: this method is a coroutine.
        """
        return self.eio.start_background_task(target, *args, **kwargs)

    async def sleep(self, seconds=0):
        """Sleep for the requested amount of time using the appropriate async
        model.

        This is a utility function that applications can use to put a task to
        sleep without having to worry about using the correct call for the
        selected async mode.

        Note: this method is a coroutine.
        """
        return await self.eio.sleep(seconds)

    async def _emit_internal(self, sid, event, data, namespace=None, id=None):
        """Send a message to a client."""
        # tuples are expanded to multiple arguments, everything else is sent
        # as a single argument
        if isinstance(data, tuple):
            data = list(data)
        else:
            data = [data]
        await self._send_packet(sid, packet.Packet(
            packet.EVENT, namespace=namespace, data=[event] + data, id=id,
            binary=None))

    async def _send_packet(self, sid, pkt):
        """Send a Socket.IO packet to a client."""
        encoded_packet = pkt.encode()
        if isinstance(encoded_packet, list):
            binary = False
            for ep in encoded_packet:
                await self.eio.send(sid, ep, binary=binary)
                binary = True
        else:
            await self.eio.send(sid, encoded_packet, binary=False)

    async def _handle_connect(self, sid, namespace):
        """Handle a client connection request."""
        namespace = namespace or '/'
        self.manager.connect(sid, namespace)
        if await self._trigger_event('connect', namespace, sid,
                                     self.environ[sid]) is False:
            self.manager.disconnect(sid, namespace)
            await self._send_packet(sid, packet.Packet(packet.ERROR,
                                                       namespace=namespace))
            return False
        else:
            await self._send_packet(sid, packet.Packet(packet.CONNECT,
                                                       namespace=namespace))

    async def _handle_disconnect(self, sid, namespace):
        """Handle a client disconnect."""
        namespace = namespace or '/'
        if namespace == '/':
            namespace_list = list(self.manager.get_namespaces())
        else:
            namespace_list = [namespace]
        for n in namespace_list:
            if n != '/' and self.manager.is_connected(sid, n):
                await self._trigger_event('disconnect', n, sid)
                self.manager.disconnect(sid, n)
        if namespace == '/' and self.manager.is_connected(sid, namespace):
            await self._trigger_event('disconnect', '/', sid)
            self.manager.disconnect(sid, '/')
            if sid in self.environ:
                del self.environ[sid]

    async def _handle_event(self, sid, namespace, id, data):
        """Handle an incoming client event."""
        namespace = namespace or '/'
        self.logger.info('received event "%s" from %s [%s]', data[0], sid,
                         namespace)
        if self.async_handlers:
            self.start_background_task(self._handle_event_internal, self, sid,
                                       data, namespace, id)
        else:
            await self._handle_event_internal(self, sid, data, namespace, id)

    async def _handle_event_internal(self, server, sid, data, namespace, id):
        r = await server._trigger_event(data[0], namespace, sid, *data[1:])
        if id is not None:
            # send ACK packet with the response returned by the handler
            # tuples are expanded as multiple arguments
            if r is None:
                data = []
            elif isinstance(r, tuple):
                data = list(r)
            else:
                data = [r]
            await server._send_packet(sid, packet.Packet(packet.ACK,
                                                         namespace=namespace,
                                                         id=id, data=data,
                                                         binary=None))

    async def _handle_ack(self, sid, namespace, id, data):
        """Handle ACK packets from the client."""
        namespace = namespace or '/'
        self.logger.info('received ack from %s [%s]', sid, namespace)
        await self.manager.trigger_callback(sid, namespace, id, data)

    async def _trigger_event(self, event, namespace, *args):
        """Invoke an application event handler."""
        # first see if we have an explicit handler for the event
        if namespace in self.handlers and event in self.handlers[namespace]:
            if asyncio.iscoroutinefunction(self.handlers[namespace][event]) \
                    is True:
                try:
                    ret = await self.handlers[namespace][event](*args)
                except asyncio.CancelledError:  # pragma: no cover
                    ret = None
            else:
                ret = self.handlers[namespace][event](*args)
            return ret

        # or else, forward the event to a namepsace handler if one exists
        elif namespace in self.namespace_handlers:
            return await self.namespace_handlers[namespace].trigger_event(
                event, *args)

    async def _handle_eio_connect(self, sid, environ):
        """Handle the Engine.IO connection event."""
        if not self.manager_initialized:
            self.manager_initialized = True
            self.manager.initialize()
        self.environ[sid] = environ
        return await self._handle_connect(sid, '/')

    async def _handle_eio_message(self, sid, data):
        """Dispatch Engine.IO messages."""
        if sid in self._binary_packet:
            pkt = self._binary_packet[sid]
            if pkt.add_attachment(data):
                del self._binary_packet[sid]
                if pkt.packet_type == packet.BINARY_EVENT:
                    await self._handle_event(sid, pkt.namespace, pkt.id,
                                             pkt.data)
                else:
                    await self._handle_ack(sid, pkt.namespace, pkt.id,
                                           pkt.data)
        else:
            pkt = packet.Packet(encoded_packet=data)
            if pkt.packet_type == packet.CONNECT:
                await self._handle_connect(sid, pkt.namespace)
            elif pkt.packet_type == packet.DISCONNECT:
                await self._handle_disconnect(sid, pkt.namespace)
            elif pkt.packet_type == packet.EVENT:
                await self._handle_event(sid, pkt.namespace, pkt.id, pkt.data)
            elif pkt.packet_type == packet.ACK:
                await self._handle_ack(sid, pkt.namespace, pkt.id, pkt.data)
            elif pkt.packet_type == packet.BINARY_EVENT or \
                    pkt.packet_type == packet.BINARY_ACK:
                self._binary_packet[sid] = pkt
            elif pkt.packet_type == packet.ERROR:
                raise ValueError('Unexpected ERROR packet.')
            else:
                raise ValueError('Unknown packet type.')

    async def _handle_eio_disconnect(self, sid):
        """Handle Engine.IO disconnect event."""
        await self._handle_disconnect(sid, '/')

    def _engineio_server_class(self):
        return engineio.AsyncServer
