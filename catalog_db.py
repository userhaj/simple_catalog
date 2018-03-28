import sqlite3
import re
import imdbget
import os.path


class DbManage:
    def __init__(self):

        self.db_connection = sqlite3.connect('catalog.db', check_same_thread=False)
        self.db_connection.execute('''CREATE TABLE IF NOT EXISTS catalog (file text, title_guess text, title text, description text, 
                                            rating text, release text)''')

        self.db_cursor = self.db_connection.cursor()

    def add_file(self, file_path):
        if os.path.isdir(file_path):
            return
        drive, path = os.path.splitdrive(file_path)
        path, filename = os.path.split(path)
        if filename == '':
            return

        guessed_title = self.title_guess(file_path)

        self.db_cursor.execute('SELECT * FROM catalog WHERE catalog.title_guess = ?', (guessed_title,))

        if self.db_cursor.fetchone() is None:
            self.db_connection.execute(
                'INSERT INTO catalog(file,title_guess) VALUES("{}","{}")'.format(file_path, guessed_title))
            self.db_connection.commit()

    def update_all_details(self):
        self.db_cursor.execute('SELECT title_guess FROM catalog WHERE catalog.description is null')
        failures = 0

        titles_wo_description = self.db_cursor.fetchall()
        for guessed_title in titles_wo_description:
            guessed_title = guessed_title[0]  # Fetch all returns with title in a tuple. Remove tuple.
            print('Getting details for {}'.format(guessed_title))
            imdb = imdbget.ImdbGet(imdbget.imdb_get_movie_url(guessed_title))
            print('Adding {} to library as {}'.format(guessed_title, imdb.title))
            try:
                self.db_connection.execute(
                    'UPDATE catalog SET description = "{}" WHERE catalog.title_guess = "{}"'.format(imdb.description,
                                                                                                    guessed_title))
                self.db_connection.execute(
                    'UPDATE catalog SET rating = "{}" WHERE catalog.title_guess = "{}"'.format(imdb.rating,
                                                                                               guessed_title))
                self.db_connection.execute(
                    'UPDATE catalog SET release = "{}" WHERE catalog.title_guess = "{}"'.format(imdb.release_date,
                                                                                                guessed_title))
                self.db_connection.execute(
                    'UPDATE catalog SET title = "{}" WHERE catalog.title_guess = "{}"'.format(imdb.title,
                                                                                              guessed_title))
                self.db_connection.commit()
            except:  # Failure may occur for many reasons.
                failures += 1
                if failures > 5:  # Avoid spamming services if you are failing
                    break

    def title_guess(self, file_path):

        search_regex = re.compile(r'(^.*\\)(\[*.*?)(.*?\])*([(]*.*?[)]*)(.*)?(\[*.*?)(.*?\])*([(]*.*?[)]*)')
        title_without_junk = search_regex.search(file_path).group(5)[:-4]
        try:
            # Remove everything after a 3 digit number, error if 3 digit number doesn't exist
            title_without_junk = re.search(r'((^.)(.*?))(?:\d\d\d)', title_without_junk).group(1)
        except:
            pass

        return title_without_junk

    def get_description(self, title):
        self.db_cursor.execute('SELECT description FROM catalog WHERE title_guess = ?', (title,))
        return self.db_cursor.fetchone()[0]

    def get_title(self, title):
        self.db_cursor.execute('SELECT title FROM catalog WHERE title_guess = ?', (title,))
        return self.db_cursor.fetchone()[0]

    def get_rating(self, title):
        self.db_cursor.execute('SELECT rating FROM catalog WHERE title_guess = ?', (title,))
        return self.db_cursor.fetchone()[0]

    def get_release_date(self, title):
        self.db_cursor.execute('SELECT release FROM catalog WHERE title_guess = ?', (title,))
        return self.db_cursor.fetchone()[0]

    def get_file(self, title):
        self.db_cursor.execute('SELECT file FROM catalog WHERE title_guess = ?', (title,))
        return self.db_cursor.fetchone()[0]

    def get_all_title_guess(self):
        self.db_cursor.execute('SELECT title_guess FROM catalog')
        return self.db_cursor.fetchall()

    def delete_file(self, title):
        self.db_connection.execute('DELETE FROM catalog WHERE file = ?', (title,))


def title_guess(file_path):

    search_regex = re.compile(r'(^.*\\)(\[*.*?)(.*?\])*([(]*.*?[)]*)(.*)?(\[*.*?)(.*?\])*([(]*.*?[)]*)')
    title_without_junk = search_regex.search(file_path).group(5)[:-4]
    try:
        # Remove everything after a 3 digit number, error if 3 digit number doesn't exist
        title_without_junk = re.search(r'((^.)(.*?))(?:\d\d\d)', title_without_junk).group(1)
    except:
        pass

    return title_without_junk
