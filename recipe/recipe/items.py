# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RecipeItem(scrapy.Item):
    """
    Define the fields for the item created after parsing recipe page
    Args:
        site_name - The name of the recipe site.
        url - The url of the recipe page.
        title - The title of the recipe page.
        image_url - The url of the recipe image.
        ingredients - List of words from the ingredient section of the recipe.
    """
    site_name = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    image_url = scrapy.Field()
    ingredients = scrapy.Field()
