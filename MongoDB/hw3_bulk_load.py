import csv
import json
from datetime import datetime
"""
After creating json files, we imported the data into mongodb using these commands:

mongoimport --port 42222 -u LOGIN -p PASSWORD -d LOGIN --collection users --file users.json --jsonArray --drop
mongoimport --port 42222 -u LOGIN -p PASSWORD -d LOGIN --collection groups --file groups.json --jsonArray --drop
mongoimport --port 42222 -u LOGIN -p PASSWORD -d LOGIN --collection posts --file posts.json --jsonArray --drop
mongoimport --port 42222 -u LOGIN -p PASSWORD -d LOGIN --collection activities --file activities.json --jsonArray --drop
mongoimport --port 42222 -u LOGIN -p PASSWORD -d LOGIN --collection comments --file comments.json --jsonArray --drop
"""

def get_oid_string(int_id):
    """Generates a deterministic 24-char hex string to simulate ObjectId."""
    if int_id is None:
        return None
    return f"{int_id:024x}"


def format_date(date_str):
    """
    Converts a date string into the MongoDB Extended JSON Date format: {"$date": "..."}
    """
    date_formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return {"$date": dt.strftime("%Y-%m-%dT%H:%M:%SZ")}
        except ValueError:
            continue
    return None


# 1. users.json
users = {}
comments_data_for_users = []

with open('../users.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        user_id = int(row['user_id'])
        users[user_id] = {
            "_id": {"$oid": get_oid_string(user_id)},
            "username": row['username'],
            "country": row['country'],
            "join_date": format_date(row['join_date']),
            "joined_groups": [],
            "created_posts": [],
            "writes_comments": []
        }

# 1.1 Process group_joins.csv
with open('../group_joins.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        user_id = int(row['user_id'])
        group_id = int(row['group_id'])
        if user_id in users:
            users[user_id]["joined_groups"].append({
                "group_id": {"$oid": get_oid_string(group_id)},
                "joined_at": format_date(row['join_date'])
            })

# 1.2 Process user_shares_posts.csv
with open('../user_shares_posts.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        user_id = int(row['user_id'])
        post_id = int(row['post_id'])
        if user_id in users:
            users[user_id]["created_posts"].append({"$oid": get_oid_string(post_id)})

# 1.3 Process comments.csv to populate writes_comments
try:
    with open('../comments.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            comment_id = int(row['comment_id'])
            user_id = int(row['user_id'])

            comments_data_for_users.append(row)

            if user_id in users:
                users[user_id]["writes_comments"].append({"$oid": get_oid_string(comment_id)})
except FileNotFoundError:
    print("Warning: comments.csv not found. 'writes_comments' field will be empty.")
    pass

with open('users.json', 'w', encoding='utf-8') as f:
    json.dump(list(users.values()), f, indent=4, ensure_ascii=False)

# 2. groups.json
groups = {}

with open('../groups.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        group_id = int(row['group_id'])
        groups[group_id] = {
            "_id": {"$oid": get_oid_string(group_id)},
            "name": row['group_name'],
            "posts": [],
            "last_activity": {"$date": "1970-01-01T00:00:00Z"}
        }

if 0 not in groups:
    groups[0] = {
        "_id": {"$oid": "000000000000000000000000"},
        "name": "Main Page (Default)",
        "posts": [],
        "last_activity": {"$date": "2023-01-01T00:00:00Z"}
    }

try:
    with open('../post_in_group.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_group_id = row['group_id'].strip("[]")
            clean_post_id = row['post_id'].strip("[]")

            if clean_group_id and clean_post_id:
                gid = int(clean_group_id)
                pid = int(clean_post_id)
                if gid in groups:
                    post_oid = {"$oid": get_oid_string(pid)}
                    if post_oid not in groups[gid]["posts"]:
                        groups[gid]["posts"].append(post_oid)
except FileNotFoundError:
    pass

with open('../group_joins.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        group_id = int(row['group_id'])
        if group_id in groups:
            join_date_iso = format_date(row['join_date'])
            if join_date_iso and join_date_iso["$date"] > groups[group_id]["last_activity"]["$date"]:
                groups[group_id]["last_activity"] = join_date_iso

with open('groups.json', 'w', encoding='utf-8') as f:
    json.dump(list(groups.values()), f, indent=4, ensure_ascii=False)

# 3. posts.json
posts = {}

with open('../posts.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        post_id = int(row['post_id'])
        aid = int(float(row['activity_id'])) if row['activity_id'] else None

        activity_ref = {"$oid": get_oid_string(aid)} if aid is not None else None

        posts[post_id] = {
            "_id": {"$oid": get_oid_string(post_id)},
            "activity": activity_ref,
            "created_at": None
        }

with open('../user_shares_posts.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        post_id = int(row['post_id'])
        if post_id in posts:
            posts[post_id]["created_at"] = format_date(row['created_at'])

valid_posts = [p for p in posts.values() if p["created_at"] is not None]

with open('posts.json', 'w', encoding='utf-8') as f:
    json.dump(valid_posts, f, indent=4, ensure_ascii=False)

# 4. activities.json
activities = []

country_map = {
    "Czech Republic": "cz", "Germany": "de",
    "Poland": "pl", "United States": "us"
}

with open('../activities.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        activity_id = int(row['activity_id'])
        raw_country = row['country']
        clean_country = country_map.get(raw_country, raw_country)

        activities.append({
            "_id": {"$oid": get_oid_string(activity_id)},
            "region": row['region'],
            "distance_m": float(row['distance_m']),
            "country": clean_country
        })

with open('activities.json', 'w', encoding='utf-8') as f:
    json.dump(activities, f, indent=4, ensure_ascii=False)

# 5. comments.json
comments = []

for row in comments_data_for_users:
    comment_id = int(row['comment_id'])

    comment_doc = {
        "_id": {"$oid": get_oid_string(comment_id)},
        "written_at": format_date(row['written_at'])
    }

    comments.append(comment_doc)

with open('comments.json', 'w', encoding='utf-8') as f:
    json.dump(comments, f, indent=4, ensure_ascii=False)