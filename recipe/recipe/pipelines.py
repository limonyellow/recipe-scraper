# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import logging
import os
from time import perf_counter

import certifi
import pymongo

MONGODB_HOST = os.environ.get('RECIPE_SCRAPER_MONGODB_HOST', 'localhost')
MONGODB_OPTIONS = os.environ.get('RECIPE_SCRAPER_MONGODB_OPTIONS', '')
MONGODB_LOCAL_PORT = 27017
MONGODB_USERNAME = os.environ.get('RECIPE_SCRAPER_MONGODB_USERNAME')
MONGODB_PASSWORD = os.environ.get('RECIPE_SCRAPER_MONGODB_PASSWORD')
MONGODB_RECIPES_DB_NAME = 'recipes'
MONGODB_KITCHEN_COACH_COLL_NAME = 'kitchencoach'
MONGODB_INGREDIENTS_COLL_NAME = 'ingredients'
MONGODB_CONNECTION_STRING = f'mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}?{MONGODB_OPTIONS}'


class RecipePipeline:
    def __init__(self):
        """
        Initialize the connection to mongodb.
        """
        self.conn = pymongo.MongoClient(MONGODB_CONNECTION_STRING, tlsCAFile=certifi.where())
        db = self.conn[MONGODB_RECIPES_DB_NAME]
        self.kitchen_coach_collection = db[MONGODB_KITCHEN_COACH_COLL_NAME]
        self.ingredients_collection = db[MONGODB_INGREDIENTS_COLL_NAME]
        self.logger = logging.getLogger(__name__)
        self.counter = 0

    def process_item(self, item, spider):
        """
        Inserts the recipe item to two mongodb collections:
        kitchencoach - Stores each recipe and its details.
        ingredients - Stores every unique ingredient word.
            Along the ingredient, there will be references to all the recipes urls the ingredient is appeared in and
            how many times.
        """
        start = perf_counter()
        # Creates the document of the recipe with all the related ingredients.
        url = item['url']
        query = {'url': f'{url}'}
        update = {'$set': dict(item)}
        self.kitchen_coach_collection.update_one(query, update, upsert=True)
        ingredients = item['ingredients']
        for ingredient in ingredients:
            # Creates the document of the ingredient if not exists.
            query = {'name': f'{ingredient}'}
            update = {'$set': {'name': f'{ingredient}'}}
            self.ingredients_collection.update_one(query, update, upsert=True)

            # Creates the object of the url if not exists.
            query = {'name': f'{ingredient}', 'urls': {'$not': {'$elemMatch': {'url': f'{url}'}}}}
            update = {'$addToSet': {'urls': {'url': f'{url}', "counter": 0}}}
            self.ingredients_collection.find_one_and_update(query, update)

            # Increment the counter of the url.
            query = {'name': f'{ingredient}', 'urls': {'$elemMatch': {'url': f'{url}'}}}
            update = {'$inc': {'urls.$.counter': 1}}
            self.ingredients_collection.find_one_and_update(query, update)

        self.counter += 1
        end = perf_counter()
        process_time = end - start
        self.logger.info(
            f'Successfully processed item #{self.counter} "{item.get("title")}" in {process_time=}`s',
            extra={'counter': self.counter}
        )
        return item
