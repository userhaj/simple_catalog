import bs4 as bs
import urllib.request


class ImdbGet(object):

    def __init__(self, site_url):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

        try:
            site_request = urllib.request.Request(site_url, data=None, headers=headers)
            site_source = urllib.request.urlopen(site_request)
            self.site_soup = bs.BeautifulSoup(site_source, 'html.parser')
        except:
            pass


        # Set by get_details
        self.release_date = None
        self.language = None
        self.title = None
        self.rating = None
        self.description = None
        try:
            self.get_details()
            self.description = self.get_description()
            self.rating = self.get_rating()
        except:
            pass

    def __str__(self):
        return 'Title: {}\nRating: {}\nRelease: {}\nDescription: {}'.format(self.title, self.rating, self.release_date, self.description)

    def get_description(self):
        try:
            description = self.site_soup.findAll(itemprop="description")[1].get_text().strip('\n')
        except:
            description = None
        return description

    def get_rating(self):
        try:
            rating = self.site_soup.findAll(itemprop="contentRating")[1].get_text()
        except:
            rating = None

        return rating

    def get_details(self):
        try:
            self.release_date = self.site_soup.find('h4', text='Release Date:').next_sibling.strip('\n').replace('\n', '')
        except:
            pass
        try:
            self.language = self.site_soup.find('h4', text='Language:').next_element.next_element.next_element.get_text()
        except:
            pass
        try:
            self.title = self.site_soup.find(itemprop="name").get_text()
        except:
            pass


def imdb_get_movie_url(title_name):
    """Get url of movie title
    Attributes:
        title_name (str): title of movie"""
    search_term = str(title_name.replace(' ', '+').encode('utf-8').strip())
    # Use 1st google result because imdb search is terrible
    site_url = ''.join(['https://www.google.com/search?q=imdb+', search_term])
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}
    site_request = urllib.request.Request(site_url, data=None, headers=headers)
    site_source = urllib.request.urlopen(site_request)
    site_soup = bs.BeautifulSoup(site_source, 'html.parser')

    return site_soup.find('cite').text


if __name__ == '__main__':
    movie = 'A great movie name'
    imdb_url = imdb_get_movie_url(movie)
    Imdb = ImdbGet(imdb_url)
    print(Imdb)




