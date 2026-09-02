from seleniumwire.thirdparty.mitmproxy import addons, master, options
from seleniumwire.thirdparty.mitmproxy.addons import (
    dumper,
    errorcheck,
    keepserving,
    readfile,
)


class DumpMaster(master.Master):
    def __init__(
        self,
        options: options.Options,
        loop=None,
        with_termlog=True,
        with_dumper=True,
    ) -> None:
        super().__init__(options, event_loop=loop, with_termlog=with_termlog)
        self.addons.add(*addons.default_addons())
        if with_dumper:
            self.addons.add(dumper.Dumper())
        self.addons.add(
            keepserving.KeepServing(),
            readfile.ReadFileStdin(),
            errorcheck.ErrorCheck(),
        )
