from users import generate_users
from friends import generate_friends
from groups import generate_groups
from posts import generate_posts_tags_photos
from comments import generate_comments
from activities import generate_activities

if __name__ == "__main__":
    print("Generating users...")
    generate_users()
    print("Generating friendships...")
    generate_friends()
    print("Generating groups...")
    generate_groups()
    print("Generating posts, tags, photos...")
    generate_posts_tags_photos()
    print("Generating comments...")
    generate_comments()
    print("Generating activities...")
    generate_activities()

    print("All done!")