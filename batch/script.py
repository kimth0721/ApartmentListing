from kafka import KafkaProducer
from elasticsearch import Elasticsearch
from kafka import KafkaConsumer
import time
import json

time.sleep(15)
print("Batch Script Running")
consumer = KafkaConsumer('new-listings-topic', group_id='listing-indexer', bootstrap_servers=['kafka:9092'])
es = Elasticsearch(['es'])

fixtures = [{"name": "Apartment 1", "price": 750, "rating": "3.50", "username": "cyeung", "id": 1}, {"name": "Apartment 2", "price": 875, "rating": "2.95", "username": "cyeung", "id": 2},
            {"name": "Apartment 3", "price": 1925, "rating": "4.25", "username": "cyeung", "id": 3}, {"name": "Apartment 4", "price": 968, "rating": "4.95", "username": "tk9at", "id": 4},
            {"name": "Apartment 5", "price": 478, "rating": "3.81", "username": "tk9at", "id": 5}, {"name": "Apartment 6 ", "price": 899, "rating": "4.50", "username": "tk9at", "id": 6},
            {"name": "Apartment 7", "price": 2500, "rating": "1.50", "username": "bradyw7", "id": 7}, {"name": "Apartment 8", "price": 2384, "rating": "0.75", "username": "bradyw7", "id": 8}]
for apartment in fixtures:
    es.index(index='listing_index', doc_type='listing', id=apartment['id'], body=apartment)
    #es.index(index='listing_index', doc_type='username', id=apartment['username'], body =apartment)
    es.indices.refresh(index="listing_index")
print("Fixtures Loaded.")


for message in consumer:
    new_listing = json.loads((message.value).decode('utf-8'))[0]
    print(new_listing)
    es.index(index='listing_index', doc_type='listing', id=new_listing['id'], body=new_listing)
    #es.index(index='listing_index', doc_type='username', id=new_listing['username'], body=new_listing)
    es.indices.refresh(index="listing_index")