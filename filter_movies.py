import csv

rows = []

with open("movies.csv") as input_file:
    for row in csv.reader(input_file):
        rows = rows + [row]

interested_columns = {'budget': 2, 'genres': 3, 'imdb_id': 6,
                      'original language': 7, 'overview': 9,
                      'popularity': 10, 'production companies': 12,
                      'production countries': 13, 'release date': 14,
                      "revenue": 15, 'duration': 16, 'spoken languages': 17,
                      'tagline': 19, 'title': 20, 'original title': 8,
                      'vote average': 22, 'vote count': 23}
rows = [list(row.__getitem__(i) for i in interested_columns.values()) for
        row in rows
        if len(row) > 23]

with open("filtered_movies.csv", "w") as output_file:
    writer = csv.writer(output_file)
    writer.writerows(rows)
