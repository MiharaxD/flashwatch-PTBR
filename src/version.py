"""The application's version.

A single line stamped before packaging, also advanced by the release workflow.
The updater compares this number with GitHub to avoid downloading the same or
an older build. Source checkouts display the number but never replace themselves.

Kept in its own module so stamping it cannot disturb anything else, and so the
value is importable without pulling in Qt.
"""

__version__ = "1.0.2"
