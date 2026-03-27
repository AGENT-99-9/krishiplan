from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from krishisarthi.db import get_db
from bson import ObjectId
from datetime import datetime
from rest_framework.permissions import AllowAny, IsAuthenticated

class PingView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"message": "Community app is reachable"})

class PostListView(APIView):
    authentication_classes = [] # Disable default auth for public listing
    permission_classes = [AllowAny]
    def get(self, request):
        db = get_db()
        category = request.query_params.get('category', 'All Discussions')
        search = request.query_params.get('search', '')
        
        query = {}
        if category != 'All Discussions':
            query['category'] = category
        if search:
            query['$or'] = [
                {'title': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]

        cursor = db["community_posts"].find(query).sort("created_at", -1)
        posts = []
        for doc in cursor:
            posts.append({
                "id": str(doc["_id"]),
                "title": doc.get("title", ""),
                "description": doc.get("description", ""),
                "category": doc.get("category", "All Discussions"),
                "author_id": str(doc.get("author_id", "")),
                "author_name": doc.get("author_name", "Anonymous"),
                "likes": doc.get("likes", []),
                "like_count": len(doc.get("likes", [])),
                "comments": doc.get("comments", []),
                "comment_count": len(doc.get("comments", [])),
                "created_at": doc.get("created_at", datetime.utcnow()).isoformat()
            })
        return Response(posts)

class PostCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        db = get_db()
        data = request.data
        user_id = str(request.user["_id"])
        
        title = data.get("title")
        if not title:
            return Response({"detail": "Title is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        new_post = {
            "title": title,
            "description": data.get("description", ""),
            "category": data.get("category", "All Discussions"),
            "author_id": user_id,
            "author_name": request.user.get("full_name") or request.user.get("username") or "Anonymous",
            "likes": [],
            "comments": [],
            "created_at": datetime.utcnow()
        }
        result = db["community_posts"].insert_one(new_post)
        new_post["id"] = str(result.inserted_id)
        new_post["author_id"] = str(new_post["author_id"])
        new_post["created_at"] = new_post["created_at"].isoformat()
        del new_post["_id"]
        
        # Log activity for dashboard feed
        try:
            db["activity_log"].insert_one({
                "user_id": user_id,
                "type": "community_post",
                "message": f"Started a discussion: \"{title[:60]}{'...' if len(title) > 60 else ''}\"",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception:
            pass
        
        return Response(new_post, status=status.HTTP_201_CREATED)

class PostLikeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, post_id):
        db = get_db()
        user_id = str(request.user["_id"])
        post = db["community_posts"].find_one({"_id": ObjectId(post_id)})
        if not post:
            return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        
        likes = post.get("likes", [])
        if user_id in likes:
            likes.remove(user_id)
        else:
            likes.append(user_id)
        
        db["community_posts"].update_one(
            {"_id": ObjectId(post_id)},
            {"$set": {"likes": likes}}
        )
        return Response({"likes": len(likes), "is_liked": user_id in likes})

class PostCommentView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, post_id):
        db = get_db()
        comment_text = request.data.get("comment")
        if not comment_text:
            return Response({"detail": "Comment text required"}, status=status.HTTP_400_BAD_REQUEST)
        
        comment = {
            "id": str(ObjectId()),
            "user_id": str(request.user["_id"]),
            "user_name": request.user.get("full_name") or request.user.get("username"),
            "text": comment_text,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = db["community_posts"].update_one(
            {"_id": ObjectId(post_id)},
            {"$push": {"comments": comment}}
        )
        if result.matched_count == 0:
            return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(comment, status=status.HTTP_201_CREATED)

class TrendingTopicsView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def get(self, request):
        db = get_db()
        pipeline = [
            {"$project": {
                "title": 1,
                "comment_count": {"$size": {"$ifNull": ["$comments", []]}}
            }},
            {"$sort": {"comment_count": -1}},
            {"$limit": 5}
        ]
        cursor = db["community_posts"].aggregate(pipeline)
        trending = []
        for doc in cursor:
            trending.append({
                "id": str(doc["_id"]),
                "title": doc.get("title", ""),
                "reply_count": doc.get("comment_count", 0)
            })
        return Response(trending)

class TopContributorsView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def get(self, request):
        db = get_db()
        cursor = db["users"].find({}).sort("points", -1).limit(5)
        contributors = []
        for doc in cursor:
            contributors.append({
                "username": doc.get("username", "Anonymous"),
                "full_name": doc.get("full_name", ""),
                "role": doc.get("role", "Farmer"),
                "points": doc.get("points", 0)
            })
        return Response(contributors)
