Gedit Plugins
=============

These plugins are not mine, but I've improved on them.

For csmartindent, I added smart indentation support for PHP and JavaScript,
which could also benifit from { auto indent.. etc.

For pythonindentation, I added support for enforcing the spaces only rule for
Python. I also fixed a bug where if you have ``returnSomething`` as a variable
and at a line start, and if you press enter, it would auto dedent. Now it checks
if the ``return``, ``raise``, ``continue``, ``pass``, and ``break`` is on its 
own, which would make it a statement.

Install, put it under ~/.gnome2/gedit/plugins (?)
IDK about windows, I don't have it as of the moment, I will find out later,
though.
