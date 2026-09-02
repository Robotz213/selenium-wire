import urllib
import urllib.parse

from seleniumwire.thirdparty.mitmproxy.contentviews._api import Contentview, Metadata

from ._utils import byte_pairs_to_str_pairs, merge_repeated_keys, yaml_dumps


class URLEncodedContentview(Contentview):
    name = "URL-encoded"
    syntax_highlight = "yaml"

    def prettify(
        self,
        data: bytes,
        metadata: Metadata,
    ) -> str:
        items = urllib.parse.parse_qsl(data, keep_blank_values=True)
        return yaml_dumps(merge_repeated_keys(byte_pairs_to_str_pairs(items)))

    def render_priority(
        self,
        data: bytes,
        metadata: Metadata,
    ) -> float:
        return float(
            bool(data) and metadata.content_type == "application/x-www-form-urlencoded"
        )


urlencoded = URLEncodedContentview()
