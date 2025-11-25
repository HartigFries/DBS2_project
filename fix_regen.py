import pandas as pd

def user_shares_posts_regen():
    df_posts = pd.read_csv("data/user_shares_posts.csv")
    df_posts = df_posts.drop(columns=["group_id"], errors="ignore")
    df_posts.to_csv("data/user_shares_posts_fixed.csv", index=False)


def post_in_group():
    df_up = pd.read_csv("data/user_shares_posts.csv")    
    df_posts = pd.read_csv("data/post_in_group.csv") 

    # Ensure df_posts has the post_id column
    if "post_id" not in df_posts.columns:
        df_posts["post_id"] = pd.NA

    # Left-join template containing all post_ids
    df_fixed = (
        pd.DataFrame({"post_id": df_up["post_id"].unique()})
        .merge(df_posts, on="post_id", how="left")
    )

    # Replace missing group_id with 0
    df_fixed.loc[df_fixed["group_id"].isna(), "group_id"] = "[0]"

    df_fixed.to_csv("data/post_in_group_fixed.csv", index=False)


if __name__ == "__main__":
    user_shares_posts_regen()
    post_in_group()