#!/usr/bin/python
from urllib.parse import urljoin
import requests
import os
import json
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import argparse


def download_txt_with_title(book_id, folder='books'):
    download_url = 'http://tululu.org/txt.php?id=' + str(book_id)
    title_url = 'http://tululu.org/b' + str(book_id)
    print(title_url)
    os.makedirs(folder, exist_ok=True)
    response = requests.get(download_url, allow_redirects=False)
    if response.status_code == 302:
        return
    title_response = requests.get(title_url)
    soup = BeautifulSoup(title_response.text, 'lxml')
    header = soup.select_one('h1').text
    title = header.split("::")[0].strip()
    filename = sanitize_filename(title)
    path = os.path.join(folder, filename + '.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(response.text)


def download_img(book_id, folder='images'):
    title_url = 'http://tululu.org/b' + str(book_id)
    os.makedirs(folder, exist_ok=True)
    title_response = requests.get(title_url)
    soup = BeautifulSoup(title_response.text, 'lxml')
    img_url = soup.select_one('.bookimage img')['src']
    full_img_url = urljoin('http://tululu.org/', img_url)
    img_response = requests.get(full_img_url)
    img_filename = sanitize_filename(os.path.basename(full_img_url))
    path = os.path.join(folder, img_filename)
    with open(path, 'wb') as f:
        f.write(img_response.content)


def parse_genres(soup):
    genres_span = soup.select('span.d_book a')
    genres = [genre.text for genre in genres_span]
    return genres


def parse_comments(soup):
    comment_divs = soup.select('div.texts span')
    comments = [div.text for div in comment_divs]
    return comments


def parse_title_and_author(soup):
    header = soup.select_one('h1').text
    title = header.split("::")[0].strip()
    author = header.split("::")[1].strip()
    return title, author


def make_request(url):
    response = requests.get(url)
    json_data = response.json()
    if 'error' in json_data:
        raise requests.exceptions.HTTPError(json_data['error'])
    return response


def main(start_page, end_page):
    urls = []
    pages = range(start_page, end_page + 1)
    for page in pages:
        url = 'http://tululu.org/l55/' + str(page)
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'lxml')
        books = soup.select('table.d_book')
        for book in books:
            source = book.select_one('a')['href']
            urls.append(urljoin('http://tululu.org/', source))

    descriptions = []
    for url in urls:
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'lxml')
        book_id = url.split('/')[-2][1:]
        comments = parse_comments(soup)
        genres = parse_genres(soup)
        title, author = parse_title_and_author(soup)
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
        download_txt_with_title(book_id)
        download_img(book_id)

    with open('description.json', 'w', encoding='utf-8') as f:
        json.dump(descriptions, f, ensure_ascii=False)
    print('Скачивание завершено, приятного чтения, дедушка!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="tululu",
        description="Программа для скачивания научно-фантастических книг с сайта tululu.org",
        epilog="Сделано Максимом для любимого дедушки"
    )
    parser.add_argument('--start_page', help='С какой страницы начинать скачивать книги', type=int)
    parser.add_argument('--end_page', help='На какой странице остановить скачивание книг', type=int, default=701)
    args = parser.parse_args()
    main(args.start_page, args.end_page)
