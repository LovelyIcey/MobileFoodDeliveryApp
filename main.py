import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

from test_UserRegistration import UserRegistration
from test_OrderPlacement import Cart, OrderPlacement, UserProfile, RestaurantMenu, PaymentMethod
from test_PaymentProcessing import PaymentProcessing
from test_RestaurantBrowsing import RestaurantDatabase, RestaurantBrowsing

# Utility functions for user data storage
USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mobile Food Delivery App")
        self.geometry("600x400")

        # Load user registration data from file
        self.user_data = load_users()

        # Initialize core classes
        self.registration = UserRegistration()
        self.registration.users = self.user_data  # Load existing users into registration system

        self.database = RestaurantDatabase()
        self.browsing = RestaurantBrowsing(self.database)

        # Initially no user logged in
        self.logged_in_email = None

        # Create initial frame
        self.current_frame = None
        self.show_startup_frame()

    def show_startup_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = StartupFrame(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_register_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = RegisterFrame(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_login_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self)
        self.current_frame.pack(fill="both", expand=True)

    def login_user(self, email):
        self.logged_in_email = email
        # After login, show main app frame
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = MainAppFrame(self, email)
        self.current_frame.pack(fill="both", expand=True)


class StartupFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Welcome to the Mobile Food Delivery App", font=("Arial", 16)).pack(pady=30)

        tk.Button(self, text="Register", command=self.go_to_register, width=20).pack(pady=10)
        tk.Button(self, text="Login", command=self.go_to_login, width=20).pack(pady=10)

    def go_to_register(self):
        self.master.show_register_frame()

    def go_to_login(self):
        self.master.show_login_frame()


class RegisterFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Register New User", font=("Arial", 14)).pack(pady=20)

        self.email_entry = self.create_entry("Email:")
        self.pass_entry = self.create_entry("Password:", show="*")
        self.conf_pass_entry = self.create_entry("Confirm Password:", show="*")

        tk.Button(self, text="Register", command=self.register_user).pack(pady=10)
        tk.Button(self, text="Back", command=self.go_back).pack()

    def create_entry(self, label_text, show=None):
        frame = tk.Frame(self)
        frame.pack(pady=5)
        tk.Label(frame, text=label_text, width=15, anchor="e").pack(side="left")
        entry = tk.Entry(frame, show=show)
        entry.pack(side="left")
        return entry

    def register_user(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        confirm_password = self.conf_pass_entry.get()

        result = self.master.registration.register(email, password, confirm_password)
        if result["success"]:
            # Save the updated users to file
            save_users(self.master.registration.users)
            messagebox.showinfo("Success", "Registration successful! Please log in.")
            self.master.show_login_frame()
        else:
            messagebox.showerror("Error", result["error"])

    def go_back(self):
        self.master.show_startup_frame()


class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="User Login", font=("Arial", 14)).pack(pady=20)

        self.email_entry = self.create_entry("Email:")
        self.pass_entry = self.create_entry("Password:", show="*")

        tk.Button(self, text="Login", command=self.login).pack(pady=10)
        tk.Button(self, text="Back", command=self.go_back).pack()

    def create_entry(self, label_text, show=None):
        frame = tk.Frame(self)
        frame.pack(pady=5)
        tk.Label(frame, text=label_text, width=15, anchor="e").pack(side="left")
        entry = tk.Entry(frame, show=show)
        entry.pack(side="left")
        return entry

    def login(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        # Validate login
        # For simplicity, just check if user exists and password matches
        users = self.master.registration.users
        if email in users and users[email]["password"] == password:
            self.master.login_user(email)
        else:
            messagebox.showerror("Error", "Invalid email or password")

    def go_back(self):
        self.master.show_startup_frame()


class MainAppFrame(tk.Frame):
    def __init__(self, master, user_email):
        super().__init__(master)
        tk.Label(self, text=f"Welcome, {user_email}", font=("Arial", 14)).pack(pady=10)

        self.user_email = user_email
        self.database = master.database
        self.browsing = master.browsing

        # Create user's profile and cart
        self.user_profile = UserProfile(delivery_address="123 Main St")
        self.cart = Cart()
        self.restaurant_menu = RestaurantMenu(available_items=["Burger", "Pizza", "Salad"])
        self.order_placement = OrderPlacement(self.cart, self.user_profile, self.restaurant_menu)

        # Search Frame
        search_frame = tk.Frame(self)
        search_frame.pack(pady=10)
        tk.Label(search_frame, text="Cuisine:").pack(side="left")
        self.cuisine_var = tk.Entry(search_frame)
        self.cuisine_var.pack(side="left", padx=5)
        tk.Button(search_frame, text="Search", command=self.search_restaurants).pack(side="left")

        # Results Treeview
        self.results_tree = ttk.Treeview(self, columns=("cuisine", "location", "rating"), show="headings")
        self.results_tree.heading("cuisine", text="Cuisine")
        self.results_tree.heading("location", text="Location")
        self.results_tree.heading("rating", text="Rating")
        self.results_tree.pack(pady=10, fill="x")

        # Buttons for actions
        action_frame = tk.Frame(self)
        action_frame.pack(pady=5)
        tk.Button(action_frame, text="View All Restaurants", command=self.view_all_restaurants).pack(side="left", padx=5)
        tk.Button(action_frame, text="Add Item to Cart", command=self.add_item_to_cart).pack(side="left", padx=5)
        tk.Button(action_frame, text="View Cart", command=self.view_cart).pack(side="left", padx=5)
        tk.Button(action_frame, text="Checkout", command=self.checkout).pack(side="left", padx=5)

    def search_restaurants(self):
        self.results_tree.delete(*self.results_tree.get_children())
        cuisine = self.cuisine_var.get().strip()
        results = self.browsing.search_by_filters(cuisine_type=cuisine if cuisine else None)
        for r in results:
            self.results_tree.insert("", "end", values=(r["cuisine"], r["location"], r["rating"]))

    def view_all_restaurants(self):
        self.results_tree.delete(*self.results_tree.get_children())
        results = self.database.get_restaurants()
        for r in results:
            self.results_tree.insert("", "end", values=(r["cuisine"], r["location"], r["rating"]))

    def add_item_to_cart(self):
        chosen_restaurant = self.choose_restaurant()
        if chosen_restaurant:  # 如果用户选择了一个餐馆
            menu_popup = AddItemPopup(self, chosen_restaurant, self.cart)
            self.wait_window(menu_popup)

    def choose_restaurant(self):
        restaurants = self.database.get_restaurants()
        restaurant_names = [r["name"] for r in restaurants]

        popup = tk.Toplevel(self)
        popup.title("Choose Restaurant")
        tk.Label(popup, text="Select a restaurant:").pack(pady=10)

        var = tk.StringVar(popup)
        var.set(restaurant_names[0])
        menu = tk.OptionMenu(popup, var, *restaurant_names)
        menu.pack(pady=5)

        def on_confirm():
            chosen_restaurant_name = var.get()
            chosen_restaurant = next((r for r in restaurants if r["name"] == chosen_restaurant_name), None)
            popup.destroy()
            self.show_menu_popup(chosen_restaurant)

        tk.Button(popup, text="Confirm", command=on_confirm).pack(pady=10)
        popup.wait_window()  # 这里会阻塞直到弹出窗口关闭

    def show_menu_popup(self, chosen_restaurant):
        if chosen_restaurant:
            menu_popup = AddItemPopup(self, chosen_restaurant, self.cart)
            self.wait_window(menu_popup)


    def view_cart(self):
        if CartViewPopup.instance and CartViewPopup.instance.winfo_exists():  # 检查实例是否存在且窗口未被销毁
            CartViewPopup.instance.lift()  # 激活现有窗口
        else:
            cart_view = CartViewPopup(self, self.cart)  # 创建新窗口
            self.wait_window(cart_view)

    def checkout(self):
        # Validate order and proceed if valid
        validation = self.order_placement.validate_order()
        if not validation["success"]:
            messagebox.showerror("Error", validation["message"])
            return

        # Show Checkout Popup
        checkout_popup = CheckoutPopup(self, self.order_placement)
        self.wait_window(checkout_popup)


class AddItemPopup(tk.Toplevel):
    def __init__(self, master, restaurant, cart):
        super().__init__(master)
        self.title("Add Item to Cart")
        self.restaurant = restaurant
        self.cart = cart

        tk.Label(self, text=f"Select a dish from {restaurant['name']}:").pack(pady=10)

        self.item_var = tk.StringVar()
        self.item_var.set(restaurant['dishes'][0] if restaurant['dishes'] else "")
        tk.OptionMenu(self, self.item_var, *restaurant['dishes']).pack(pady=5)

        tk.Label(self, text="Quantity:").pack()
        self.qty_entry = tk.Entry(self)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(pady=5)

        tk.Button(self, text="Add to Cart", command=self.add_to_cart).pack(pady=10)

    def add_to_cart(self):
        item = self.item_var.get()
        qty = int(self.qty_entry.get())

        # 检查输入的数量是否合法
        if qty <= 0:
            messagebox.showerror("Error", "Quantity must be greater than 0.")
            return

        price = 10.0  # Static price for simplicity
        self.cart.add_item(item, price, qty)
        messagebox.showinfo("Cart", f"Added {qty} of {item} to cart.")
        self.destroy()


class CartViewPopup(tk.Toplevel):
    instance = None  # 类变量，用于存储当前的实例

    def __init__(self, master, cart):
        super().__init__(master)
        self.title("Cart Items")
        self.cart = cart
        self.item_frames = []  # 用于存储每个商品的frame，以便后续删除

        if CartViewPopup.instance:
            # 如果实例已经存在，那么将焦点转移到现有的窗口上
            CartViewPopup.instance.lift()
            return
        else:
            CartViewPopup.instance = self  # 设置当前实例为类变量

        self.update_cart_display()  # 初始显示购物车内容

    def update_cart_display(self):
        for frame in self.item_frames:  # 清除现有的商品显示
            frame.destroy()
        self.item_frames = []  # 重置frame列表

        items = self.cart.view_cart()
        if not items:
            tk.Label(self, text="Your cart is empty").pack(pady=20)
        else:
            for item in items:
                frame = tk.Frame(self)  # 为每个商品创建一个frame
                frame.pack(pady=5)

                # 商品信息
                label = tk.Label(frame, text=f"{item['name']} x{item['quantity']} = ${item['subtotal']:.2f}")
                label.pack(side="left")

                # 删除按钮
                remove_button = tk.Button(frame, text="x", command=lambda: self.remove_item(item))
                remove_button.pack(side="right")

                self.item_frames.append(frame)  # 将frame添加到列表中

    def remove_item(self, item):
        # 从购物车中移除商品，并更新界面
        self.cart.remove_item(item['name'])
        self.update_cart_display()  # 更新购物车显示

    def add_item(self, item):
        # 添加商品到购物车，并更新界面
        self.cart.add_item(item)
        self.update_cart_display()  # 更新购物车显示

    def on_closing(self):
        CartViewPopup.instance = None
        self.destroy()


class CheckoutPopup(tk.Toplevel):
    def __init__(self, master, order_placement):
        super().__init__(master)
        self.title("Checkout")
        self.order_placement = order_placement

        order_data = order_placement.proceed_to_checkout()
        tk.Label(self, text="Review your order:", font=("Arial", 12)).pack(pady=10)

        # Show items
        for item in order_data["items"]:
            tk.Label(self, text=f"{item['name']} x{item['quantity']} = ${item['subtotal']:.2f}").pack()

        total = order_data["total_info"]
        tk.Label(self, text=f"Subtotal: ${total['subtotal']:.2f}").pack()
        tk.Label(self, text=f"Tax: ${total['tax']:.2f}").pack()
        tk.Label(self, text=f"Delivery Fee: ${total['delivery_fee']:.2f}").pack()
        tk.Label(self, text=f"Total: ${total['total']:.2f}").pack()

        tk.Label(self, text=f"Delivery Address: {order_data['delivery_address']}").pack(pady=5)

        # Payment method selection
        tk.Label(self, text="Payment Method:").pack(pady=5)
        self.payment_method = tk.StringVar()
        self.payment_method.set("credit_card")
        tk.Radiobutton(self, text="Credit Card", variable=self.payment_method, value="credit_card").pack()
        tk.Radiobutton(self, text="Paypal", variable=self.payment_method, value="paypal").pack()

        tk.Label(self, text="For credit card enter a 16-digit card number:").pack(pady=5)
        self.card_entry = tk.Entry(self)
        self.card_entry.insert(0, "1234567812345678")
        self.card_entry.pack(pady=5)

        # Discount code entry
        tk.Label(self, text="Discount Code:").pack(pady=5)
        self.discount_code_entry = tk.Entry(self)
        self.discount_code_entry.insert(0, "12345")
        self.discount_code_entry.pack(pady=5)

        tk.Button(self, text="Confirm Order", command=self.confirm_order).pack(pady=10)

    def confirm_order(self):
        # Process order confirmation with the given payment method
        payment_method_obj = PaymentMethod()  # Mock payment method handling in the old code
        # Actually, we have PaymentProcessing class. Let's just rely on PaymentMethod for simplicity here.
        # If you wanted to use PaymentProcessing, you could do so by integrating it as well.
        # For now, we'll simulate PaymentMethod.process_payment by checking if total > 0.
        # In a full scenario, integrate PaymentProcessing similarly.

        # Confirm the order
        result = self.order_placement.confirm_order(payment_method_obj)
        if result["success"]:
            messagebox.showinfo("Order Confirmed", f"Order ID: {result['order_id']}\nEstimated Delivery: {result['estimated_delivery']}")
            self.destroy()
        else:
            messagebox.showerror("Error", result["message"])


if __name__ == "__main__":
    app = Application()
    app.mainloop()
