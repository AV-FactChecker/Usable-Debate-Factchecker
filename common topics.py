from newsapi import NewsApiClient
import datetime
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import Pinecone, ServerlessSpec
from pinecone_text.sparse import BM25Encoder
from sentence_transformers import SentenceTransformer


bm25 = BM25Encoder()
model = SentenceTransformer('all-mpnet-base-v2')


def generate_embeddings(texts : list[str]):
    fitted = bm25.fit(texts)
    embeddings= bm25.encode_documents(texts)

    return embeddings

def generate_dense(sentences):
    embeddings = model.encode(sentences)
    return embeddings


pc = Pinecone(api_key="${{secrets.PINECONE_API_KEY}}")

if "factcheck-article-data-tvisha-avhs" not in pc.list_indexes().names():
    pc.create_index(
        name="factcheck-article-data-tvisha-avhs",
        dimension=768, 
        metric="cosine",  
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ) 
    )


index = pc.Index("factcheck-article-data-tvisha-avhs")


topics = ["abortion", "environment", "economic policy", "foreign policy", "immigration", "war in Gaza", "police and safety", "voting rights", "education", "project 2025", "Kamala Harris", "Donald Trump", "Joe Biden", "Tim Walz", "JD Vance", "LGBTQ rights", "womens rights", "American politics", "USA", "presidential election", "presidential debate", "US debt", "race", "healthcare", "gun laws", "policy making", "US Economy", "RNC", "assassination", "arlington", "shooting", "Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut", "District ", "of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming", "gay, transgender", "Trump assassination"]


count = 0

for topic in topics:
    newsapi = NewsApiClient(api_key='${{secrets.NEWS_API_KEY}}')

    # from (datetime.date.today().replace(day=1)-datetime.timedelta(days=1)).replace(day=datetime.date.today().day).strftime("%Y %m %d")
    # to datetime.date.today().strftime("%Y %m %d")
    all_articles = newsapi.get_everything(
                                        q=topic,
                                        from_param='2024-09-06',
                                        to='2024-09-10',
                                        language='en',
                                        sort_by='relevancy',
                                        )
    
    article_content = []


    for i in all_articles['articles']:
        article_content.append(str(i['description']))

    print(len(article_content))

    embeddings = generate_embeddings(article_content)
    dense_embeddings = generate_dense(article_content)

    
    vectors = []
    


    for embedding in range(len(embeddings)):
        vectors.append(
            {
                "id" : "article_" + str(9115+embedding + 100*count),
                "values" : dense_embeddings[embedding],
                "sparse_values" : embeddings[embedding],
                "metadata" : {"text": article_content[embedding]}
            }
        )
    index.upsert(vectors)

    print(index.describe_index_stats())

    count += 1




