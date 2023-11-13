from flask import Flask, render_template, request, url_for, jsonify
import http.client
import json
import re
import requests
import urllib.parse

app = Flask(__name__)

RAPIDAPI_KEY = "c5a2ffe436msh751d8ed39930b58p19da33jsn81112dfec3fa"
GAMESPOTAPI_KEY = "15db3545ca5bec59186fca6096262dfacf0c7659"
RAPIDAPI_HOST = "steam2.p.rapidapi.com"
GAME_SPOT_API_BASE_URL = "https://www.gamespot.com/api"


def sanitize_input(input_str):
    return re.sub(r'[^a-zA-Z0-9]', '', input_str)


@app.route("/", methods=['GET'])
def login():
    return render_template("index.html")


@app.route("/get-steam-user-summary/<steamId>", methods=['GET'])
def get_steam_user_summary(steamId):
    steamApiKey = "E4ABF7871264272AD62B7798CCF512DC"
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={steamApiKey}&steamids={steamId}"
    response = requests.get(url)
    return response.json()


def get_reviews_for_app(appId, limit=40):
    conn = http.client.HTTPSConnection("steam2.p.rapidapi.com")
    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': RAPIDAPI_HOST
    }

    endpoint = f"/appReviews/{appId}/limit/{limit}/*"
    conn.request("GET", endpoint, headers=headers)

    res = conn.getresponse()
    reviews_data = json.loads(res.read().decode("utf-8"))

    return reviews_data


@app.route("/home", methods=['GET'])  # Using the root path for homepage
def home():
    conn = http.client.HTTPSConnection("steam-store-data.p.rapidapi.com")

    headers = {
        'X-RapidAPI-Key': 'f9e9157472mshd29534641f6cf76p17a316jsnd7768c1ea96e',
        'X-RapidAPI-Host': 'steam-store-data.p.rapidapi.com'
    }

    conn.request("GET", "/api/featuredcategories/", headers=headers)

    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))

    categories = {k: v for k, v in data.items() if isinstance(v, dict) and 'items' in v}

    # Adding detail URLs to each item using the game's ID
    for category in categories.values():
        for item in category['items']:
            if 'id' in item:
                item['detail_url'] = url_for('game_detail', game_id=item['id'])
            else:
                print(f"Missing ID for item: {item.get('name', 'Unknown Item')}")

    return render_template("home.html", categories=categories)


@app.route("/game/<int:appid>/news", methods=['GET'])
def game_news(appid):
    conn = http.client.HTTPSConnection("steam2.p.rapidapi.com")
    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': RAPIDAPI_HOST
    }

    endpoint = f"/newsForApp/{appid}/limit/10/300"  # Use the app_id dynamically
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))

    # Debugging: Print the data to see if it contains news items
    print(data)

    if 'appnews' in data and 'newsitems' in data['appnews']:
        newsitems = data['appnews']['newsitems']
        # Debugging: Print the news_items
        print(newsitems)
    else:
        newsitems = []

    # Debugging: Print a message if no news items were found
    if not newsitems:
        print("No news items found.")

    # Change this to the template you're actually using for game details
    return render_template("gamedetails.html", news=newsitems, appid=appid)


@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return render_template("search.html", error="Please enter a search query.", games=[])

    print(f"Query before encoding: {query}")
    encoded_query = urllib.parse.quote_plus(query)
    print(f"Query after encoding: {encoded_query}")

    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': RAPIDAPI_HOST
    }

    endpoint = f"/search/{encoded_query}/page/1"
    print(f"Endpoint: {endpoint}")
    print(f"Headers: {headers}")

    try:
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        print(f"Status Code: {res.status}")

        response_data = json.loads(res.read().decode("utf-8"))
        print(f"Response: {response_data}")

        games = response_data  # This assumes the response is a list of games. Adjust accordingly if it's not.

    except Exception as e:
        # Log the exception for debugging
        print(f"Error: {e}")
        return render_template("search.html", error="Failed to fetch game results. Please try again.", games=[])

    if not games:
        return render_template("search.html", error="No games found for the given query.", games=[])

    return render_template("search.html", games=games)


@app.route("/game/<int:game_id>", methods=['GET'])
def game_detail(game_id):
    conn = http.client.HTTPSConnection("steam2.p.rapidapi.com")
    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': RAPIDAPI_HOST
    }


@app.route("/home", methods=['GET'])
def get_articles():
    print("Fetching articles...")  # Confirm this line is printed in the console
    headers = {
        'User-Agent': 'SteamSync/1.0 (cvillatoro2021@fau.edu)',
        'Authorization': 'Bearer ' + GAMESPOTAPI_KEY
    }
    params = {
        'format': 'json'
    }
    response = requests.get(f"{GAME_SPOT_API_BASE_URL}/articles/", headers=headers, params=params)

    print("Response Status Code:", response.status_code)  # Check the response status code
    if response.status_code == 200:
        data = response.json()
        print("API Response:", data)  # Debug print

        articles = data.get('results', [])
        print("Found articles:", articles)  # Debug print if articles are found
        return render_template('home.html', articles=articles)
    else:
        error_message = response.json().get('error', 'Unknown Error')
        print('Error fetching articles:', error_message, response.status_code)  # Debug print with status code
        return jsonify({'error': error_message}), response.status_code




    # Fetching game details
    conn.request("GET", f"/appDetail/{game_id}", headers=headers)
    res = conn.getresponse()
    game = json.loads(res.read().decode("utf-8"))

    # Fetching game reviews
    conn.request("GET", f"/appReviews/{game_id}/limit/40/*", headers=headers)
    res_reviews = conn.getresponse()
    reviews_data = json.loads(res_reviews.read().decode("utf-8"))
    reviews = reviews_data['reviews'][:10]  # extracting the first 10 reviews

    # Fetching game news
    endpoint = f"/newsForApp/{game_id}/limit/10/300"  # Use the game_id dynamically
    conn.request("GET", endpoint, headers=headers)
    res_news = conn.getresponse()
    news_data = json.loads(res_news.read().decode("utf-8"))
    newsitems = news_data.get('appnews', {}).get('newsitems', [])[:5]

    # Rendering the template with game details, reviews, and news
    return render_template("game_detail.html", game=game, reviews=reviews, news=newsitems)


if __name__ == "__main__":
    app.run(debug=True)
