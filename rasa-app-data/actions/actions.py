from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType
from rasa_sdk.executor import CollectingDispatcher
from pymongo import MongoClient
import re
from bson.decimal128 import Decimal128

# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


# Class and Service Details
client = MongoClient('mongodb://khas:10G53JJaX8KH@213.238.182.152:27018/KHAS')
db = client['KHAS']
kategori_collection = db['Category']
specification_collection = db['SpecificationAttribute']
product_collection = db['Product']
pictures_collection = db['Picture']
baseimageurl = "https://omniecdn.blob.core.windows.net/omnitest/"
basewebsiteurl = "https://khas.mobitek.org/"

def get_picture_info(product):
    picture_info = []
    if 'ProductPictures' in product:
        for product_picture in product['ProductPictures']:
            picture_id = product_picture['PictureId']
            picture = pictures_collection.find_one({'_id': picture_id})
            if picture:
                picture_mimetype = picture['MimeType']
                image_type = picture_mimetype.split('/')[1]
                picture_info.append(f"<img src='{baseimageurl}{picture_id}_{picture['SeoFilename']}.{image_type}' width='150' height='150'>")
    return picture_info

def find_categories_and_features_and_write_items(mesaj):
    kategoriler = kategori_collection.find()
    kategori_dict = {kategori['Name'].lower(): kategori['_id'] for kategori in kategoriler}
    kategori_adlari = list(kategori_dict.keys())
    kategori_regex_pattern = r'\b(' + '|'.join(map(re.escape, kategori_adlari)) + r')\b'
    specification_attributes = specification_collection.find()
    specification_dict = {}
    for attribute in specification_attributes:
        for option in attribute['SpecificationAttributeOptions']:
            specification_dict[option['Name'].lower()] = option['_id']
    specification_adlari = list(specification_dict.keys())
    specification_regex_pattern = r'\b(' + '|'.join(map(re.escape, specification_adlari)) + r')\b'
    
    kategori_matches = re.findall(kategori_regex_pattern, mesaj.lower())
    specification_matches = re.findall(specification_regex_pattern, mesaj.lower()) 
    kategori_ids = [kategori_dict[match] for match in kategori_matches]
    specification_ids = [specification_dict[match] for match in specification_matches]
    specification_queries = [{"ProductSpecificationAttributes.SpecificationAttributeOptionId": spec_id} for spec_id in specification_ids]
    query = {
        "ProductCategories.CategoryId": {"$in": kategori_ids},
        "$and": specification_queries
    }   
    products = product_collection.find(query)
    product_list = []
    for product in products:
        picture_urls = get_picture_info(product)
        pictures = " ".join(picture_urls) 
        product_info = f"{product['Name']}\n{pictures}\n<a href='{basewebsiteurl}{product['SeName']}'>{basewebsiteurl}{product['SeName']}</a>"
        product_list.append(product_info)
    return product_list

def search_by_product(mesaj):
    products = product_collection.find()
    product_dict = {product['Name'].lower(): product['_id'] for product in products}
    product_names = list(product_dict.keys())
    product_regex_pattern = r'\b(' + '|'.join(map(re.escape, product_names)) + r')\b'
    product_matches = re.findall(product_regex_pattern, mesaj.lower())
    product_ids = [product_dict[match] for match in product_matches]

    product_query = {
        "_id": {"$in": product_ids}
    }

    products = product_collection.find(product_query)
    product_list = []
    for product in products:
        picture_urls = get_picture_info(product)
        pictures = " ".join(picture_urls)  # Resimleri boşluk ile ayırarak yazdırmak için
        product_info = f"{product['Name']}\n{pictures}\n<a href='{basewebsiteurl}{product['SeName']}'>{basewebsiteurl}{product['SeName']}</a>"
        product_list.append(product_info)
    return product_list

def category_products_Search(mesaj):
    kategoriler = kategori_collection.find()
    kategori_dict = {kategori['Name'].lower(): kategori['_id'] for kategori in kategoriler}
    # Kategori adları listesi oluştur
    kategori_adlari = list(kategori_dict.keys())  
    # Regex deseni oluştur
    mesaj_kelimeleri = mesaj.lower().split()
    kategori_ids = [kategori_dict[kategori] for kelime in mesaj_kelimeleri for kategori in kategori_adlari if kelime in kategori]
    # Ürünleri bul ve ekrana yazdır
    query = {
        "ProductCategories.CategoryId": {"$in": kategori_ids}
    } 
    products = product_collection.find(query)
    product_list = []
    for product in products:
        picture_urls = get_picture_info(product)
        pictures = " ".join(picture_urls)  # Resimleri boşluk ile ayırarak yazdırmak için
        product_info = f"{product['Name']}\n{pictures}\n<a href='{basewebsiteurl}{product['SeName']}'>{basewebsiteurl}{product['SeName']}</a>"
        product_list.append(product_info)  
    return product_list

