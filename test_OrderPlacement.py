import unittest
from unittest import mock  # Import the mock module for simulating payment failures in tests.

# CartItem Class
class CartItem:
    """
    Represents an individual item in the shopping cart.
    
    Attributes:
        name (str): The name of the item.
        price (float): The price of the item.
        quantity (int): The quantity of the item in the cart.
    """
    def __init__(self, name, price, quantity):
        """
        Initializes a CartItem object with the given name, price, and quantity.
        
        Args:
            name (str): Name of the item.
            price (float): Price of the item.
            quantity (int): Quantity of the item in the cart.
        """
        self.name = name
        self.price = price
        self.quantity = quantity

    def update_quantity(self, new_quantity):
        """
        Updates the quantity of the item in the cart.
        
        Args:
            new_quantity (int): The new quantity of the item.
        """
        self.quantity = new_quantity

    def get_subtotal(self):
        """
        Calculates the subtotal price for this item based on its price and quantity.
        
        Returns:
            float: The subtotal price for this item.
        """
        return self.price * self.quantity


# Cart Class
class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, name, price, quantity):
        for item in self.items:
            if item.name == name:
                item.update_quantity(item.quantity + quantity)
                return f"Updated {name} quantity to {item.quantity}"
        new_item = CartItem(name, price, quantity)
        self.items.append(new_item)
        return f"Added {name} to cart"

    def remove_item(self, name):
        self.items = [item for item in self.items if item.name != name]
        return f"Removed {name} from cart"

    def update_item_quantity(self, name, new_quantity):
        for item in self.items:
            if item.name == name:
                item.update_quantity(new_quantity)
                return f"Updated {name} quantity to {new_quantity}"
        return f"{name} not found in cart"

    def calculate_total(self):
        subtotal = sum(item.get_subtotal() for item in self.items)
        tax = subtotal * 0.10  # Assume 10% tax rate.
        delivery_fee = 5.00  # Flat delivery fee.
        total = subtotal + tax + delivery_fee
        return {"subtotal": subtotal, "tax": tax, "delivery_fee": delivery_fee, "total": total}

    def view_cart(self):
        return [{"name": item.name, "quantity": item.quantity, "subtotal": item.get_subtotal()} for item in self.items]

    def get_items(self):
        return self.items


# OrderPlacement Class
class OrderPlacement:
    def __init__(self, cart, user_profile, restaurant_menu):
        self.cart = cart
        self.user_profile = user_profile
        self.restaurant_menu = restaurant_menu

    def proceed_to_checkout(self):
        items = self.cart.view_cart()
        subtotal = sum(item["subtotal"] for item in items)
        tax = subtotal * 0.10  # 10% tax
        delivery_fee = 5.00  # Flat delivery fee
        total = subtotal + tax + delivery_fee
        return {
            "items": items,
            "total_info": {
                "subtotal": subtotal,
                "tax": tax,
                "delivery_fee": delivery_fee,
                "total": total
            },
            "delivery_address": self.user_profile.delivery_address
        }

    def confirm_order(self, payment_method):
        # Simulate order confirmation
        return {"success": True, "order_id": "12345", "estimated_delivery": "30 minutes"}

    def validate_order(self):
        """
        Validates the order to ensure it's ready for checkout.

        Returns:
            dict: A dictionary with a 'success' key indicating whether the order is valid,
                   and an 'message' key providing a message about the validation result.
        """
        if not self.cart.get_items():
            return {"success": False, "message": "Your cart is empty."}
        # 添加其他验证逻辑，例如检查订单总额是否大于零
        total_info = self.cart.calculate_total()
        if total_info["total"] <= 0:
            return {"success": False, "message": "Order total is zero or negative."}
        # 如果所有检查都通过，则返回成功的验证结果
        return {"success": True, "message": "Order is valid and ready for checkout."}


