import os
import pickle
import scipy.sparse
import pandas as pd
from heapq import heappush, heappop
import scipy.spatial
import requests
import wikipedia

from main.models import Article
from celery import shared_task
from sklearn.feature_extraction.text import TfidfVectorizer
import bs4


@shared_task
def check_model_files():
    if os.path.exists("model.pickle") and os.path.exists("data.npz"):
        return "model_ready"
    return "model_not_ready"

@shared_task
def train_model_and_save():
    max_articles_train = int(os.environ.get("NUM_ARTICLE", 1000))

    Article.objects.all().delete()
    try:
        data = pd.read_csv("wiki_movie_plots_deduped.csv").sample(max_articles_train)
    except Exception as e:
        raise Exception(f"Error loading data: {e}")

    text_corpus = list(data.Plot)

    articles = [
        Article(
            number=i,
            title=data.iloc[i].Title[:100],
            url=data.iloc[i]["Wiki Page"][:100],
            summary=data.iloc[i].Plot[:4000],
        )
        for i in range(data.shape[0])
    ]
    Article.objects.bulk_create(articles)

    model = TfidfVectorizer(
        analyzer="word", stop_words="english", strip_accents="ascii"
    )
    param_matrix = model.fit_transform(text_corpus)

    if os.path.exists("model.pickle"):
        os.remove("model.pickle")
    if os.path.exists("data.npz"):
        os.remove("data.npz")

    with open("model.pickle", "wb") as f:
        pickle.dump(model, f)

    scipy.sparse.save_npz("data.npz", param_matrix)


@shared_task
def get_similar_articles(url, cnt):
    try:
        response = requests.get(url)
    except Exception as e:
        raise Exception(f"Error fetching URL: {e}")

    if response:
        html = bs4.BeautifulSoup(response.text, "html.parser")
        title = html.select("#firstHeading")[0].text
    else:
        raise Exception(f"URL not found: {url}")

    try:
        page = wikipedia.page(title, auto_suggest=False)
        content = page.content
    except Exception as e:
        raise Exception(f"Error fetching Wikipedia page: {e}")

    if not os.path.exists("model.pickle") or not os.path.exists("data.npz"):
        raise Exception("Model not trained yet")

    with open("model.pickle", "rb") as model_file:
        model = pickle.load(model_file)

    data = scipy.sparse.load_npz("data.npz")
    film_summary_vector = model.transform([content]).toarray()
    row_number = 0
    top = []

    for row in data:
        vec = row.toarray()
        dist = scipy.spatial.distance.euclidean(
            vec.reshape(-1), film_summary_vector.reshape(-1)
        )
        heappush(top, (-dist, row_number))
        if len(top) > cnt:
            heappop(top)
        row_number += 1

    top = sorted(top, reverse=True)
    films = []
    for dist, num in top:
        film = Article.objects.get(number=num)
        films.append(film)

    return films, page.title
