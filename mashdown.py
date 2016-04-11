from __future__ import unicode_literals
from html.parser import HTMLParser
import httplib2
import feedparser
import youtube_dl


class MyHTMLParser(HTMLParser):
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


class Mashdown:
    def __init__(self):
        self.links = []
        self.abs_path = 'D:\\Music\\smashdown\\'

    
    def main(self):
        httplib = httplib2.Http(".cache")
        (resp_headers, rss_content) = httplib.request("http://reddit.com/r/mashups/hot/.rss", "GET")
        feed = feedparser.parse(rss_content)
        entries = feed['entries']
        self.links = self.parselinks(entries)
        self.links = self.prettify_titles(self.links)
        ##self.links = self.HTTPS_HTTP(self.links)
        self.download(self.links)        

    def parselinks(self, rss):
        links = []
        for link in rss:
            author = link['author']
            if author != '/u/AutoModerator':
                ## do things to links 
                title = link['title']
                content = link['content'][0]['value']
                h = MyHTMLParser()
                h.feed(content)
                link = h.the_link
                site = h.site
                if link != '':
                    links.append([title, author, link, site])
                h.close()

        return links


    def prettify_titles(self,links):
        for link in links:
            title = link[0]
            
            fragments = title.split(' -')
            link[0] = fragments[0]


        return links

    def HTTPS_HTTP(self,links):
        for link in links:
            url = link[3]
            
            url = url.replace('https','http')
            link[3] = url
        return links

    def download(self, links):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'aac',
                'preferredquality': '256',
            }],
            'nocheckcertificate':'1'
            }
        for link in links:
            title = link[0]
            url = link[2]
            if (link[3] == 'youtube'):
                ydl_opts['outtmpl'] = self.abs_path + title + '.m4a'
                
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
        

if __name__ == "__main__":
    x = Mashdown()
    x.main()
