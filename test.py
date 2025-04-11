from flask import Flask, jsonify, request
import requests
from functools import lru_cache

app = Flask(__name__)

BASE_URL="http://20.244.56.144/evaluation-service"

AUTH_HEADERS = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzQ0MzgzNzkyLCJpYXQiOjE3NDQzODM0OTIsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6IjVhYmZlMWE5LTJlYzctNDczYS05ZGRiLTA1NjNlYjU3NzhjMyIsInN1YiI6ImFrYXNoc2hlbnZpOTNAZ21haWwuY29tIn0sImVtYWlsIjoiYWthc2hzaGVudmk5M0BnbWFpbC5jb20iLCJuYW1lIjoiYWthc2ggZCBzaGVudmkiLCJyb2xsTm8iOiI0Y2IyMmNzMDA1IiwiYWNjZXNzQ29kZSI6Im5aWURxSCIsImNsaWVudElEIjoiNWFiZmUxYTktMmVjNy00NzNhLTlkZGItMDU2M2ViNTc3OGMzIiwiY2xpZW50U2VjcmV0IjoidFp4ZFBldHhjZ1d6V3dEVCJ9.noC0S81qVS1EpMJpPi1hok5BSwHYS8SuB3KnSs2Hz3g"
}


@lru_cache(maxsize=None)
def get_users():
    res = requests.get(f"{BASE_URL}/users", headers=AUTH_HEADERS)
    print("get_users() response:", res.json())
    return res.json().get("users", {})  


@lru_cache(maxsize=None)
def get_user_posts(user_id):
    res = requests.get(f"{BASE_URL}/users/{user_id}/posts", headers=AUTH_HEADERS)
    data = res.json()
    if isinstance(data, dict) and "posts" in data:
        return data["posts"]  
    elif isinstance(data, list):
        return data  
    return []


@lru_cache(maxsize=None)
def get_post_comments(post_id):
    res = requests.get(f"{BASE_URL}/posts/{post_id}/comments", headers=AUTH_HEADERS)
    data = res.json()
    if isinstance(data, dict) and "comments" in data:
        return data["comments"]
    elif isinstance(data, list):
        return data
    return []


@app.route("/users", methods=["GET"])
def top_users():
    users = get_users()  
    user_comment_count = []

    for user_id, user_name in users.items():
        posts = get_user_posts(user_id)
        total_comments = 0

        for post in posts:
            if isinstance(post, dict):  
                post_id = post.get("id")
                if post_id:
                    comments = get_post_comments(post_id)
                    total_comments += len(comments)

        user_comment_count.append({
            "id": user_id,
            "name": user_name,
            "total_comments": total_comments
        })

    top_users = sorted(user_comment_count, key=lambda x: x["total_comments"], reverse=True)[:5]
    return jsonify(top_users), 200


@app.route("/posts", methods=["GET"])
def posts():
    post_type = request.args.get("type")

    if post_type not in ["popular", "latest"]:
        return jsonify({"error": "Invalid type. Use 'popular' or 'latest'."}), 400

    all_posts = []
    users = get_users()

    for user_id in users.keys():
        all_posts.extend(get_user_posts(user_id))

    if post_type == "popular":
        max_comments = 0
        popular_posts = []

        for post in all_posts:
            post_id = post.get("id")
            comments = get_post_comments(post_id)
            comment_count = len(comments)

            if comment_count > max_comments:
                max_comments = comment_count
                popular_posts = [post]
            elif comment_count == max_comments:
                popular_posts.append(post)

        return jsonify({"popular_posts": popular_posts}), 200

    elif post_type == "latest":
        latest_posts = sorted(all_posts, key=lambda x: x.get("timestamp", ""), reverse=True)[:5]
        return jsonify({"latest_posts": latest_posts}), 200


if __name__ == "__main__":
    app.run(debug=True)
