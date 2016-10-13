from html.parser import HTMLParser


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.the_link = ''
        self.site = ''

    def handle_starttag(self, tag, attrs):
        if (tag == 'a'):
            for attr in attrs:
                if attr[0] == 'href':
                    link = attr[1]
                    if link.find('soundcloud') != -1:
                        self.the_link = link
                        self.site = 'soundcloud'
                    if link.find('youtube') != -1:
                        self.the_link = link
                        self.site = 'youtube'
