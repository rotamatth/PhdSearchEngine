from collections import Counter
import random


def get_recommendations(history):
    if not history:
        print("No history provided")
        return {}

    history = [
        search for search in history
        if search.get("query") or search.get("location") or search.get("university") or search.get("year")
    ]

    if not history:
        print("Filtered history is empty")
        return {}

    titles = [search.get("query", "").strip() for search in history if search.get("query")]
    locations = [search.get("location", "").strip() for search in history if search.get("location")]
    employers = [search.get("university", "").strip() for search in history if search.get("university")]

    print(f"Titles: {titles}, Locations: {locations}, Employers: {employers}")

    recommendations = {
        "Title": Counter(titles).most_common(1)[0][0] if titles else None,
        "Location": Counter(locations).most_common(1)[0][0] if locations else None,
        "Employer": Counter(employers).most_common(1)[0][0] if employers else None
    }

    return {k: v for k, v in recommendations.items() if v}


# Example function for generating recommendations
def generate_recommendations(user_history, phd_positions):
    # Generate personalized recommendations based on user history.
    recommendations = []
    #generate recommendations based on title matches in user history
    for search_term in user_history:
        matching_positions = [
            pos for pos in phd_positions if search_term.lower() in pos['title'].lower()
        ]
        recommendations.extend(matching_positions)

    # Deduplicate recommendations based on title
    seen_titles = set()
    unique_recommendations = []
    for rec in recommendations:
        # Remove the prefix from the title
        rec["title"] = rec["title"].split(" ", 1)[-1]  # Remove the first word (e.g., 'sd-25117')

        # Avoid duplicates
        if rec["title"] not in seen_titles:
            unique_recommendations.append(rec)
            seen_titles.add(rec["title"])

    # Randomly shuffle recommendations to introduce diversity
    random.shuffle(unique_recommendations)

    # Limit to top 3 recommendations
    return unique_recommendations[:3]
