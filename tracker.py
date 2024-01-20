from pymongo import MongoClient
from datetime import datetime
from pricing import priceFlipkart, priceAmazon

def update_tracker():
    mongo_uri = "mongodb+srv://lakshya3:312004lakshya@cluster0.sdupdia.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(mongo_uri)
    database_name = "IITJ"
    collection_name = "ProductTracker"
    db = client[database_name]
    collection = db[collection_name]
    documents = collection.find()
    updated_data=[]
    for document in documents:
        url=document["url"]
        if "amazon" in url:
            price=priceAmazon(url)["price"]
        else:
            price=priceFlipkart(url)["price"]
        document["data"].append({"price":price,"time":datetime.now()}) #convert into string if not working
        updated_data.append({"url":url,"data":{"price":price,"time":str(datetime.now())}})
        collection.update_one({"_id": document["_id"]}, {"$set": document})
        print(f"Updated {document['_id']} with {price} at {datetime.now()}")
    call_back_url(updated_data)
    client.close()
    
def call_back_url(data):
    import requests
    url="https://dropmytest.onrender.com/price-change"
    response=requests.post(url,json=data)
    print(response.text)
    
def add_to_tracker(url:str):
    mongo_uri = "mongodb+srv://lakshya3:312004lakshya@cluster0.sdupdia.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(mongo_uri)
    database_name = "IITJ"
    collection_name = "ProductTracker"
    db = client[database_name]
    collection = db[collection_name]
    document = collection.find_one({"url": url})
    if document:
        return "Already in Tracker"
    else:
        document={"url":url,"data":[]}
        collection.insert_one(document)
        return "Added to Tracker"