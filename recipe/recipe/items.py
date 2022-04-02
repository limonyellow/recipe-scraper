# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RecipeItem(scrapy.Item):
    # Define the fields for the item created after parsing recipe page:
    url = scrapy.Field()
    title = scrapy.Field()
    # content = scrapy.Field()
    time_to_parse = scrapy.Field()
    ingredients = scrapy.Field()
