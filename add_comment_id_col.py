import pandas as pd

def comment_fix():
    df_comment = pd.read_csv("data/comments.csv")
    df_comment["comment_id"] = range(1, len(df_comment) + 1)
    cols = ["comment_id"] + [c for c in df_comment.columns if c != "comment_id"]
    df_comment = df_comment[cols]
    df_comment.to_csv("data/comments_fixed.csv", index=False)


if __name__ == "__main__":
    comment_fix()