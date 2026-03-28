from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from krishisarthi.db import get_db
from bson.objectid import ObjectId

class AdminBaseView(APIView):
    def check_admin(self, request):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated or user.get('role') != 'admin':
            return False
        return True

class AdminStatsView(AdminBaseView):
    def get(self, request):
        if not self.check_admin(request):
            return Response({"error": "Admin only"}, status=status.HTTP_403_FORBIDDEN)
        
        db = get_db()
        return Response({
            "users": db["users"].count_documents({}),
            "products": db["products"].count_documents({}),
            "orders": db["orders"].count_documents({}),
            "posts": db["community_posts"].count_documents({}),
            "revenue": sum(o.get('total_price', 0) for o in db["orders"].find({"status": "Delivered"}))
        })

class AdminUsersView(AdminBaseView):
    def get(self, request):
        if not self.check_admin(request): return Response(status=403)
        db = get_db()
        users = []
        for u in db["users"].find():
            users.append({
                "id": str(u["_id"]),
                "username": u.get("username"),
                "email": u.get("email"),
                "role": u.get("role"),
                "full_name": u.get("full_name")
            })
        return Response(users)
        
    def delete(self, request, pk):
        if not self.check_admin(request): return Response(status=403)
        db = get_db()
        db["users"].delete_one({"_id": ObjectId(pk)})
        return Response({"status": "deleted"})

class AdminProductsView(AdminBaseView):
    def get(self, request):
        if not self.check_admin(request): return Response(status=403)
        db = get_db()
        products = []
        for p in db["products"].find():
            products.append({
                "id": str(p["_id"]),
                "name": p.get("name"),
                "category": p.get("category"),
                "price": p.get("price"),
                "stock": p.get("stock_quantity")
            })
        return Response(products)
        
    def delete(self, request, pk):
        if not self.check_admin(request): return Response(status=403)
        db = get_db()
        db["products"].delete_one({"_id": ObjectId(pk)})
        return Response({"status": "deleted"})
        
class AdminPostsView(AdminBaseView):
    def get(self, request):
        if not self.check_admin(request): return Response(status=403)
        db = get_db()
        posts = []
        for p in db["community_posts"].find():
            posts.append({
                "id": str(p["_id"]),
                "title": p.get("title"),
                "author": p.get("author_name"),
                "category": p.get("category"),
                "likes": len(p.get("likes", []))
            })
        return Response(posts)
        
    def delete(self, request, pk):
        if not self.check_admin(request): return Response(status=403)
        db = get_db()
        db["community_posts"].delete_one({"_id": ObjectId(pk)})
        return Response({"status": "deleted"})
