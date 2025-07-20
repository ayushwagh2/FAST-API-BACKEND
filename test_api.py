import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_root_endpoint():
    """Test the root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_create_product():
    """Test the create product endpoint"""
    print("Testing create product...")
    
    # Sample product data
    product_data = {
        "name": "Nike Air Max 270",
        "price": 129.99,
        "sizes": [
            {
                "size": "US 7",
                "quantity": 10
            },
            {
                "size": "US 8",
                "quantity": 15
            },
            {
                "size": "US 9",
                "quantity": 8
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/products",
        json=product_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)
    
    return response.json().get("id") if response.status_code == 201 else None

def test_create_product_invalid_data():
    """Test the create product endpoint with invalid data"""
    print("Testing create product with invalid data...")
    
    # Invalid product data (missing required fields)
    invalid_product_data = {
        "name": "Test Product"
        # Missing price and sizes
    }
    
    response = requests.post(
        f"{BASE_URL}/products",
        json=invalid_product_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_list_products():
    """Test the list products endpoint"""
    print("Testing list products...")
    
    response = requests.get(f"{BASE_URL}/products")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_list_products_with_pagination():
    """Test the list products endpoint with pagination"""
    print("Testing list products with pagination...")
    
    response = requests.get(f"{BASE_URL}/products?limit=2&offset=0")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_list_products_with_name_filter():
    """Test the list products endpoint with name filter"""
    print("Testing list products with name filter...")
    
    response = requests.get(f"{BASE_URL}/products?name=Nike")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_list_products_with_size_filter():
    """Test the list products endpoint with size filter"""
    print("Testing list products with size filter...")
    
    response = requests.get(f"{BASE_URL}/products?size=US 7")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_list_products_with_combined_filters():
    """Test the list products endpoint with combined filters"""
    print("Testing list products with combined filters...")
    
    response = requests.get(f"{BASE_URL}/products?name=Nike&size=US 8&limit=5")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def create_sample_products():
    """Create multiple sample products for testing"""
    print("Creating sample products for testing...")
    
    sample_products = [
        {
            "name": "Adidas Ultraboost",
            "price": 179.99,
            "sizes": [
                {"size": "US 8", "quantity": 12},
                {"size": "US 9", "quantity": 8}
            ]
        },
        {
            "name": "Puma RS-X",
            "price": 89.99,
            "sizes": [
                {"size": "US 7", "quantity": 5},
                {"size": "US 8", "quantity": 10}
            ]
        },
        {
            "name": "Nike Zoom Fly",
            "price": 159.99,
            "sizes": [
                {"size": "US 9", "quantity": 6},
                {"size": "US 10", "quantity": 4}
            ]
        }
    ]
    
    created_ids = []
    for product in sample_products:
        response = requests.post(
            f"{BASE_URL}/products",
            json=product,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 201:
            created_ids.append(response.json().get("id"))
            print(f"Created product: {product['name']}")
    
    print(f"Created {len(created_ids)} sample products")
    print("-" * 50)
    return created_ids

def test_create_order(product_ids):
    """Test the create order endpoint"""
    print("Testing create order...")
    
    if not product_ids:
        print("No product IDs available for order creation")
        return None
    
    # Sample order data
    order_data = {
        "userId": "user_1",
        "items": [
            {
                "productId": product_ids[0],
                "qty": 2
            },
            {
                "productId": product_ids[1] if len(product_ids) > 1 else product_ids[0],
                "qty": 1
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/orders",
        json=order_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)
    
    return response.json().get("id") if response.status_code == 201 else None

def test_create_order_invalid_product():
    """Test the create order endpoint with invalid product ID"""
    print("Testing create order with invalid product ID...")
    
    order_data = {
        "userId": "user_1",
        "items": [
            {
                "productId": "invalid_product_id",
                "qty": 1
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/orders",
        json=order_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_create_order_invalid_data():
    """Test the create order endpoint with invalid data"""
    print("Testing create order with invalid data...")
    
    # Invalid order data (missing required fields)
    invalid_order_data = {
        "userId": "user_1"
        # Missing items
    }
    
    response = requests.post(
        f"{BASE_URL}/orders",
        json=invalid_order_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_list_orders():
    """Test the list orders endpoint"""
    print("Testing list orders...")
    
    response = requests.get(f"{BASE_URL}/orders/user_1")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_list_orders_with_pagination():
    """Test the list orders endpoint with pagination"""
    print("Testing list orders with pagination...")
    
    response = requests.get(f"{BASE_URL}/orders/user_1?limit=2&offset=0")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_list_orders_nonexistent_user():
    """Test the list orders endpoint for a user with no orders"""
    print("Testing list orders for nonexistent user...")
    
    response = requests.get(f"{BASE_URL}/orders/nonexistent_user")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def create_multiple_orders(product_ids):
    """Create multiple orders for testing"""
    print("Creating multiple orders for testing...")
    
    if not product_ids:
        print("No product IDs available for order creation")
        return []
    
    orders_data = [
        {
            "userId": "user_1",
            "items": [
                {"productId": product_ids[0], "qty": 1}
            ]
        },
        {
            "userId": "user_1",
            "items": [
                {"productId": product_ids[0], "qty": 2},
                {"productId": product_ids[1] if len(product_ids) > 1 else product_ids[0], "qty": 1}
            ]
        },
        {
            "userId": "user_2",
            "items": [
                {"productId": product_ids[0], "qty": 3}
            ]
        }
    ]
    
    created_order_ids = []
    for order in orders_data:
        response = requests.post(
            f"{BASE_URL}/orders",
            json=order,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 201:
            created_order_ids.append(response.json().get("id"))
            print(f"Created order for user: {order['userId']}")
    
    print(f"Created {len(created_order_ids)} orders")
    print("-" * 50)
    return created_order_ids

if __name__ == "__main__":
    print("Starting API Tests...")
    print("=" * 50)
    
    try:
        # Test health check
        test_health_check()
        
        # Test root endpoint
        test_root_endpoint()
        
        # Test create product with valid data
        product_id = test_create_product()
        
        # Test create product with invalid data
        test_create_product_invalid_data()
        
        # Create sample products for testing
        product_ids = create_sample_products()
        
        # Test list products
        test_list_products()
        
        # Test list products with pagination
        test_list_products_with_pagination()
        
        # Test list products with name filter
        test_list_products_with_name_filter()
        
        # Test list products with size filter
        test_list_products_with_size_filter()
        
        # Test list products with combined filters
        test_list_products_with_combined_filters()
        
        # Test create order
        order_id = test_create_order(product_ids)
        
        # Test create order with invalid product
        test_create_order_invalid_product()
        
        # Test create order with invalid data
        test_create_order_invalid_data()
        
        # Create multiple orders for testing
        create_multiple_orders(product_ids)
        
        # Test list orders
        test_list_orders()
        
        # Test list orders with pagination
        test_list_orders_with_pagination()
        
        # Test list orders for nonexistent user
        test_list_orders_nonexistent_user()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error during testing: {e}") 