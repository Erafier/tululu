#!/usr/bin/python
# -*- coding: UTF-8 -*-

from urllib.parse import urljoin
import requests
import os
import json
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import argparse

parser = argparse.ArgumentParser(
    prog="tululu",
    description="Программа для скачивания научно-фантастических книг с сайта tululu.org",
    epilog="Сделано Максимом для любимого дедушки"
)
parser.add_argument('--start_page', help='С какой страницы начинать скачивать книги', type=int)
parser.add_argument('--end_page', help='На какой странице остановить скачивание книг', type=int, default=701)
args = parser.parse_args()

urls = []
pages = range(args.start_page, args.end_page + 1)
for page in pages:
    url = 'http://tululu.org/l55/' + str(page)
    responce = requests.get(url)
    soup = BeautifulSoup(responce.text, 'lxml')
    books = soup.select('table.d_book')
    for book in books:
        source = book.select_one('a')['href']
        urls.append(urljoin('http://tululu.org/', source))


def download_txt_with_title(book_id, folder='books/'):
    download_url = 'http://tululu.org/txt.php?id=' + str(book_id)
    title_url = 'http://tululu.org/b' + str(book_id)
    print(title_url)
    if not os.path.exists(folder):
        os.mkdir(folder)
    responce = requests.get(download_url, allow_redirects=False)
    if responce.status_code == 302:
        return
    title_responce = requests.get(title_url)
    soup = BeautifulSoup(title_responce.text, 'lxml')
    header = soup.select_one('h1').text
    title = header.split("::")[0].strip()
    filename = sanitize_filename(title)
    path = os.path.join(folder, filename + '.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(responce.text)


def download_img(book_id, folder='images/'):
    title_url = 'http://tululu.org/b' + str(book_id)
    if not os.path.exists(folder):
        os.mkdir(folder)
    title_responce = requests.get(title_url)
    soup = BeautifulSoup(title_responce.text, 'lxml')
    img_url = soup.select_one('.bookimage img')['src']
    full_img_url = urljoin('http://tululu.org/', img_url)
    img_response = requests.get(full_img_url)
    img_filename = sanitize_filename(os.path.basename(full_img_url))
    path = os.path.join(folder, img_filename)
    with open(path, 'wb') as f:
        f.write(img_response.content)


descriptions = []
for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    book_id = url.split('/')[-2][1:]
    comments = []
    comment_divs = soup.select('div.texts span')
    for divs in comment_divs:
        comments.append(divs.text)
    genres = []
    genres_span = soup.select('span.d_book a')
    for genre in genres_span:
        genres.append(genre.text)
    download_txt_with_title(book_id)
    download_img(book_id)
    header = soup.select_one('h1').text
    title = header.split("::")[0].strip()
    author = header.split("::")[1].strip()
    img_url = soup.select_one('.bookimage img')['src']
    img_src = os.path.join('images', sanitize_filename(os.path.basename(img_url)))
    book_src = os.path.join('books', title + '.txt')
    description = {
        "title": title,
        "author": author,
        "img_src": img_src,
        "book_path": book_src,
        "comments": comments,
        "genres": genres
    }
    descriptions.append(description)

with open('description.json', 'w', encoding='utf-8') as f:
    json.dump(descriptions, f, ensure_ascii=False)
print('Скачивание завершено, приятного чтения, дедушка!')
