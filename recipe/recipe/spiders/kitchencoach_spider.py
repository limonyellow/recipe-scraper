import string

import scrapy

from recipe.items import RecipeItem


class KitchenCoachSpider(scrapy.Spider):
    # The name of the spider. Will be used when calling for it to run.
    name = 'the_kitchen_coach'
    # The urls to run the spider on.
    start_urls = [
        # 'https://www.thekitchencoach.co.il/',
        # 'https://www.thekitchencoach.co.il/%d7%9e%d7%9c%d7%96%d7%99%d7%aa-%d7%9e%d7%aa%d7%9b%d7%95%d7%9f/',
        'https://www.thekitchencoach.co.il/category/%D7%9E%D7%AA%D7%9B%D7%95%D7%A0%D7%99%D7%9D/'
    ]
    # Defining the borders the spider can run in.
    allowed_domains = ['www.thekitchencoach.co.il']

    def parse(self, response, **kwargs):
        # Parsing the main page.
        # With css or xpath method on response object the returned object is 'Selector'.
        # Use 'get()' for the first element or 'getall()'/'extract()' for a list of all elements.
        # Read more on selectors - css: 'https://www.w3schools.com/cssref/css_selectors.asp'
        # xpath: 'http://zvon.org/comp/r/tut-XPath_1.html#intro', 'https://www.w3schools.com/xml/xpath_syntax.asp'
        recipes_links = response.css('div.post-listing div.entrytitmet a::attr(href)').getall()
        # Equivalent to the use of xpath expression:
        # recipes_href = \
        #     response.xpath('//div[@class="post-listing"]/descendant::div[@class="entrytitmet"]/descendant::a[@href]')
        # recipes_links = [href_tag.attrib['href'] for href_tag in recipes_href]

        for link in recipes_links:
            # Run the spider on the given url ('link') with the 'callback' function.
            yield response.follow(link, callback=self.parse_recipe_page)

        # Trying to find and parse the next page:
        next_page_link = response.css('div.pagination span#tie-next-page a::attr(href)').get()
        if next_page_link:
            yield response.follow(next_page_link, callback=self.parse)

    def parse_recipe_page(self, response):
        """
        Parse a single recipe page. Extracts all the ingredients text and metadata.
        Yields the parsed data items. They will be stored using scrapy pipeline.
        Args:
            response: The recipe web page.

        Yields:
            RecipeItem object.
        """
        url = response.url
        title = response.css('title::text').get()
        image_url = response.css('div.pf-content img::attr(src)').get()

        # Extracting the ingredients from their section in the recipe page.
        ingredients_sentences = \
            response.xpath("//h4[contains(text(),'מצרכים')]/following-sibling::h4/preceding-sibling::"
                           "p[preceding-sibling::h4[contains(text(),'מצרכים')]]/text()").extract()
        ingredients_words = ''.join(
            [''.join([c for c in sentence if not c.isdigit() and c not in string.punctuation]) for sentence in
             ingredients_sentences])
        ingredients_words = [word for word in ingredients_words.split(' ') if len(word) > 1]

        # Inserting the data into the result object.
        yield RecipeItem(
            site_name=self.name,
            url=url,
            title=title,
            image_url=image_url,
            ingredients=ingredients_words,
        )
