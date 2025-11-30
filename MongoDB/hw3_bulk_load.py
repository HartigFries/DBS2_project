import csv
import json
import ast
from datetime import datetime

"""
Po spuštění tohoto skriptu spusťte následující příkazy pro import (s --drop):

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
    Converts a date string into the MongoDB Extended JSON Date format.
    """
    if date_str is None:
        return None

    date_str = str(date_str).strip()
    if not date_str:
        return None

    date_formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return {"$date": dt.strftime("%Y-%m-%dT%H:%M:%SZ")}
        except ValueError:
            continue
    return None


def open_prefer_fixed(base_name):
    """Helper: prefer ../<name>_fixed.csv, fall back to ../<name>.csv"""
    fixed = f"../{base_name}_fixed.csv"
    original = f"../{base_name}.csv"
    try:
        return open(fixed, "r", encoding="utf-8")
    except FileNotFoundError:
        return open(original, "r", encoding="utf-8")


# --- 0. Helper structures ---
post_to_group_map = {}  # Mapping post_id -> group_id

# --- 1. USERS ---
print("Processing Users...")
users = {}
comments_data_buffer = []  # Store raw comment rows to process later

with open('../users.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        user_id = int(row['user_id'])
        users[user_id] = {
            "_id": {"$oid": get_oid_string(user_id)},
            "user_id": user_id,
            "username": row['username'],
            "country": row['country'],
            "is_commercial": int(row.get('is_commercial', 0)),
            "join_date": format_date(row['join_date']),
            "joined_groups": [],
            "created_posts": [],
            "writes_comments": []
        }

# 1.1 Group Joins
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

# 1.2 User Shares Posts
with open_prefer_fixed('user_shares_posts') as f:
    reader = csv.DictReader(f)
    for row in reader:
        user_id = int(row['user_id'])
        post_id = int(row['post_id'])
        if user_id in users:
            users[user_id]["created_posts"].append({"$oid": get_oid_string(post_id)})

# 1.3 Comments (OPRAVA: Generujeme ID, protože v CSV chybí)
try:
    with open('../comments.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Použijeme enumerate, abychom vygenerovali ID od 1 výše
        for i, row in enumerate(reader, 1):
            # Přidáme vygenerované ID do řádku pro pozdější použití
            row['generated_id'] = i
            comments_data_buffer.append(row)

            # Link comment to user immediately
            user_id = int(row['user_id'])
            if user_id in users:
                users[user_id]["writes_comments"].append({"$oid": get_oid_string(i)})
except FileNotFoundError:
    print("Warning: comments.csv not found.")

with open('users.json', 'w', encoding='utf-8') as f:
    json.dump(list(users.values()), f, indent=4, ensure_ascii=False)

# --- 2. GROUPS ---
print("Processing Groups...")
groups = {}

with open('../groups.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        group_id = int(row['group_id'])
        groups[group_id] = {
            "_id": {"$oid": get_oid_string(group_id)},
            "group_id": group_id,
            "name": row['group_name'],
            "posts": [],
            "last_activity": {"$date": "1970-01-01T00:00:00Z"}
        }

# 2.1 Post in Group
try:
    with open_prefer_fixed('post_in_group') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_group_id = row['group_id'].strip("[]")
            clean_post_id = row['post_id'].strip("[]")

            if clean_group_id and clean_post_id:
                gid = int(clean_group_id)
                pid = int(clean_post_id)

                post_to_group_map[pid] = gid

                if gid in groups:
                    post_oid = {"$oid": get_oid_string(pid)}
                    if post_oid not in groups[gid]["posts"]:
                        groups[gid]["posts"].append(post_oid)
except FileNotFoundError:
    pass

# 2.2 Update last_activity
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

# --- 3. POSTS ---
print("Processing Posts...")
posts = {}

with open('../posts.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        post_id = int(row['post_id'])

        aid = int(float(row['activity_id'])) if row['activity_id'] else None
        activity_ref = {"$oid": get_oid_string(aid)} if aid is not None else None
        gid = post_to_group_map.get(post_id)
        group_ref = {"$oid": get_oid_string(gid)} if gid is not None else None

        posts[post_id] = {
            "_id": {"$oid": get_oid_string(post_id)},
            "activity": activity_ref,
            "group": group_ref,
            "created_at": None,
            "user": None,
            "tags": []
        }

# 3.1 Enrich Posts
with open_prefer_fixed('user_shares_posts') as f:
    reader = csv.DictReader(f)
    for row in reader:
        post_id = int(row['post_id'])
        if post_id in posts:
            posts[post_id]["created_at"] = format_date(row['created_at'])

            uid = int(row['user_id'])
            posts[post_id]["user"] = {"$oid": get_oid_string(uid)}

            tags_raw = row.get('tags', '[]')
            try:
                tag_list = ast.literal_eval(tags_raw)
                if isinstance(tag_list, list):
                    for tag_uid in tag_list:
                        posts[post_id]["tags"].append({"$oid": get_oid_string(int(tag_uid))})
            except (ValueError, SyntaxError):
                pass

valid_posts = [p for p in posts.values() if p["created_at"] is not None]

with open('posts.json', 'w', encoding='utf-8') as f:
    json.dump(valid_posts, f, indent=4, ensure_ascii=False)

# --- 4. ACTIVITIES ---
print("Processing Activities...")
activities = []
country_map = {"Czech Republic": "cz", "Germany": "de", "Poland": "pl", "United States": "us"}

with open('../activities.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        activity_id = int(row['activity_id'])
        country_code = country_map.get(row['country'], row['country'])

        activities.append({
            "_id": {"$oid": get_oid_string(activity_id)},
            "activity_id": activity_id,
            "region": row['region'],
            "country": country_code,
            "distance_m": float(row['distance_m']),
            "base_elev_m": float(row['base_elev_m']),
            "total_elev_m": float(row['total_elev_m'])
        })

with open('activities.json', 'w', encoding='utf-8') as f:
    json.dump(activities, f, indent=4, ensure_ascii=False)

# --- 5. COMMENTS ---
print("Processing Comments...")
comments = []

for row in comments_data_buffer:
    # OPRAVA: Používáme vygenerované ID z kroku 1.3
    comment_id = row['generated_id']

    uid = int(row['user_id'])
    pid = int(row['post_id'])
    content = row.get('content', '')

    comment_doc = {
        "_id": {"$oid": get_oid_string(comment_id)},
        "written_at": format_date(row['written_at']),
        "user_id": {"$oid": get_oid_string(uid)},
        "post_id": {"$oid": get_oid_string(pid)},
        "content": content
    }
    comments.append(comment_doc)

with open('comments.json', 'w', encoding='utf-8') as f:
    json.dump(comments, f, indent=4, ensure_ascii=False)

print("Done! JSON files generated.")