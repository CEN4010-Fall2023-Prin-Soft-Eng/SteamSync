from flask import Flask, render_template, request, url_for
import http.client
import json
import re
import requests


app = Flask(__name__)

RAPIDAPI_KEY = "f9e9157472mshd29534641f6cf76p17a316jsnd7768c1ea96e"
RAPIDAPI_HOST = "steam2.p.rapidapi.com"


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
        'X-RapidAPI-Key': "f9e9157472mshd29534641f6cf76p17a316jsnd7768c1ea96e",
        'X-RapidAPI-Host': "steam2.p.rapidapi.com"
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
        'X-RapidAPI-Key': 'f9e9157472mshd29534641f6cf76p17a316jsnd7768c1ea96e',  # Replace with your actual API key
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


import urllib.parse

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
        'X-RapidAPI-Key': "f9e9157472mshd29534641f6cf76p17a316jsnd7768c1ea96e",
        'X-RapidAPI-Host': "steam2.p.rapidapi.com"
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
        'X-RapidAPI-Key': "f9e9157472mshd29534641f6cf76p17a316jsnd7768c1ea96e",
        'X-RapidAPI-Host': "steam2.p.rapidapi.com"
    }

    # Fetching game details
    conn.request("GET", f"/appDetail/{game_id}", headers=headers)
    res = conn.getresponse()
    game = json.loads(res.read().decode("utf-8"))

    # Fetching game reviews
    conn.request("GET", f"/appReviews/{game_id}/limit/40/*", headers=headers)# adjust the limit as needed
    res_reviews = conn.getresponse()
    reviews_data = json.loads(res_reviews.read().decode("utf-8"))

    # Extracting the first 10 reviews
    reviews = reviews_data['reviews'][:10]  # extracting the first 10 reviews

    # Rendering the template with game details and reviews
    return render_template("game_detail.html", game=game, reviews=reviews)


if __name__ == "__main__":
    app.run(debug=True)


