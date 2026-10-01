import csv
import random
import os

negative = [
    ("This product broke after 2 days. Terrible quality.", 1),
    ("Waste of money. Doesn't work as advertised.", 1),
    ("Very disappointed with this purchase.", 1),
    ("Poor customer service and bad product.", 1),
    ("Do not buy this! Total garbage.", 1),
    ("It stopped working completely.", 1),
    ("The worst electronics I have ever bought.", 1),
    ("Arrived damaged and doesn't turn on.", 1),
    ("Horrible quality, feels very cheap.", 2),
    ("Not worth the price tag at all.", 2),
    ("It barely works, very frustrating.", 2),
    ("I regret buying this, it's pretty bad.", 2)
] * 10

neutral = [
    ("It's okay, nothing special.", 3),
    ("Average product, does the job.", 3),
    ("Acceptable quality for the price.", 3),
    ("It works fine, but could be better.", 3),
    ("Not bad, but not great either.", 3),
    ("Meh, it serves its purpose.", 3),
    ("Decent purchase, matches description.", 3),
    ("Just an ordinary item, no complaints.", 3),
    ("It's fine, I guess.", 3),
    ("Average quality, okay value.", 3)
] * 12

positive = [
    ("Love this product! Excellent quality.", 5),
    ("Works perfectly, highly recommend.", 5),
    ("Great value for money.", 5),
    ("Amazing! Best purchase I've made.", 5),
    ("Very happy with this, exceeds expectations.", 5),
    ("Fantastic quality and fast shipping.", 5),
    ("Absolutely perfect, exactly what I needed.", 5),
    ("Really good product, I use it daily.", 4),
    ("Solid build quality and works well.", 4),
    ("Great design and very functional.", 4),
    ("Very satisfied, it does everything promised.", 4),
    ("Good item, glad I bought it.", 4)
] * 10

all_reviews = negative + neutral + positive
random.shuffle(all_reviews)

backend_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(backend_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

csv_path = os.path.join(data_dir, 'reviews.csv')
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['review', 'rating'])
    for r, rating in all_reviews:
        writer.writerow([r, rating])
