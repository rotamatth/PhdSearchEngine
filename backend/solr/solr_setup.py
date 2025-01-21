import pandas as pd
import pysolr

def import_data_to_solr():
    solr = pysolr.Solr('http://localhost:8983/solr/phd_positions', always_commit=True)
    df = pd.read_csv('../../scrapers/data/cleaned/positions_cleaned.csv')
    df['id'] = df.index.astype(str)
    documents = df.to_dict(orient='records')
    solr.add(documents)
    print(f"Indexed {len(documents)} documents to Solr.")

def search_solr(query, rows=10):
    solr = pysolr.Solr('http://localhost:8983/solr/phd_positions', always_commit=True)
    results = solr.search(query, rows=rows)
    if len(results) == 0:
        print("No results found for the query.")
    else:
        for doc in results:
            print(doc)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Solr Import and Search")
    parser.add_argument('--import-data', action='store_true', help="Import data to Solr")
    parser.add_argument('--search', type=str, help="Search query for Solr")
    parser.add_argument('--rows', type=int, default=10, help="Number of rows to fetch in search results")

    args = parser.parse_args()

    # Validate arguments
    if args.import_data:
        import_data_to_solr()
    elif args.search:
        search_solr(args.search, rows=args.rows)
    else:
        print("Please provide an action, either --import-data or --search.")
