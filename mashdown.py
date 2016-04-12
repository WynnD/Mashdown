from __future__ import unicode_literals
from html.parser import HTMLParser
import httplib2
import feedparser
import youtube_dl
import subprocess


##  Features to add:
##      -support for more sites:
##          -soundcloud support
##          -vimeo support
##      -confirmation dialog that lists all links to be downloaded
##      -abstraction (so this may be used on more subreddits, etc.

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
        self.abs_path = 'D:\\Music\\mashdown\\'

    
    def main(self):

        # get list of entries
        httplib = httplib2.Http(".cache")
        (resp_headers, rss_content) = httplib.request("http://reddit.com/r/mashups/hot/.rss", "GET")
        if resp_headers['status'] != '200':
            return
        feed = feedparser.parse(rss_content)
        entries = feed['entries']

        # parse the links given to us into a dictionary list dict{title, author, url, site}
        self.links = self.parselinks(entries)
        self.links = self.prettify_titles(self.links)

        # remove any links that have not been downloaded, and upload downloaded.txt with new links
        self.links = self.check_downloaded(self.links)


        
        if (self.confirm(self.links)):
            self.download(self.links)        
            # self.links = self.HTTPS_HTTP(self.links) # if we needed to convert our links into HTTP from HTTPS



    def parselinks(self, rss):
        # returns list of links [title, author, link, site]
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
                    links.append({'title':title, 'author':author, 'url': link, 'site': site})
                h.close()

        return links


    def prettify_titles(self,links):
        for link in links:
            title = link['title']
            
            fragments = title.split('[')
            link['title'] = fragments[0]


        return links

    def HTTPS_HTTP(self,links):
        for link in links:
            url = link['url']
            
            new_url = url.replace('https','http')
            link['url'] = new_url
        return links

    def download(self, links):
##        ydl_opts = {
##            'format': 'bestaudio/best',
##            'postprocessors': [{
##                'key': 'FFmpegExtractAudio',
##                'preferredcodec': 'm4a',
##                'preferredquality': '256'
##                }],
##            'nocheckcertificate':'1'
##            ##'--metadata-from-title':'%(artist)s - %(title)s' 
##
##            }
        for link in links:
            title = link['title']
            url = link['url']
            if (link['site'] == 'youtube'):

                subprocess.call(["youtube-dl", "--no-check-certificate", "-x",
                                 "--audio-format", "m4a", "--audio-quality", "256",
                                 "--embed-thumbnail",
                                 "--add-metadata",
                                 "-o", (self.abs_path + title + '.m4a'),
                                 url])
##                ydl_opts['outtmpl'] = self.abs_path + title
##                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
##                    ydl.download([url])
        
    def confirm(self, links):
        for link in links:
            if link['site'] == 'youtube':
                print(link['title'], link['url'])
        x = input("Download videos? (y/n): ")
        return (x.lower() == 'y')

    def check_downloaded(self, links):
        good_links = []
        ret = []
        
        x = open('downloaded.txt','w+')
        urls = x.readlines()
        for i in range(0, len(links)):
            if links[i]['url'] not in urls:
                ret.append(links[i])
                good_links.append(links[i]['url'])
        to_write = "\n".join(good_links)
        x.write(to_write)
        return ret
        
if __name__ == "__main__":
    x = Mashdown()
    x.main()
