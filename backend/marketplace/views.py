from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from krishisarthi.db import get_db
from bson import ObjectId
from accounts.utils import get_user_from_token
from datetime import datetime

from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated

class ProductListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request):
        category = request.query_params.get('category', 'All Categories')
        search = request.query_params.get('search', '')
        skip = int(request.query_params.get('skip', 0))
        limit = int(request.query_params.get('limit', 20))
        
        db = get_db()
        query = {"is_available": True}
        
        if category != 'All Categories':
            query['category'] = category
            
        if search:
            query['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
            
        products = []
        cursor = db["products"].find(query).sort("_id", -1).skip(skip).limit(limit)
        
        for product in cursor:
            product["id"] = str(product["_id"])
            del product["_id"]
            # Ensure seller_id is string
            if "seller_id" in product:
                product["seller_id"] = str(product["seller_id"])
            products.append(product)
            
        return Response(products)

    def post(self, request):
        db = get_db()
        data = request.data
        doc = {
            "name": data.get("name"),
            "description": data.get("description"),
            "price": data.get("price"),
            "category": data.get("category"),
            "image_url": data.get("image_url"),
            "seller_id": str(request.user["_id"]),
            "is_available": True,
        }
        
        result = db["products"].insert_one(doc)
        # Build response dict manually to avoid ObjectId serialization issues
        response_doc = {
            "id": str(result.inserted_id),
            "name": doc["name"],
            "description": doc["description"],
            "price": doc["price"],
            "category": doc["category"],
            "image_url": doc["image_url"],
            "seller_id": doc["seller_id"],
            "is_available": doc["is_available"],
        }
        
        return Response(response_doc, status=status.HTTP_201_CREATED)

class ProductDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, product_id):
        db = get_db()
        try:
            product = db["products"].find_one({"_id": ObjectId(product_id)})
        except:
            return Response({"detail": "Invalid product ID"}, status=status.HTTP_400_BAD_REQUEST)
            
        if not product:
            return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
            
        product["id"] = str(product["_id"])
        del product["_id"]
        return Response(product)


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        db = get_db()
        orders = list(db["orders"].find({"buyer_id": str(request.user["_id"])}).sort("created_at", -1))
        for order in orders:
            order["id"] = str(order["_id"])
            del order["_id"]
            # Convert datetime to string for JSON serialization
            if "created_at" in order and isinstance(order["created_at"], datetime):
                order["created_at"] = order["created_at"].isoformat()
        return Response(orders)

    def post(self, request):
        db = get_db()
        data = request.data
        product_id = data.get("product_id")
        quantity = int(data.get("quantity", 1))
        
        try:
            product = db["products"].find_one({"_id": ObjectId(product_id)})
            if not product:
                return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({"detail": "Invalid product ID"}, status=status.HTTP_400_BAD_REQUEST)
            
        total_price = float(product.get("price", 0)) * quantity
        
        order = {
            "product_id": str(product["_id"]),
            "product_name": product.get("name"),
            "product_image": product.get("image_url"),
            "buyer_id": str(request.user["_id"]),
            "seller_id": product.get("seller_id"),
            "quantity": quantity,
            "total_price": total_price,
            "status": "Pending",
            "created_at": datetime.utcnow()
        }
        
        result = db["orders"].insert_one(order)
        order["id"] = str(result.inserted_id)
        del order["_id"]
        order["created_at"] = order["created_at"].isoformat()
        
        # Log activity for the dashboard
        db["activity_log"].insert_one({
            "user_id": str(request.user["_id"]),
            "type": "marketplace_purchase",
            "message": f"Purchased {quantity}x {product.get('name')}",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return Response(order, status=status.HTTP_201_CREATED)
