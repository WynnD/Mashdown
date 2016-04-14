from __future__ import unicode_literals
from html.parser import HTMLParser
import httplib2
import feedparser
import youtube_dl
import subprocess
import re


##  Features to add:
##      -support for more sites:
##          -soundcloud support
##          -vimeo support
##      -abstraction (so this may be used on more subreddits, etc.)




class Mashdown:




    def __init__(self):
        self.links = []
        self.abs_path = 'D:\\Music\\mashdown\\'

    
    def main(self):

        # get list of entries
        httplib = httplib2.Http(".cache")

        print("Welcome to Mashdown! Enter q at any time to quit.\n")

        subreddit = clean_subreddit(input("What subreddit would you like me to scan?"))
        if subreddit == 'q': #check if user wants to quit
            print("Quitting program. Thanks for using Mashdown!")

        hnrct = prompt_hnrct() # choose what page you want to download in ['hot','new','rising','controversial','top']

        if hnrct == 'q': #check if user wants to quit
            print("Quitting program. Thanks for using Mashdown!")


        # make HTTP request
        (resp_headers, rss_content) = httplib.request("http://reddit.com/r/"+subreddit+"/"+hnrct+"/.rss", "GET")

        if resp_headers['status'] != '200':
            print("Reddit is not responding right now. Try again in a little bit.")
            return

        # parse rss feed into a workable list
        feed = feedparser.parse(rss_content)

        # save reddit posts (this removes and headers and other unneeded stuff)
        entries = feed['entries']

        # parse the links given to us into a dictionary list dict{title, author, url, site}
        self.links = self.parselinks(entries)

        # optional file name prettifier (doesn't work very well right now)
        # self.links = self.prettify_titles(self.links)

        # remove any links that have not been downloaded, and update downloaded.txt with new links
        self.links = self.check_downloaded(self.links)

        format_opts = self.get_opts()

        
        if (self.confirm(self.links)):
            self.download(self.links, format_opts)        
            

            # use this if we need to convert our links into HTTP from HTTPS (might not be useful )
            # self.links = self.HTTPS_HTTP(self.links) 

    def prompt_hnrct(self):
        choice = ''

        while choice not in ['hot','new','rising', 'controversial', 'top', 'q']:
            choice = input("Which page would you like? Type one of: 'hot', 'new', 'rising', 'controversial', 'top', OR type 'q' to quit")
            choice = choice.lower()

        return choice



    def parselinks(self, rss):
        # returns list of links [title, author, link, site]
        links = []
        for link in rss:
            author = link['author']
            if author != '/u/AutoModerator':
                ## do things to links 
                title = link['title']
                content = link['content'][0]['value']
                h = Mashdown.HTMLParser()
                h.feed(content)
                link = h.the_link
                site = h.site
                if link != '':
                    links.append({'title':title, 'author':author, 'url': link, 'site': site})
                h.close()

        return links

    def clean_subreddit(self, subreddit):
        subreddit = subreddit.re(r'/[rR]/', r'[/\]','')

        return subreddit


    def prettify_titles(self,links):

        for link in links:
            title = link['title']
            
            fragments = title.split(' [')
            link['title'] = fragments[0]
            
        return links


    def HTTPS_HTTP(self,links):
        # converts https links to http
        for link in links:
            url = link['url']
            
            new_url = url.replace('https','http')
            link['url'] = new_url
        return links


    def list_links(self,links):
        # lists links that can be downloaded by youtube-dl
        for link in links:
            if link['site'] == 'youtube':
                print(link['title'], link['url'])


    def confirm(self, links):
        # call list_links() then confirm that user wants to download listed links
        self.list_links(links)
        x = input("Download videos? (y/n): ")

        return (x.lower() == 'y')

    def get_opts(self):
        # get encoding options
        print("Formatting/encoding options:")

        ask_default = ''
        while ask_default.lower() not in ['y','n']:
            ask_default = input("Use default encoding options? (y/n): ")
            if (ask_default.lower() == 'n'):
                opts = manual_opts()

    return opts
    def manual_opts(self):
        audio_format = ''
        bitrate = 0
        while (audio_format not in ['mp3','m4a']) and (bitrate not in [128,256,320]):
            audio_format = input("Choose audio format ('mp3','m4a'): ").lower()
            bitrate = int(input("Choose bitrate (128,256,320): "))

        opts = {'format': audio_format, 'bitrate':bitrate}
        return opts



    def download(self, links, opts):
        # call youtube-dl with requested
        for link in links:
            title = link['title']
            url = link['url']
            if (link['site'] == 'youtube'):

                subprocess.call(["youtube-dl", "--no-check-certificate", "-x",
                                 "--audio-format", opts['format'], "--audio-quality", str(opts['bitrate']),
                                 "--embed-thumbnail",
                                 "--add-metadata",
                                 "-o", (self.abs_path + title + '.' + opts['format']),
                                 url])
       

    def check_downloaded(self, links):
        # checks if URLs have already been downloaded in the past
        good_links = []
        ret = []
        
        x = open('downloaded.txt','r+')
        urls = x.readlines()
        for i in range(0, len(links)):
            if (links[i]['url']+'\n') not in urls:
                ret.append(links[i])
                good_links.append(links[i]['url'])
        to_write = "\n".join(good_links)
        x.write(to_write)

        return ret
        

    class HTMLParser(HTMLParser):
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

if __name__ == "__main__":
    x = Mashdown()
    x.main()
