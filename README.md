# Парсер книг с сайта tululu.org

Программа позволяет скачивать книги научно-фантастического
жанра с обложками и описанием с сайта tululu.org

Описания книг записываются в файл `description.json`  
Обложки книг записываются в папку `image`  
Сами книги записываются в папку `book`

### Как установить

Для запуска скрипта необходим Python3.х версии 
и библиотеки:
* urlib3
* BeautifulSoup
* pathvalidate 
* requests

### Аргументы

Программа имеет два аргумента:
1. `--start_page` - обязательный аргумент, определяет, с какой страницы начинать скачивание книг
2. `--end_page` - необязательный аргумент, определяет, до какой страницы будут скачиваться книги. По умолчанию равен последней странице каталога.


### Цель проекта

Код написан в образовательных целях Максимки для дедушки на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