# PaymentMethod Class
class PaymentMethod:
    """
    Represents the method of payment for an order.
    """
    def process_payment(self, amount):
        """
        Processes the payment for the given amount.
        
        Args:
            amount (float): The amount to be paid.
        
        Returns:
            bool: True if the payment is successful, False otherwise.
        """
        if amount > 0:
            return True
        return False


# UserProfile Class (for simulating the user's details)
class UserProfile:
    """
    Represents the user's profile, including delivery address.
    
    Attributes:
        delivery_address (str): The user's delivery address.
    """
    def __init__(self, delivery_address):
        """
        Initializes a UserProfile object with a delivery address.
        
        Args:
            delivery_address (str): The user's delivery address.
        """
        self.delivery_address = delivery_address


# RestaurantMenu Class (for simulating available menu items)
class RestaurantMenu:
    """
    Represents the restaurant's menu, including available items.
    
    Attributes:
        available_items (list): A list of items available on the restaurant's menu.
    """
    def __init__(self, available_items):
        """
        Initializes a RestaurantMenu with a list of available items.
        
        Args:
            available_items (list): A list of available menu items.
        """
        self.available_items = available_items

    def is_item_available(self, item_name):
        """
        Checks if a specific item is available in the restaurant's menu.
        
        Args:
            item_name (str): The name of the item to check.
        
        Returns:
            bool: True if the item is available, False otherwise.
        """
        return item_name in self.available_items


# Unit tests for OrderPlacement class
class TestOrderPlacement(unittest.TestCase):
    """
    Unit tests for the OrderPlacement class.
    """
    def setUp(self):
        """
        Sets up the test environment by creating instances of necessary classes.
        """
        self.restaurant_menu = RestaurantMenu(available_items=["Burger", "Pizza", "Salad"])
        self.user_profile = UserProfile(delivery_address="123 Main St")
        self.cart = Cart()
        self.order = OrderPlacement(self.cart, self.user_profile, self.restaurant_menu)

    def test_validate_order_empty_cart(self):
        """
        Test case for validating an order with an empty cart.
        """
        result = self.order.validate_order()
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Cart is empty")

    def test_validate_order_item_not_available(self):
        """
        Test case for validating an order with an unavailable item.
        """
        self.cart.add_item("Pasta", 15.99, 1)
        result = self.order.validate_order()
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Pasta is not available")

    def test_validate_order_success(self):
        """
        Test case for successfully validating an order.
        """
        self.cart.add_item("Burger", 8.99, 2)
        result = self.order.validate_order()
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Order is valid")

    def test_confirm_order_success(self):
        """
        Test case for confirming an order with successful payment.
        """
        self.cart.add_item("Pizza", 12.99, 1)
        payment_method = PaymentMethod()
        result = self.order.confirm_order(payment_method)
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Order confirmed")
        self.assertEqual(result["order_id"], "ORD123456")

    def test_confirm_order_failed_payment(self):
        """
        Test case for confirming an order with failed payment.
        """
        self.cart.add_item("Pizza", 12.99, 1)
        payment_method = PaymentMethod()

        # Use unittest.mock.patch to simulate failed payment processing.
        with mock.patch.object(payment_method, 'process_payment', return_value=False):
            result = self.order.confirm_order(payment_method)
            self.assertFalse(result["success"])
            self.assertEqual(result["message"], "Payment failed")

    def test_update_item_quantity(self):
        """Test case for updating quantity when item already exists in the cart"""
        # Step 1: Add the item "Apple" to the cart initially.
        self.cart.add_item("Apple", 1.0, 5)  # "Apple" starts with quantity 5.

        # Step 2: Now update the quantity of "Apple" by adding 3 more.
        result = self.cart.add_item("Apple", 1.0, 3)  # "Apple" quantity should become 8.

        # Step 3: Check that the result message reflects the quantity update.
        self.assertEqual(result, "Updated Apple quantity to 8")  # Expect updated quantity to be 8.

        # Step 4: Verify that the quantity of "Apple" in the cart is correct.
        self.assertEqual(self.cart.items[0].quantity, 8)  # Ensure that the quantity is 8.


if __name__ == "__main__":
    unittest.main()
