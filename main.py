from fastapi import FastAPI, HTTPException, Query, Path
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
import re

app = FastAPI(title="E-commerce Products API", version="1.0.0")

# MongoDB connection
MONGODB_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGODB_URL)
db = client.ecommerce_db
products_collection = db.products
orders_collection = db.orders

# Pydantic models
class Size(BaseModel):
    size: str
    quantity: int

class ProductCreate(BaseModel):
    name: str
    price: float
    sizes: List[Size]

class ProductResponse(BaseModel):
    id: str

class ProductListItem(BaseModel):
    id: str
    name: str
    price: float

class PaginationInfo(BaseModel):
    next: Optional[str] = None
    limit: int
    previous: Optional[int] = None

class ProductListResponse(BaseModel):
    data: List[ProductListItem]
    page: PaginationInfo

# Order models
class OrderItem(BaseModel):
    productId: str
    qty: int

class OrderCreate(BaseModel):
    userId: str
    items: List[OrderItem]

class OrderResponse(BaseModel):
    id: str

class ProductDetails(BaseModel):
    name: str
    id: str

class OrderItemWithDetails(BaseModel):
    productDetails: ProductDetails
    qty: int

class OrderListItem(BaseModel):
    id: str
    items: List[OrderItemWithDetails]
    total: float

class OrderListResponse(BaseModel):
    data: List[OrderListItem]
    page: PaginationInfo

@app.on_event("startup")
async def startup_db_client():
    await client.admin.command('ping')
    print("Connected to MongoDB!")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

@app.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate):
    """
    Create a new product in the e-commerce system.
    
    Args:
        product: Product data including name, price, and sizes
        
    Returns:
        ProductResponse: Contains the unique ID of the created product
        
    Raises:
        HTTPException: If there's an error creating the product
    """
    try:
        # Generate unique ID
        product_id = str(uuid.uuid4())
        
        # Prepare product document for MongoDB
        product_doc = {
            "id": product_id,
            "name": product.name,
            "price": product.price,
            "sizes": [size.dict() for size in product.sizes],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert product into MongoDB
        await products_collection.insert_one(product_doc)
        
        return ProductResponse(id=product_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")

@app.get("/products", response_model=ProductListResponse)
async def list_products(
    name: Optional[str] = Query(None, description="Filter by product name (supports regex or partial search)"),
    size: Optional[str] = Query(None, description="Filter for products that have a specific size"),
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip")
):
    """
    List products with filtering and pagination support.
    
    Args:
        name: Optional filter by product name (supports regex or partial search)
        size: Optional filter for products that have a specific size
        limit: Number of products to return (1-100, default: 10)
        offset: Number of products to skip for pagination (default: 0)
        
    Returns:
        ProductListResponse: Contains list of products and pagination info
    """
    try:
        # Build filter query
        filter_query = {}
        
        # Name filter (supports regex or partial search)
        if name:
            # Try regex first, if it fails, use case-insensitive partial match
            try:
                filter_query["name"] = {"$regex": name, "$options": "i"}
            except re.error:
                # If regex is invalid, use simple partial match
                filter_query["name"] = {"$regex": re.escape(name), "$options": "i"}
        
        # Size filter
        if size:
            filter_query["sizes.size"] = size
        
        # Get total count for pagination
        total_count = await products_collection.count_documents(filter_query)
        
        # Get products with pagination (sorted by _id as specified)
        cursor = products_collection.find(filter_query).skip(offset).limit(limit).sort("_id", 1)
        
        products = []
        async for product in cursor:
            products.append(ProductListItem(
                id=product["id"],
                name=product["name"],
                price=product["price"]
            ))
        
        # Calculate pagination info
        next_offset = offset + limit if offset + limit < total_count else None
        previous_offset = offset - limit if offset > 0 else None
        
        pagination = PaginationInfo(
            next=str(next_offset) if next_offset is not None else None,
            limit=len(products),
            previous=previous_offset if previous_offset is not None else None
        )
        
        return ProductListResponse(data=products, page=pagination)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing products: {str(e)}")

@app.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(order: OrderCreate):
    """
    Create a new order in the e-commerce system.
    
    Args:
        order: Order data including userId and items
        
    Returns:
        OrderResponse: Contains the unique ID of the created order
        
    Raises:
        HTTPException: If there's an error creating the order or invalid product IDs
    """
    try:
        # Validate that all products exist
        product_ids = [item.productId for item in order.items]
        existing_products = await products_collection.find({"id": {"$in": product_ids}}).to_list(length=None)
        
        if len(existing_products) != len(product_ids):
            existing_ids = [p["id"] for p in existing_products]
            missing_ids = [pid for pid in product_ids if pid not in existing_ids]
            raise HTTPException(status_code=400, detail=f"Products not found: {missing_ids}")
        
        # Generate unique order ID
        order_id = str(uuid.uuid4())
        
        # Calculate total order value
        total = 0
        for item in order.items:
            product = next(p for p in existing_products if p["id"] == item.productId)
            total += product["price"] * item.qty
        
        # Prepare order document for MongoDB
        order_doc = {
            "id": order_id,
            "userId": order.userId,
            "items": [item.dict() for item in order.items],
            "total": total,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert order into MongoDB
        await orders_collection.insert_one(order_doc)
        
        return OrderResponse(id=order_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")

@app.get("/orders/{user_id}", response_model=OrderListResponse)
async def list_orders(
    user_id: str = Path(..., description="User ID to get orders for"),
    limit: int = Query(10, ge=1, le=100, description="Number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip")
):
    """
    List orders for a specific user with pagination support.
    
    Args:
        user_id: User ID to get orders for
        limit: Number of orders to return (1-100, default: 10)
        offset: Number of orders to skip for pagination (default: 0)
        
    Returns:
        OrderListResponse: Contains list of orders with product details and pagination info
    """
    try:
        # Build filter query for user's orders
        filter_query = {"userId": user_id}
        
        # Get total count for pagination
        total_count = await orders_collection.count_documents(filter_query)
        
        # Get orders with pagination (sorted by _id as specified)
        cursor = orders_collection.find(filter_query).skip(offset).limit(limit).sort("_id", 1)
        
        orders = []
        async for order in cursor:
            # Get product details for each item in the order
            order_items = []
            for item in order["items"]:
                # Look up product details
                product = await products_collection.find_one({"id": item["productId"]})
                if product:
                    product_details = ProductDetails(
                        name=product["name"],
                        id=product["id"]
                    )
                    order_items.append(OrderItemWithDetails(
                        productDetails=product_details,
                        qty=item["qty"]
                    ))
            
            orders.append(OrderListItem(
                id=order["id"],
                items=order_items,
                total=order["total"]
            ))
        
        # Calculate pagination info
        next_offset = offset + limit if offset + limit < total_count else None
        previous_offset = offset - limit if offset > 0 else None
        
        pagination = PaginationInfo(
            next=str(next_offset) if next_offset is not None else None,
            limit=len(orders),
            previous=previous_offset if previous_offset is not None else None
        )
        
        return OrderListResponse(data=orders, page=pagination)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing orders: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "E-commerce Products API",
        "version": "1.0.0",
        "endpoints": {
            "create_product": "POST /products",
            "list_products": "GET /products",
            "create_order": "POST /orders",
            "list_orders": "GET /orders/{user_id}",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        await client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 