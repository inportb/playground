TBCrypt
=======

Summary
-------

A module that RSA encrypts tracebacks (to no real useful end).
Requires PyCrypto.

Usage
-----

```python
include tbcrypt
```

Notes
-----

The included tool `traceback_decoder` decodes the encrypted tracebacks
as long as the correct key is given. Try it out on the included
`example_traceback` traceback generated from (the also included)
`test.py`.