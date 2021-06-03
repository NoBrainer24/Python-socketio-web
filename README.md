python-socketio
===============

[![Build status](https://github.com/miguelgrinberg/python-socketio/workflows/build/badge.svg)](https://github.com/miguelgrinberg/python-socketio/actions) [![codecov](https://codecov.io/gh/miguelgrinberg/python-socketio/branch/main/graph/badge.svg)](https://codecov.io/gh/miguelgrinberg/python-socketio)

Python implementation of the `Socket.IO`_ realtime client and server.

Sponsors
--------

The following organizations are funding this project:

![Socket.IO](https://images.opencollective.com/socketio/050e5eb/logo/64.png)<br>[Socket.IO](https://socket.io)  | [Add your company here!](https://github.com/sponsors/miguelgrinberg)|
-|-

Many individual sponsors also support this project through small ongoing contributions. Why not [join them](https://github.com/sponsors/miguelgrinberg)?

Version compatibility
---------------------

The Socket.IO protocol has been through a number of revisions, and some of these
introduced backward incompatible changes, which means that the client and the
server must use compatible versions for everything to work.

If you are using the Python client and server, the easiest way to ensure compatibility
is to use the same version of this package for the client and the server. If you are
using this package with a different client or server, then you must ensure the
versions are compatible.

The version compatibility chart below maps versions of this package to versions
of the JavaScript reference implementation and the versions of the Socket.IO and
Engine.IO protocols.

JavaScript Socket.IO version | Socket.IO protocol revision | Engine.IO protocol revision | python-socketio version
-|-|-|-
0.9.x | 1, 2 | 1, 2 | Not supported
1.x and 2.x | 3, 4 | 3 | 4.x
3.x and 4.x | 5 | 4 | 5.x

Resources
---------

-  [Documentation](http://python-socketio.readthedocs.io/en/latest/)
-  [PyPI](https://pypi.python.org/pypi/python-socketio)
-  [Change Log](https://github.com/miguelgrinberg/python-socketio/blob/main/CHANGES.md)
-  Questions? See the [questions](https://stackoverflow.com/questions/tagged/python-socketio) others have asked on Stack Overflow, or [ask](https://stackoverflow.com/questions/ask?tags=python+python-socketio) your own question.
