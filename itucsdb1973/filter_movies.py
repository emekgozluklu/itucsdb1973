import csv

rows = []

with open("movies.csv") as input_file:
    for row in csv.reader(input_file):
        rows.append(row)

interested_columns = {'budget': 2, 'genres': 3, 'imdb_id': 6,
                      'language': 7, 'overview': 9,
                      'popularity': 10, 'production_companies': 12,
                      'production_countries': 13, 'release_date': 14,
                      "revenue": 15, 'duration': 16, 'spoken_languages': 17,
                      'tag_line': 19, 'title': 20,
                      'vote_average': 22, 'vote_count': 23}
rows = [list(row.__getitem__(i) for i in interested_columns.values()) for
        row in rows
        if len(row) > 23]

rows[0] = list(interested_columns.keys())
with open("filtered_movies.csv", "w") as output_file:
    writer = csv.writer(output_file)
    writer.writerows(rows)
