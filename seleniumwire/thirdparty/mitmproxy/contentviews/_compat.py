from __future__ import annotations

import sys
import typing
from collections.abc import Iterator

from seleniumwire.thirdparty.mitmproxy import contentviews
from seleniumwire.thirdparty.mitmproxy.contentviews import SyntaxHighlight
from seleniumwire.thirdparty.mitmproxy.contentviews._api import Contentview, Metadata
from seleniumwire.thirdparty.mitmproxy.utils.strutils import always_str

if sys.version_info < (3, 13):  # pragma: no cover
    from typing_extensions import deprecated
else:
    from warnings import deprecated

if typing.TYPE_CHECKING:
    from seleniumwire.thirdparty.mitmproxy.contentviews.base import TViewLine, View


class LegacyContentview(Contentview):
    @property
    def name(self) -> str:
        return self.contentview.name

    @property
    def syntax_highlight(self) -> SyntaxHighlight:
        return getattr(self.contentview, "syntax_highlight", "none")

    def render_priority(
        self,
        data: bytes,
        metadata: Metadata,
    ) -> float:
        return (
            self.contentview.render_priority(
                data=data,
                content_type=metadata.content_type,
                flow=metadata.flow,
                http_message=metadata.http_message,
            )
            or 0.0
        )

    def prettify(self, data: bytes, metadata: Metadata) -> str:
        lines: Iterator[TViewLine]
        desc_, lines = self.contentview(
            data,
            content_type=metadata.content_type,
            flow=metadata.flow,
            http_message=metadata.http_message,
        )
        return "\n".join(
            "".join(always_str(text, "utf8", "backslashescape") for tag, text in line)
            for line in lines
        )

    def __init__(self, contentview: View):
        self.contentview = contentview


@deprecated("Use `mitmproxy.contentviews.registry` instead.")
def get(name: str) -> Contentview | None:
    try:
        return contentviews.registry[name.lower()]
    except KeyError:
        return None


@deprecated("Use `mitmproxy.contentviews.Contentview` instead.")
def remove(view: View):
    pass
