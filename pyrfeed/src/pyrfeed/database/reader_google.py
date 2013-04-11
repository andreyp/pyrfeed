import re
from private import login_info
from ReaderDatabase import ReaderDatabase
from GoogleReader import GoogleReader

class Reader(object) :
    def __init__(self,login,passwd) :
        self._googlereader = GoogleReader()
        self._googlereader.identify(login=login,passwd=passwd)
        if not(self._googlereader.login()) :
            raise "Can't login"
        self._database = ReaderDatabase('reader.sqlite3')
    def synchro(self) :
        xmlfeed = self._googlereader.get_feed(n=200)
        self._database.start_add_session()
        for entry in xmlfeed.get_entries() :
            self._database.add_item(
                google_id=entry['google_id'].encode('utf-8'),
                original_id=entry['original_id'].encode('utf-8'),
                link=entry['link'].encode('utf-8'),
                content=entry['content'].encode('utf-8'),
                title=entry['title'].encode('utf-8'),
                author=entry['author'].encode('utf-8'),
                published=entry['published'],
                updated=entry['updated'],
                crawled=entry['crawled'],
                )
            for term in entry['categories'] :
                label = entry['categories'][term]
                self._database.add_item_categorie(
                    google_id=entry['google_id'].encode('utf-8'),
                    categorie_name=term.encode('utf-8'),
                    categorie_shortname=label.encode('utf-8'),
                    )
        self._database.stop_add_session()
def test() :
    rd=Reader(**login_info)
    rd.synchro()

if __name__ == '__main__' :
    test()