def product_price_Search(mesaj):
    kategoriler = kategori_collection.find()
    kategori_dict = {kategori['Name'].lower(): kategori['_id'] for kategori in kategoriler}
    # Kategori Adlarını Listeleme ve Regex Deseni Oluşturma
    kategori_adlari = list(kategori_dict.keys())
    kategori_regex_pattern = r'\b(' + '|'.join(map(re.escape, kategori_adlari)) + r')\b'  
    # Mesaj İçinde Kategori ve Fiyat Eşleşmelerini Bulma
    kategori_matches = re.findall(kategori_regex_pattern, mesaj.lower())
    price_matches = re.findall(r'\b\d+(?:\.\d{1,2})?\b', mesaj.lower())  
    # Kategori Kimliklerini Elde Etme
    kategori_ids = [kategori_dict[match] for match in kategori_matches]
    # Fiyat Eşleşmesi ve Decimal128 Formatına Çevirme
    price_values = []
    for price in price_matches:
        price_values.append(Decimal128(price))
    # Kategori ve Fiyat bilgisi olmadan sorgu yapmayı engelleme
    if not kategori_ids or not price_values:
            return []
    # Fiyat Karşılaştırma Anahtar Kelimeleri
    low_price_keywords = ["low", "cheap", "under", "less"]
    high_price_keywords = ["high", "expensive", "over", "much", "above"]
    other_price_keywords = ["between", "among"]
    # Mesajdaki Fiyat Karşılaştırma Anahtar Kelimelerine Göre Sorgu Oluşturma
    if any(keyword in mesaj.lower() for keyword in low_price_keywords):
        query = {
            "ProductCategories.CategoryId": {"$in": kategori_ids},
            "Price": {"$lt": price_values[0]}
        }
    elif any(keyword in mesaj.lower() for keyword in high_price_keywords):
        query = {
            "ProductCategories.CategoryId": {"$in": kategori_ids},
            "Price": {"$gt": price_values[0]}
        }
    elif any(keyword in mesaj.lower() for keyword in other_price_keywords) and len(price_values) == 2:
        query = {
            "ProductCategories.CategoryId": {"$in": kategori_ids},
            "Price": {"$gte": price_values[0], "$lte": price_values[1]}
         }    
    else:
        query = {
            "ProductCategories.CategoryId": {"$in": kategori_ids},
            "Price": {"$lt": price_values[0]}  # Varsayılan olarak düşük fiyatlı ürünler
        }

    # Ürünleri Veritabanından Çekme
    products = product_collection.find(query)
    # Ürün Bilgilerini Listeleme
    product_list = []
    for product in products:
        picture_urls = get_picture_info(product)
        pictures = " ".join(picture_urls) 
        product_info = f"{product['Name']}\n{pictures}\n<a href='{basewebsiteurl}{product['SeName']}'>{basewebsiteurl}{product['SeName']}</a>"
        product_list.append(product_info) 
    return product_list   

class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    async def run(self, dispatcher,
                        tracker: Tracker, 
                        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # the session should begin with a `session_started` event
        events = [SessionStarted()]

        # any slots that should be carried over should come after the
        # `session_started` event
        events.extend(self.fetch_slots(tracker))

        # Send a greeting message
        #dispatcher.utter_message(template="utter_greet")

        # an `action_listen` should be added at the end as a user message follows
        events.append(ActionExecuted("action_listen"))

        return events
    
# class ExtractEntities(Action): 
#     def name(self) -> Text:
#         return "action_extract_entities"
#     def run(self, dispatcher: CollectingDispatcher,
#                     tracker: Tracker,
#                     domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         category = next(tracker.get_latest_entity_values('category'), None)
#         colour = next(tracker.get_latest_entity_values('colour'), None)
#         capacity = next(tracker.get_latest_entity_values('capacity'), None)
#         max_dpi = next(tracker.get_latest_entity_values('max_dpi'), None)


#         # Link oluşturma
#         link = f"https://khas.mobitek.org/{category}/?colour={colour}"
        
#         # HTML formatında mesaj oluşturma
#         message = f'Sure, here are the filtered products: <a href="{link}" target="_blank">{link}</a>'
        
#         # Mesajı basma
#         dispatcher.utter_message(text=message)

#         return []

class ActionSearch_by_Price(Action):
  def name(self) -> Text:
        return "action_product_price_Search"

  def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        mesaj = tracker.latest_message.get('text')
        
        # Arama işlemini gerçekleştirin
        results = product_price_Search(mesaj)
        
        if results:
            dispatcher.utter_message(text="I show the product you specified for you:")
            for result in results:
                dispatcher.utter_message(text=result)
        else:
            dispatcher.utter_message(text="Sorry, no products matching your search criteria were found.")
            
        return []    

class ActionSearch_by_product(Action):
  def name(self) -> Text:
        return "action_search_by_product"

  def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        mesaj = tracker.latest_message.get('text')
        
        # Arama işlemini gerçekleştirin
        results = search_by_product(mesaj)
        
        if results:
            dispatcher.utter_message(text="I show the product you specified for you:")
            for result in results:
                dispatcher.utter_message(text=result)
        else:
            dispatcher.utter_message(text="Sorry, no products matching your search criteria were found.")
            
        return []

class ActionCategory_Products_Search(Action):
  def name(self) -> Text:
        return "action_category_products_search"

  def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        mesaj = tracker.latest_message.get('text')
        
        # Arama işlemini gerçekleştirin
        results = category_products_Search(mesaj)
        
        if results:
            dispatcher.utter_message(text="I'm listing the products in the category you specified for you:")
            for result in results:
                dispatcher.utter_message(text=result)
        else:
            dispatcher.utter_message(text="Sorry, no products matching your search criteria were found.")
            
        return []

class ActionSearchByFeature(Action):

    def name(self) -> Text:
        return "action_search_by_feature"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        mesaj = tracker.latest_message.get('text')
        
        # Arama işlemini gerçekleştirin
        results = find_categories_and_features_and_write_items(mesaj)
        
        if results:
            dispatcher.utter_message(text="I have listed the products of the feature and category you specified for you:")
            for result in results:
                dispatcher.utter_message(text=result)
        else:
            dispatcher.utter_message(text="Sorry, no products matching your search criteria were found.")
            
        return []