from idiokit import threado, util
from abusehelper.core import utils, cymru, bot, events

class MDLBot(bot.PollingBot):
    use_cymru_whois = bot.BoolParam(default=False)

    def augment(self):
        if not self.use_cymru_whois:
            return bot.PollingBot.augment(self)
        return cymru.CymruWhois() | self.printer()

    @threado.stream
    def printer(inner,self):
        i = 0
        while True:
            event = yield inner
            print i, event
            new = events.Event()
            new.update('ip',event.values('ip'))
            new.update('cc',event.values('cc'))
            new.update('asn', event.values('asn'))
            new.update('as name', event.values('as name'))
            inner.send(new)
            i += 1
    @threado.stream
    def poll(inner, self, url="http://www.malwaredomainlist.com/hostslist/ip.txt"):
        url="http://www.malwaredomainlist.com/hostslist/ip.txt"

        self.log.info("Downloading MDL IP-list")
        try:
            info, fileobj = yield inner.sub(utils.fetch_url(url))
        except utils.FetchUrlFailed, fuf:
            self.log.error("MDL IP-list downloading failed: %r", fuf)
            return
        except:
            import pdb;pdb.set_trace()
        self.log.info("MDL IP-list downloaded")

        charset = info.get_param("charset")

	if charset is None:
		decode = util.guess_encoding
	else:
        	decode = lambda x: x.decode(charset)

        i = 0
        for line in fileobj:
            event = events.Event()
            ip = decode(line.strip())
            event.add("ip", ip)
            inner.send(event)
            i += 1

if __name__ == "__main__":
    MDLBot.from_command_line().execute()