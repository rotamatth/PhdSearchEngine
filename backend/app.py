from flask import Flask, render_template, request, jsonify, session
import json
import requests
import os
import random
from werkzeug.security import generate_password_hash, check_password_hash
from recommender import get_recommendations  # Importing the function

app = Flask(__name__, static_url_path="/static")
app.secret_key = "your_secret_key"

SOLR_URL = "http://localhost:8983/solr/phd_positions/select"

# User management functions

def load_users():
    try:
        if not os.path.exists("database/users.json"):
            return {}  # If the file doesn't exist, return an empty dictionary
        with open("database/users.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def save_users(users):
    try:
        os.makedirs("database", exist_ok=True)  # Ensure the directory exists
        with open("database/users.json", "w") as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        print(f"Error saving users: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recommendations")
def recommendations():
    if "username" not in session:
        return jsonify([])  # Return empty if not logged in

    username = session["username"]
    users = load_users()

    if username not in users or not users[username].get("search_history"):
        return jsonify([])  # No recommendations if no history

    try:
        history = users[username]["search_history"]
        filters = get_recommendations(history)

        # Fetch popular/trending results if no filters
        if not filters:
            params = {"q": "*:*", "rows": 3, "sort": "Published desc", "wt": "json"}
            response = requests.get(SOLR_URL, params=params)
            response.raise_for_status()
            solr_results = response.json()["response"]["docs"]

            recommendations = [
                {
                    "title": doc.get("Title", ""),
                    "university": doc.get("Employer", ""),
                    "location": doc.get("Location", ""),
                    "year": doc.get("Published", ""),
                    "link": doc.get("URL", "")
                }
                for doc in solr_results
            ]

            users[username]["recommendations"] = recommendations
            save_users(users)
            return jsonify(recommendations)

        # Build the query dynamically
        query_parts = []
        if filters.get("Title"):
            query_parts.append(f"Title:{filters['Title']}")
        if filters.get("Location"):
            query_parts.append(f"Location:{filters['Location']}")
        if filters.get("Employer"):
            query_parts.append(f"Employer:{filters['Employer']}")

        query = " OR ".join(query_parts)
        params = {"q": query, "rows": 10, "wt": "json"}
        response = requests.get(SOLR_URL, params=params)
        response.raise_for_status()

        solr_results = response.json()["response"]["docs"]

        # Deduplicate and clean recommendations
        seen_titles = set()
        recommendations = []
        for doc in solr_results:
            title = doc.get("Title", "")
            if isinstance(title, list):
                title = " ".join(title)  # Handle list of titles
            cleaned_title = title.split(" ", 1)[-1]  # Clean title
            if cleaned_title not in seen_titles:
                recommendations.append({
                    "title": cleaned_title,
                    "university": doc.get("Employer", ""),
                    "location": doc.get("Location", ""),
                    "year": doc.get("Published", ""),
                    "link": doc.get("URL", "")
                })
                seen_titles.add(cleaned_title)

        # Shuffle recommendations
        random.shuffle(recommendations)

        # Save recommendations to user data
        # Limit recommendations to 3
        recommendations = recommendations[:3]

        # Save recommendations to user data
        users[username]["recommendations"] = recommendations
        save_users(users)  # Persist changes
        return jsonify(recommendations)

            
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return jsonify([])

@app.route("/filters")
def filters():
    try:
        filters = {"locations": [], "universities": [], "years": []}
        for field, key in [("Location_str", "locations"), ("Employer_str", "universities"), ("Published_str", "years")]:
            solr_query = f"{SOLR_URL}?q=*:*&facet=true&facet.field={field}&rows=0&wt=json"
            print(f"Querying Solr for {field}: {solr_query}")  # Log per debug
            response = requests.get(solr_query)
            response.raise_for_status()
            data = response.json()
            print(f"Response for {field}: {data}")  # Log l'intera risposta di Solr
            filters[key] = data["facet_counts"]["facet_fields"].get(field, [])[::2]  # Prendi i valori
        return jsonify(filters)
    except Exception as e:
        print(f"Error fetching filters: {e}")
        return jsonify({"error": "Could not fetch filters"}), 500


@app.route("/search")
def search():
    query = request.args.get("query", "").strip()
    location = request.args.get("location", "").strip()
    university = request.args.get("university", "").strip()
    year = request.args.get("year", "").strip()

    solr_query = '*:*' if not query else f"Title:{query} OR Employer:{query} OR Location:{query}"

    solr_params = {
        'q': solr_query,
        'rows': 100,
        'wt': 'json',
    }

    filters = []
    if location:
        filters.append(f'Location:"{location}"')
    if university:
        filters.append(f'Employer:"{university}"')
    if year:
        filters.append(f'Published:"{year}"')

    if filters:
        solr_params['fq'] = ' AND '.join(filters)

    try:
        response = requests.get(SOLR_URL, params=solr_params)
        response.raise_for_status()
        data = response.json()

        results = [
            {
                "title": doc.get("Title", ""),
                "university": doc.get("Employer", ""),
                "location": doc.get("Location", ""),
                "year": doc.get("Published", ""),
                "link": doc.get("URL", ""),
            }
            for doc in data["response"]["docs"]
        ]

        # Log search history for logged-in users
        if "username" in session:
            username = session["username"]
            users = load_users()

            users[username]["search_history"].append({
                "query": query,
                "location": location,
                "university": university,
                "year": year
            })
            save_users(users)

        return jsonify(results)
    except Exception as e:
        print(f"Error querying Solr: {e}")
        return jsonify({"error": "Could not fetch results"}), 500

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json  # Get JSON data from the request
        print("Received registration data:", data)  # Debugging: Print received data

        if not data:
            raise ValueError("No data provided in the request.")

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"success": False, "message": "Username and password are required."}), 400

        users = load_users()
        print("Loaded users:", users)  # Debugging: Print current users

        if username in users:
            return jsonify({"success": False, "message": "Username already exists."}), 400

        # Add new user
        users[username] = {
            "password": generate_password_hash(password),
            "search_history": [],
            "recommendations": []
        }
        save_users(users)
        print("User registered successfully:", username)  # Debugging: Log success
        return jsonify({"success": True, "message": "User registered successfully."})
    except Exception as e:
        print(f"Error in /register: {e}")  # Log detailed error
        return jsonify({"success": False, "message": "Internal server error."}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    users = load_users()

    if username in users and check_password_hash(users[username]["password"], password):
        session["username"] = username
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid username or password"})

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)
