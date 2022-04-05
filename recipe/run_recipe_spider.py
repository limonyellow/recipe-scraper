import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from recipe.spiders.kitchencoach_spider import KitchenCoachSpider

if __name__ == '__main__':
    # Preparing the settings:
    settings_file_path = 'recipe.settings'  # The path seen from root.
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
    process = CrawlerProcess(get_project_settings())

    # KitchenCoachSpider is the class of the spider.
    p = process.crawl(KitchenCoachSpider)
    process.start()  # the script will block here until the crawling is finished
