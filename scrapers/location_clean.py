import pandas as pd

known_countries = {
    "the netherlands", "germany", "switzerland", "france", "belgium",
    "luxembourg", "austria", "sweden", "norway", "finland", "denmark",
    "italy", "spain", "israel", "china", "united states", "uk",
    "ireland", "czech republic", "turkey", "greece", "portugal",
    "poland", "russia", "japan", "south korea", "australia"
}
iso_map = {
    "de": "Germany", "fr": "France", "nl": "The Netherlands",
    "us": "United States", "uk": "United Kingdom",
    "be": "Belgium", "ch": "Switzerland", "se": "Sweden",
    "no": "Norway", "fi": "Finland", "it": "Italy",
    "es": "Spain", "il": "Israel", "cn": "China", "tw": "Taiwan"
}
manual_corrections = {
    "westmead, sydney": "Australia",
    "manhasset, new york": "United States",
    "toscana life sciences, within the gsk campus, siena (italy)": "Italy",
    "hsinchu (tw)": "Taiwan",
    "chicago, illinois": "United States",
    "esch-sur-alzette": "Luxembourg",
    "galway (county), connacht (ie)": "Ireland",
    "aarhus, midtjylland (dk)": "Denmark",
    "odense, fyn (dk)": "Denmark",
    "antwerp": "Belgium",
    "brooklyn, new york": "United States",
    "united kingdom": "United Kingdom",
    "dresden": "Germany",
    "ostrava, czech republic (cz)": "Czech Republic",
    "ghent": "Belgium",
    "cambridgeshire (gb)": "United Kingdom",
    "chestnut hill, massachusetts": "United States",
    "bethesda, md (nih main campus)": "United States",
    "austria (at)": "Austria"
}

def extract_country(location_str):
    if pd.isna(location_str):
        return "Not recognized"
    location_str_clean = location_str.strip().lower()
    if location_str_clean in manual_corrections:
        return manual_corrections[location_str_clean]
    parts = [p.strip().lower() for p in location_str.split(",") if p.strip()]
    for part in reversed(parts):
        if part in known_countries:
            return part.capitalize()
        if "(" in part and ")" in part:
            code = part.split("(")[-1].split(")")[0].lower()
            if code in iso_map:
                return iso_map[code]
    return location_str

input_file = 'data/cleaned/positions_cleaned.csv'
output_file = 'data/cleaned/positions_cleaned.csv'

locations_df = pd.read_csv(input_file)
locations_df['Location'] = locations_df['Location'].apply(extract_country)
locations_df.to_csv(output_file, index=False)
print(f"Saved in '{output_file}'")
