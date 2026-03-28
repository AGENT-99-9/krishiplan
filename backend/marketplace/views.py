from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from krishisarthi.db import get_db
from bson import ObjectId
from accounts.utils import get_user_from_token
from datetime import datetime

from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated

from accounts.permissions import IsVendor, IsAdmin, IsVendorOrAdmin

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
        # Only vendors or admins can add products
        if request.user.get("role") not in ['vendor', 'admin']:
            return Response({"detail": "Only vendors can add products."}, status=status.HTTP_403_FORBIDDEN)
            
        db = get_db()
        data = request.data
        
        # Validate required fields
        name = data.get("name")
        price = data.get("price", 0)
        category = data.get("category")
        if not name or not category:
            return Response({"detail": "Product name and category are required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            price = float(price)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid price value."}, status=status.HTTP_400_BAD_REQUEST)
        
        doc = {
            "name": name,
            "description": data.get("description", ""),
            "price": price,
            "category": category,
            "image_url": data.get("image_url"),
            "seller_id": str(request.user["_id"]),
            "seller_name": request.user.get("full_name"),
            "is_available": True,
            "stock_quantity": int(data.get("stock_quantity", 0)),
            "created_at": datetime.utcnow()
        }
        
        result = db["products"].insert_one(doc)
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

class VendorInventoryView(APIView):
    permission_classes = [IsVendor]
    
    def get(self, request):
        db = get_db()
        products = list(db["products"].find({"seller_id": str(request.user["_id"])}).sort("_id", -1))
        for p in products:
            p["id"] = str(p["_id"])
            del p["_id"]
        return Response(products)

    def patch(self, request, product_id):
        """Update inventory stock or details."""
        db = get_db()
        data = request.data
        try:
            update_data = {}
            if "stock_quantity" in data: update_data["stock_quantity"] = int(data["stock_quantity"])
            if "price" in data: update_data["price"] = float(data["price"])
            if "is_available" in data: update_data["is_available"] = bool(data["is_available"])
            
            result = db["products"].update_one(
                {"_id": ObjectId(product_id), "seller_id": str(request.user["_id"])},
                {"$set": update_data}
            )
            if result.matched_count == 0:
                return Response({"detail": "Product not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"status": "updated"})
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, product_id):
        db = get_db()
        result = db["products"].delete_one({"_id": ObjectId(product_id), "seller_id": str(request.user["_id"])})
        if result.deleted_count == 0:
            return Response({"detail": "Product not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"status": "deleted"}, status=status.HTTP_204_NO_CONTENT)

class VendorAnalyticsView(APIView):
    permission_classes = [IsVendor]
    
    def get(self, request):
        db = get_db()
        seller_id = str(request.user["_id"])
        
        # Total Products
        total_products = db["products"].count_documents({"seller_id": seller_id})
        
        # Total Orders
        orders = list(db["orders"].find({"seller_id": seller_id}))
        total_orders = len(orders)
        
        # Total Revenue
        total_revenue = sum(order.get("total_price", 0) for order in orders)
        
        # Category breakdown
        pipeline = [
            {"$match": {"seller_id": seller_id}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]
        categories = list(db["products"].aggregate(pipeline))
        
        # Recent activity
        activities = list(db["activity_log"].find({"user_id": seller_id}).sort("timestamp", -1).limit(5))
        for a in activities:
            a["id"] = str(a["_id"])
            del a["_id"]

        return Response({
            "total_products": total_products,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "categories": [{"name": c["_id"], "count": c["count"]} for c in categories],
            "recent_activities": activities
        })

class VendorOrderListView(APIView):
    permission_classes = [IsVendor]
    def get(self, request):
        db = get_db()
        orders = list(db["orders"].find({"seller_id": str(request.user["_id"])}).sort("created_at", -1))
        for order in orders:
            order["id"] = str(order["_id"])
            del order["_id"]
            if "created_at" in order and isinstance(order["created_at"], datetime):
                order["created_at"] = order["created_at"].isoformat()
        return Response(orders)

    def patch(self, request, order_id):
        """Update order status, shipping info, or tracking."""
        db = get_db()
        data = request.data
        try:
            update_data = {}
            if "status" in data: update_data["status"] = data["status"]
            if "shipping_provider" in data: update_data["shipping_provider"] = data["shipping_provider"]
            if "tracking_id" in data: update_data["tracking_id"] = data["tracking_id"]
            
            result = db["orders"].update_one(
                {"_id": ObjectId(order_id), "seller_id": str(request.user["_id"])},
                {"$set": update_data}
            )
            if result.matched_count == 0:
                return Response({"detail": "Order not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)
            
            # Log activity
            db["activity_log"].insert_one({
                "user_id": str(request.user["_id"]),
                "type": "order_update",
                "message": f"Updated order {order_id} status to {data.get('status', 'updated')}",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return Response({"status": "updated"})
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, product_id):
        db = get_db()
        try:
            product = db["products"].find_one({"_id": ObjectId(product_id)})
        except Exception:
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
        if not product_id:
            return Response({"detail": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            quantity = int(data.get("quantity", 1))
            if quantity < 1:
                return Response({"detail": "Quantity must be at least 1"}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)
        buyer_id = str(request.user["_id"])
        
        try:
            product = db["products"].find_one({"_id": ObjectId(product_id)})
            if not product:
                return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({"detail": "Invalid product ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Security: Prevent self-purchase
        if product.get("seller_id") == buyer_id:
            return Response({"detail": "Vendors cannot purchase their own products"}, status=status.HTTP_403_FORBIDDEN)

        # Inventory check
        current_stock = product.get("stock_quantity", 0)
        if current_stock < quantity:
            return Response({"detail": f"Insufficient stock. Only {current_stock} units available."}, status=status.HTTP_400_BAD_REQUEST)
            
        total_price = float(product.get("price", 0)) * quantity
        
        order = {
            "product_id": str(product["_id"]),
            "product_name": product.get("name"),
            "product_image": product.get("image_url"),
            "buyer_id": buyer_id,
            "seller_id": product.get("seller_id"),
            "quantity": quantity,
            "total_price": total_price,
            "status": "Pending",
            "created_at": datetime.utcnow()
        }
        
        # Atomic stock decrement
        stock_updated = db["products"].update_one(
            {"_id": ObjectId(product_id), "stock_quantity": {"$gte": quantity}},
            {"$inc": {"stock_quantity": -quantity}}
        )

        if stock_updated.modified_count == 0:
            return Response({"detail": "Stock changed since last read, please try again."}, status=status.HTTP_409_CONFLICT)

        result = db["orders"].insert_one(order)
        order["id"] = str(result.inserted_id)
        del order["_id"]
        order["created_at"] = order["created_at"].isoformat()
        
        # Log activity for the dashboard
        db["activity_log"].insert_one({
            "user_id": buyer_id,
            "type": "marketplace_purchase",
            "message": f"Purchased {quantity}x {product.get('name')}",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return Response(order, status=status.HTTP_201_CREATED)
