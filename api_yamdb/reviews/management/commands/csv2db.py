import csv
import logging
import os

from django.conf import settings
from django.core.management import BaseCommand
from django.db import IntegrityError

from reviews.models import (
    Categories,
    Comment,
    Genres,
    TitlesGenres,
    Review,
    Titles,
    User
)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s, %(pathname)s'
)

FILES_CLASSES = {
    'category': Categories,
    'genre': Genres,
    'titles': Titles,
    'genre_title': TitlesGenres,
    'users': User,
    'review': Review,
    'comments': Comment,
}

FIELDS = {
    'category': ('category', Categories),
    'title_id': ('title', Titles),
    'genre_id': ('genre', Genres),
    'author': ('author', User),
    'review_id': ('review', Review),
}


def open_csv_file(file_name):
    """Function for opening the csv files,
    takes directory parameter from settings."""
    csv_file = file_name + '.csv'
    csv_path = os.path.join(settings.DIR_FOR_CSV, csv_file)
    try:
        with (open(csv_path, encoding='utf-8')) as file:
            return list(csv.reader(file))
    except FileNotFoundError:
        logging.error(f'Файл {csv_file} не найден.')
        return


def change_foreign_values(data_csv):
    """Make a set of data correctly sorted with its fields"""
    data_csv_copy = data_csv.copy()
    for field_key, field_value in data_csv.items():
        if field_key in FIELDS.keys():
            field_key0 = FIELDS[field_key][0]
            data_csv_copy[field_key0] = FIELDS[field_key][1].objects.get(
                pk=field_value)
    return data_csv_copy


def load_csv(file_name, class_name):
    """Main function"""
    table_not_loaded = f'Таблица {class_name.__qualname__} не загружена.'
    table_loaded = f'Таблица {class_name.__qualname__} загружена.'
    data = open_csv_file(file_name)
    rows = data[1:]
    for row in rows:
        data_csv = dict(zip(data[0], row))
        data_csv = change_foreign_values(data_csv)
        try:
            table = class_name(**data_csv)
            table.save()
        except (ValueError, IntegrityError) as error:
            logging.error(f'Ошибка в загружаемых данных. {error}. '
                          f'{table_not_loaded}')
            break
    logging.info(table_loaded)


class Command(BaseCommand):

    def handle(self, *args, **options):
        for key, value in FILES_CLASSES.items():
            logging.info(f'Загрузка таблицы {value.__qualname__}')
            load_csv(key, value)
