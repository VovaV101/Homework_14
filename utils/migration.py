import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hw10.settings")

django.setup()

from quotes.models import Quote, Tag, Author  # noqa
from quotes.utils import get_mongodb


def import_records():
    db = get_mongodb()
    authors = db.authors.find()

    for author in authors:
        author_data = {
            "fullname": author["fullname"],
            "born_date": author["born_date"],
            "born_location": author["born_location"],
            "description": author["description"],
        }
        Author.objects.get_or_create(**author_data)

    quotes = db.quotes.find()
    for quote in quotes:
        tags = []
        for tag in quote.get("tags"):
            if tag:
                t, *_ = Tag.objects.get_or_create(name=tag)
                tags.append(t)

        exist_quote = bool(len(Quote.objects.filter(quote=quote["quote"])))
        if not exist_quote:
            author = db.authors.find_one({"_id": quote["author"]})
            a = Author.objects.get(fullname=author["fullname"])
            quote_data = {"author": a, "quote": quote["quote"]}
            q = Quote.objects.create(**quote_data)
            for tag in tags:
                q.tags.add(tag)


if __name__ == "__main__":
    import_records()
