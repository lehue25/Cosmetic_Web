from flask import (Flask, render_template, request, redirect, session,jsonify, url_for, jsonify, flash)
import sqlite3, uuid

from datetime import datetime
app = Flask(__name__)
app = Flask(__name__, static_folder='static')
app.secret_key = 'my_secret_key'
sqldbweb='db/products.db'
sqldbreview='db/review.db'

@app.route('/')
def index():
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE product_personalized = 1 LIMIT 4')
    products = cursor.fetchall()
    cursor.execute('SELECT * FROM products WHERE product_featured = 1 ORDER BY create_at DESC LIMIT 8')
    featured = cursor.fetchall()
    conn.close()
    return render_template('index.html', table = products, featured = featured)
@app.route("/index.html")
def home():
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE product_personalized = 1 LIMIT 4')
    products = cursor.fetchall()
    cursor.execute('SELECT * FROM products WHERE product_featured = 1 LIMIT 8')
    featured = cursor.fetchall()
    conn.close()
    return render_template('index.html', table = products, featured = featured)

@app.route('/products.html')
def product():
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('select * from products limit 20')
    data = cursor.fetchall()
    cursor.execute('select * from products where sale_off ="-25%" limit 4')
    sale = cursor.fetchall()
    conn.close()
    return render_template('products.html', table=data, sale=sale)

@app.route('/product/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
    product = cursor.fetchall()
    cursor.execute("SELECT product_detail.* FROM products INNER JOIN product_detail ON products.product_id = product_detail.product_id WHERE products.product_id = ?", (product_id,))
    product_detail = cursor.fetchall()
    cursor.execute("SELECT * FROM product_reviews where product_id = ? ORDER BY create_at DESC LIMIT 5", (product_id,))
    product_reviews= cursor.fetchall()
     # Lấy danh mục của sản phẩm hiện tại
    cursor.execute("SELECT label FROM products WHERE product_id = ?", (product_id,))
    label = cursor.fetchone()[0]

    # Tìm các sản phẩm có cùng danh mục
    cursor.execute("SELECT * FROM products WHERE label = ? AND product_id != ? LIMIT 5", (label, product_id))
    related_products = cursor.fetchall()
    conn.close()
    return render_template('product_detail.html', product=product, product_detail=product_detail,product_reviews =product_reviews, related_products =related_products )

def add_review_to_database(user_id, username, product_id, messages, rating):
    conn = sqlite3.connect(sqldbweb)
    cur = conn.cursor()
    cur.execute("INSERT INTO product_reviews (user_id, username, product_id, messages, rating) VALUES (?, ?, ?, ?, ?)",
                (user_id, username, product_id, messages, rating))
    conn.commit()
    conn.close()
    
def user_has_ordered_product(user_id, product_id):
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    product_id_lowercase = str(product_id).lower()

    # Thực hiện truy vấn SQL
    cursor.execute("""
        SELECT * 
        FROM orders 
        INNER JOIN order_detail 
        ON orders.order_id = order_detail.order_id 
        WHERE orders.user_id = ? COLLATE NOCASE 
        AND order_detail.product_id = ?""",
        (user_id, product_id_lowercase))
    order = cursor.fetchone()
    conn.close()
    return order is not None

@app.route('/submit_review_prod', methods=['POST'])
def submit_review_prod():
    if request.method == 'POST':
        product_id = request.form['product_id']
        user_id = request.form['user_id']
        username = request.form['username']
        messages = request.form['messages']
        rating = request.form['rating']
        
        if user_has_ordered_product(user_id, product_id):
            add_review_to_database(user_id, username, product_id, messages, rating)
            outputmessage = "Đánh giá thành công!"
            return outputmessage;

        else:
            outputmessage = "Bạn chưa mua sản phẩm này"
            return outputmessage;
@app.route('/review.html')
def review():
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts ORDER BY create_at DESC')
    post = cursor.fetchall()
    cursor.execute('SELECT * FROM posts ORDER BY create_at DESC LIMIT 3')
    recent_news = cursor.fetchall()
    conn.close()
    return render_template('review.html', table = post, recent_news=recent_news)

@app.route('/review/<int:post_id>')
def post_detail(post_id):
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts WHERE post_id= ?', (post_id,))
    post = cursor.fetchall()
    cursor.execute('SELECT * FROM products LIMIT 5')
    related_products= cursor.fetchall()
    conn.close()
    return render_template('review_detail.html', table = post, related_products= related_products)
@app.route('/contact.html')
def contact():
    return render_template('contact.html')
# SEARCH FUNCTION
@app.route('/search', methods=['POST'])
def search():
    try:
        search_text = request.form['searchInput']
    except KeyError:
        # Xử lý nếu không có 'searchInput' trong form
        return "Invalid request", 400

    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()
    conn.close()

    search_table = load_data_from_db(search_text)
    
    return render_template(
        'search.html', table=data, x=search_text, search_result=search_table
    )

def load_data_from_db(search_text):
    if search_text:
        conn = sqlite3.connect(sqldbweb)
        cursor = conn.cursor()
        # Sử dụng parameterized query để tránh lỗi và vấn đề an ninh
        sqlcommand = "SELECT * FROM products WHERE product_name LIKE ? OR label LIKE ? OR product_brand LIKE ? "
        cursor.execute(sqlcommand, ('%' + search_text + '%', '%' + search_text + '%','%' + search_text + '%',))
        data = cursor.fetchall()
        conn.close()
        if not data:
            return "Product not found"
        else:
            return data
    else: 
        return "Invalid search"

@app.route('/category/<category>')
def get_products(category=None):
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ? AND sale_off <='-25%' LIMIT 4", (category,))
    sale = cursor.fetchall()
    cursor.execute("SELECT * FROM products WHERE category = ? or label = ? ", (category,category,))
    products = cursor.fetchall()
    conn.close()
    has_sale = bool(sale)  
    return render_template('category.html', sale= sale, products=products, selected_category=category, has_sale=has_sale)


@app.route("/cart/add", methods=['POST'])
def add_to_cart():
    if 'logged_in' in session and session['logged_in']: 
        # 1. get product id and quantity from the form
        product_id = request.form["product_id"]
        quantity = int(request.form["quantity"])
        #2. get the product name in price form the database
        conn = sqlite3.connect(sqldbweb)
        cursor = conn.cursor()
        cursor.execute("SELECT product_name, product_price,img " "FROM products WHERE product_id = ?",(product_id,) )
        #get one product
        product = cursor.fetchone()
        conn.close()
        product_dict = {
            "product_id": product_id,
            "product_name": product[0],
            "product_price": product[1],
            "product_img":product[2],
            "quantity": quantity
        }
        #get the cart from the session or create an empty list
        cart = session.get("cart",[])
        user_id = session.get('user_id')
        session['user_id'] = user_id

        #check if the product is already in the cart 
        found = False
        for item in cart:
            if item["product_id"] ==product_id:
                # update the quantity of existing product
                item["quantity"] += quantity
                found = True
                break
        if not found: 
            # add the new product to the cart 
            cart.append(product_dict)
        session["cart"] = cart
        rows = len(cart)
        outputmessage = "Product added to cart successfully!"
        # return redirect(url_for('view_cart', user_id=session['user_id']))
        #return redirect(url_for('view_cart', user_id=session['user_id']))
        return outputmessage;
    else:
        message_need_login = "Bạn cần đăng nhập!"
        return message_need_login;
@app.route('/update_cart', methods=['POST'])
def update_cart():
    cart = session.get('cart', [])
    new_cart = []
    delivery = session.get('delivery', None)
    for product in cart:
        product_id = str(product['product_id'])
        quantity_key = f'quantity-{product_id}'
        delete_key = f'delete-{product_id}'
        if delete_key not in request.form :
            new_cart.append(product)
        if quantity_key in request.form:
            quantity = int(request.form[quantity_key])
            if quantity > 0:
                product['quantity'] = quantity
            elif quantity == 0 and delete_key not in request.form:
                product['quantity'] = 0
    session['cart'] = new_cart
    total_price = 0
    for item in new_cart :
        total_price+= item["product_price"] * item["quantity"] 
    rows = len(cart)
    return render_template("cart.html", carts = new_cart, rows = rows,delivery = delivery,total_price=total_price)
# change quantity
@app.route("/change_quantity", methods=['POST'])
def change_quantity():
    if 'cart' in session:
        cart = session['cart'] 
        data = request.get_json() # Lấy dữ liệu gửi từ client
        product_id = data['productId']
        new_quantity = data['quantity']
        
        # Tìm sản phẩm trong giỏ hàng và cập nhật số lượng
        for item in cart:
            if item["product_id"] == product_id:
                item["quantity"] = new_quantity
                break
        
        session['cart'] = cart
        session.modified = True
        
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Cart not found in session"}), 404


@app.route("/cart/<int:user_id>", methods=['POST','GET'])
def view_cart(user_id):
    if 'logged_in' in session and session['logged_in']: 
        current_cart = session.get("cart", [])
        has_item_in_cart = bool(current_cart)
        rows = len(current_cart)
        conn = sqlite3.connect(sqldbweb)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders WHERE user_id = ? COLLATE NOCASE ORDER BY order_id DESC LIMIT 1', (user_id,))
        delivery = cursor.fetchall()  
        session['delivery'] = delivery
        conn.close()
        total_price = 0
        for item in current_cart :
            total_price+= item["product_price"] * item["quantity"] 
        return render_template("cart.html", carts=current_cart, has_item_in_cart=has_item_in_cart, rows=rows, logged_in=session['logged_in'], delivery = delivery,total_price=total_price)
    else:
        message_need_login = "Bạn cần đăng nhập!"
        return render_template("index.html", message_need_login=message_need_login, logged_in=session.get('logged_in', False))


@app.route("/login", methods=["POST"])
def login(): 
    username = request.form["username"]
    password = request.form["password"]
    if check_exists(username, password):
        user_id = check_exists(username, password) 
    # Lưu ID của người dùng vào session
        session['user_id'] = user_id[1]
        session['logged_in'] = True
        session['username'] = username
        session['logged_in'] = True
        # user_data = check_exists(username, password)
        # session['user_data'] = user_data[1]
        return jsonify({'success': True, 'message': 'Đăng nhập thành công'})
    else:
        return jsonify({'success': False, 'message': 'Tên đăng nhập hoặc mật khẩu không đúng'})

@app.route("/logout")
def logout():
    # Xóa toàn bộ thông tin trong session
    session.clear()
    # Chuyển hướng người dùng đến trang chính hoặc trang đăng nhập
    return redirect(url_for("index"))
#đăng ký tài khoản
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]
    date_of_birth = request.form["date_of_birth"]
    phone_number = request.form["phone_number"]
    if not check_exists(username, email):
        create_user(username, password, email, date_of_birth, phone_number)
        return jsonify({'success': True, 'message': 'Đăng ký thành công, vui lòng đăng nhập!'})
    else:
        return jsonify({'success': False, 'message': 'Username hoặc Email, Số điện thoại đã tồn tại'})
def check_exists(username, email):
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
    data = cursor.fetchone()
    conn.close()
    return data

def create_user(username, password, email, date_of_birth, phone_number):
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, email, date_of_birth, phone_number) VALUES (?, ?, ?, ?, ?)",
                   (username, password, email, date_of_birth, phone_number))
    conn.commit()
    conn.close()
#hiển thị thông tin người dùng
@app.route("/user/<int:user_id>")
def get_user_info(user_id):
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()  
    conn.close()
    return render_template('user.html', user=user)
#thay đổi và lưu dữ liệu người dùng
@app.route("/save_changes/<int:user_id>", methods=["POST"])
def save_changes(user_id):
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone() 
    conn.close()

    if request.method == "POST":
        # Lấy dữ liệu từ form gửi từ client
        new_email = request.form.get('email')
        new_phone = request.form.get('phone')
        new_password = request.form.get('password')

        # Kiểm tra xem có dữ liệu nào được chỉnh sửa không
        if new_email is not None or new_phone is not None or new_password is not None:
            # Thực hiện cập nhật thông tin vào cơ sở dữ liệu
            update_user_info_in_database(user_id, new_email, new_phone, new_password)
        
        # Chuyển hướng người dùng đến trang sau khi cập nhật thành công
        return redirect(f"/user/{user_id}")

    # Nếu không phải là request POST, trả về trang thông tin người dùng
    return redirect(f"/user/{user_id}")

def update_user_info_in_database(user_id, new_email, new_phone, new_password):
    conn = sqlite3.connect(sqldbweb)  
    cursor = conn.cursor()
    # Tạo một danh sách các trường cần cập nhật
    update_fields = []
    if new_email is not None:
        update_fields.append(('email', new_email))
    if new_phone is not None:
        update_fields.append(('phone_number', new_phone))
    if new_password is not None:
        update_fields.append(('password', new_password))
    # Tạo câu lệnh SQL cập nhật dựa trên các trường được chỉnh sửa
    if update_fields:
        # Tạo phần SET của câu lệnh UPDATE
        set_clause = ', '.join([f"{field} = ?" for field, _ in update_fields])
        # Tạo danh sách giá trị cần cập nhật
        values = [value for _, value in update_fields]
        # Thực thi câu lệnh UPDATE
        cursor.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", (*values, user_id))
        conn.commit()
    conn.close()


#xuất hóa đơn
@app.route("/completed", methods=["POST"])
def complete():
    # Lấy thông tin giao hàng từ form
    full_name = request.form["fullName"]
    phone_number = request.form["phoneNumber"]
    email = request.form["email"]
    city = request.form["city"]
    district = request.form["district"]
    ward = request.form["ward"]
    note = request.form["note"]
    # Lấy thông tin giỏ hàng từ session
    carts = session.get("cart", [])
    total_price = 0
    for item in carts :
        total_price+= item["product_price"] * item["quantity"] 
    user_id = session.get('user_id')
    payment_method = request.form.get("payment_method")
    create_order(full_name,phone_number,email,city,district,ward,note,user_id,total_price)
    for item in carts :
        product_id = item["product_id"]
        quantity = item["quantity"]
        create_order_detail(product_id,quantity)
    session.pop('cart', None)
    
    return render_template('completed.html', full_name=full_name,phone_number=phone_number, email= email,city=city,district=district,ward=ward,note=note,carts=carts, payment_method= payment_method)
def create_order(fullName,phoneNumber,email,city,district,ward,note,user_id,totalPrice):
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (user_id,total_price, name, email, phone_number, city, district,ward,note) VALUES (?,?,?,?,?,?,?,?,?)",
                   (user_id,totalPrice,fullName,email,phoneNumber,city,district,ward,note))
    conn.commit()
    conn.close()
def create_order_detail(product_id,quantity):
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('SELECT order_id FROM orders ORDER BY order_id DESC LIMIT 1')
    order_id = cursor.fetchone()
    cursor.execute("INSERT INTO order_detail (order_id,product_id,quantity) VALUES (?,?,?)",
                   (order_id[0],product_id,quantity))
    conn.commit()
    conn.close()
@app.route("/order_detail")
def order_detail():
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('SELECT order_id FROM orders ORDER BY order_id DESC LIMIT 1')
    order_id = cursor.fetchone()
    cursor.execute('SELECT * FROM posts ORDER BY create_at DESC LIMIT 3')
    recent_news = cursor.fetchall()# tra ve kieu tuple u[], 
    # Truy vấn cơ sở dữ liệu để lấy thông tin chi tiết của đơn hàng
    cursor.execute("""
        SELECT orders.*, products.product_name, products.img,order_detail.quantity,products.product_price, products.product_brand
        FROM orders
        JOIN order_detail ON orders.order_id = order_detail.order_id
        JOIN products ON order_detail.product_id = products.product_id
        WHERE orders.order_id = ? COLLATE NOCASE
        ORDER BY orders.order_id DESC
    """, (order_id[0],))
    order_details = cursor.fetchall()
    conn.close()
    return render_template("order_detail.html", order_details=order_details, recent_news=recent_news)
@app.route("/orders")
def get_orders():
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    user_id  = session.get("user_id")
    # Truy vấn cơ sở dữ liệu để lấy thông tin chi tiết của đơn hàng
    cursor.execute("""
        SELECT *
        FROM orders
        WHERE orders.user_id = ? COLLATE NOCASE 
        ORDER BY orders.order_id DESC
    """, (user_id,))
    order_details = cursor.fetchall()
    cursor.execute('SELECT * FROM products WHERE product_featured = 1 COLLATE NOCASE ORDER BY create_at DESC LIMIT 3')
    featured = cursor.fetchall()
    cursor.execute('SELECT COUNT(order_detail_id) - 1 FROM order_detail JOIN orders ON order_detail.order_id = orders.order_id WHERE orders.user_id = ? COLLATE NOCASE GROUP BY order_detail.order_id ORDER BY order_detail.order_id DESC', (user_id,))
    count_prod = cursor.fetchall()
    conn.close()
    orders_list = []
    for order in order_details:
        order_dict = {}
        order_dict['order_id'] = order[0]
        order_dict['user_id'] = order[1]
        order_dict['recipient_name'] = order[3]
        order_dict['user_city'] = order[6]
        order_dict['user_district'] = order[7]  
        order_dict['user_ward'] = order[8]
        order_dict['note'] = order[9]
        orderx = get_order_details_by_order_id(order[0])
        first_product = orderx[0]  # Lấy sản phẩm đầu tiên trong danh sách
        order_dict['img'] = first_product['img']
        order_dict['name'] = first_product['name']
        order_dict['price'] = first_product['price']
        order_dict['total_price'] = order[2]
        order_dict['order_day'] = order[11]
        order_dict['status'] = order[12]
        orders_list.append(order_dict)    
    return render_template("customer_order.html", orders_list=orders_list, featured=featured, count_prod= count_prod)


def get_order_details_by_order_id(order_id):
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('SELECT * from order_detail INNER JOIN products ON products.product_id = order_detail.product_id WHERE order_id = ?',(order_id,))
    products_order = cursor.fetchall()
    products_order_list = []
    for product in products_order:
        product_dict ={}
        product_dict['product_id'] =  product[1]
        product_dict['quantity'] = product[3]
        product_dict['price'] = product[6]
        product_dict['img'] = product[11]
        product_dict['name'] = product[5]
        products_order_list.append(product_dict)
    return products_order_list

#chức năng hiển thị chi tiết order của người dùng
@app.route("/order_details/<int:order_id>")
def order_details(order_id):
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM orders
        WHERE orders.order_id = ? COLLATE NOCASE 
    """, (order_id,))
    order = cursor.fetchone()
    # Lấy tất cả các chi tiết đơn hàng cho đơn hàng này
    order_details = get_order_details_by_order_id(order_id)
    cursor.execute('SELECT * FROM posts ORDER BY create_at DESC LIMIT 3')
    recent_news = cursor.fetchall()
    conn.close()
    return render_template("order_details.html", order=order, order_details=order_details, recent_news =recent_news)
#END 
@app.route('/contact_form', methods=['POST'])
def submit_contact_form():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message') 
    try:
        conn = sqlite3.connect(sqldbweb)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contact_mess (name, email, message) VALUES (?, ?, ?)", (name, email, message))
        conn.commit()
        conn.close()
        message_contact = "Shifiny cảm ơn bạn đã lên hệ! Chúng tôi sẽ sớm phản hồi tin nhắn của bạn."
        return message_contact 
    except Exception as e:
        return str(e), 500
#Admin
@app.route("/admin")
def admin():
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('select * from products ORDER BY create_at DESC')
    data = cursor.fetchall()
    conn.close()
    delete_success_message = session.pop('delete_success_message', None)
    return render_template('Template_Admin/admin.html', table=data, delete_success_message=delete_success_message)
@app.route("/product-show.html")
def prd_show_ad():
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('select * from products limit 20')
    data = cursor.fetchall()
    conn.close()
    return render_template('Template_Admin/product-show.html', table=data)
@app.route("/product-create.html")
def prd_create_ad():
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('select * from products limit 20')
    data = cursor.fetchall()
    conn.close()
    return render_template('Template_Admin/product-create.html', table=data)

@app.route('/product-create', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        # Lấy thông tin sản phẩm từ biểu mẫu
        brand = request.form['Brand']
        category = request.form['product_category']
        name = request.form['name']
        image = request.form['product-img']
        price = request.form['price']
        description = request.form['description']
        ingredients = request.form['Ingredients']
        user_manual = request.form['User manual']
        quantity = request.form['quantity']
        description_image_2 = request.form['description_image_2']
        description_image_1 = request.form['description_image_1']
        product_label = request.form['product_label']
        combination_skin = request.form.get('combination_skin', '0')  # If not checked, default value is '0'
        oily_skin = request.form.get('oily_skin', '0')
        normal_skin = request.form.get('normal_skin', '0')
        dry_skin = request.form.get('dry_skin', '0')
        sensitive_skin = request.form.get('sensitive_skin', '0')
        feature_product = request.form.get('feature_product', '0')
        sale_off = request.form['sale_off']
        if insert_product(brand, category, name, image, price, description, ingredients, user_manual, quantity,description_image_2,description_image_1,product_label, combination_skin,dry_skin,normal_skin,oily_skin,sensitive_skin,feature_product,sale_off):
            success_message = "Bạn đã thêm sản phẩm thành công!"
            return render_template('Template_Admin/product-create.html', success_message=success_message)
        else:
            return "Đã xảy ra lỗi khi thêm sản phẩm!"
    else:
        return render_template('Template_Admin/product-create.html')
# Hàm chèn thông tin sản phẩm vào CSDL
def insert_product(brand, category, name, image, price, description, ingredients, user_manual,quantity,description_image_2,description_image_1,product_label, combination_skin,dry_skin,normal_skin,oily_skin,sensitive_skin,feature_product,sale_off):
        conn = sqlite3.connect(sqldbweb)
        cursor = conn.cursor()
        sql = '''INSERT INTO products (product_brand, category, product_name, img, product_price, product_des, Ingredients, product_infor,quantity,img_detail,img_des_sd,label,Combination, Dry, Normal, Oily, Sensitive, product_featured, sale_off)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?,?,?,?,?,?,?)'''

        cursor.execute(sql, (brand, category, name, image, price, description, ingredients, user_manual,quantity,description_image_2,description_image_1,product_label, combination_skin,dry_skin,normal_skin,oily_skin,sensitive_skin,feature_product,sale_off))
        conn.commit()
        conn.close()
        return True
# Search PRODUCT Function Admin
@app.route("/searchPrdAdmin", methods=['POST'])
def searchPrdAdmin():
    try:
        search_text = request.form['searchInput']
    except KeyError:
        return "Invalid request", 400
    conn = sqlite3.connect(sqldbweb)
    cursor  = conn.cursor()
    cursor.execute("SELECT * FROM products ")
    data = cursor.fetchall()
    conn.close()
    search_table = load_data_from_db(search_text)
    return render_template(
        'Template_Admin/admin.html', data= data, x= search_text, search_result = search_table)

# Delete Product Funtion Admin 
@app.route("/deletePrdAdmin", methods=['POST'])
def deletePrdAdmin():
  try:
        # Lấy product_id từ dữ liệu gửi đi
        product_id = request.form.get('product_id')
        if not product_id:
            return "Product ID is required", 400

        conn = sqlite3.connect(sqldbweb)
        cursor = conn.cursor()
        # Sử dụng tham số trong truy vấn để tránh injection SQL
        cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
        conn.commit()
        conn.close()
        session['delete_success_message'] = "Bạn đã xóa sản phẩm thành công!"
        return redirect(url_for('admin'))
  except Exception as e:
      return str(e), 500

# View Product Detail
@app.route('/product_show/<int:product_id>', methods=['GET'])
def product_show(product_id):
    conn = sqlite3.connect(sqldbweb) 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id = ?",(product_id,))
    product_view = cursor.fetchall()
    conn.close()
    return render_template('Template_Admin/product-show.html', product_view = product_view)
#Hiển thị thông tin sản phẩm
@app.route("/product-edit/<int:product_id>")
def product_edit(product_id):
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id = ?",(product_id,))
    product_edit = cursor.fetchall()
    # Lấy thông báo thành công từ session (nếu có)
    success_message = session.pop('success_message', None)
    # Truyền thông báo thành công vào template
    return render_template('Template_Admin/product-edit.html', product_edit=product_edit, success_message=success_message)
# Lưu thay đổi thông tin sản phẩm
@app. route("/save_edit_product/<int:product_id>",methods=["POST"])
def save_edit_prd(product_id):
    if request.method == 'POST':
        # Lấy thông tin sản phẩm từ biểu mẫu chỉnh sửa
        brand = request.form['Brand']
        category = request.form['product_category']
        name = request.form['name']
        image = request.form['product-img']
        price = request.form['price']
        description = request.form['description']
        ingredients = request.form['Ingredients']
        user_manual = request.form['user_manual']
        quantity = request.form['quantity']
        description_image_2 = request.form['description_image_2']
        description_image_1 = request.form['description_image_1']
        product_label = request.form['product_label']
        combination_skin = request.form.get('combination_skin', '0')  # If not checked, default value is '0'
        oily_skin = request.form.get('oily_skin', '0')
        normal_skin = request.form.get('normal_skin', '0')
        dry_skin = request.form.get('dry_skin', '0')
        sensitive_skin = request.form.get('sensitive_skin', '0')
        feature_product = request.form.get('feature_product', '0')
        sale_off = request.form['sale_off']
        # Kết nối CSDL và cập nhật thông tin sản phẩm
        conn = sqlite3.connect(sqldbweb)
        cursor = conn.cursor()
        sql = '''UPDATE products 
                 SET product_brand=?, category=?, product_name=?, img=?, product_price=?, product_des=?, Ingredients=?, product_infor=?,quantity=?,img_detail=?,img_des_sd=?,label=?,Combination=?, Dry=?, Normal=?, Oily=?, Sensitive=?, product_featured=?, sale_off=?,update_at = CURRENT_TIMESTAMP
                 WHERE product_id=?'''
        cursor.execute(sql, (brand, category, name, image, price, description, ingredients, user_manual, quantity, description_image_2, description_image_1, product_label, combination_skin, dry_skin, normal_skin, oily_skin, sensitive_skin, feature_product, sale_off, product_id))
        conn.commit()
        conn.close()
        session['success_message'] = "Sản phẩm đã được cập nhật thành công!"
        # Chuyển hướng về trang chỉnh sửa sản phẩm
        return redirect(url_for('product_edit', product_id=product_id))
    else:
        return "Method not allowed"
    
#View Contact Message Admin Function
@app.route("/contact-message.html")
def view_contact_mess():
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contact_mess')
    contact_mess = cursor.fetchall()
    conn.commit()
    conn.close()
    return render_template('Template_Admin/contact-message.html', contact_mess = contact_mess)
#Delete Contact Message Admin Function
@app.route("/deleteMessContact", methods=['POST'])
def deleteMessContact():
    try:
        #Lấy contact_id từ dữ liệu gửi đi
        contact_mess_id = request.form.get('contact_mess_id')
        if not contact_mess_id:
            return "Contact Message ID is required", 400
        conn = sqlite3.connect(sqldbweb)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contact_mess WHERE contact_mess_id = ?", (contact_mess_id,))
        conn.commit()
        conn.close()
        session['delete_success_message'] = "Bạn đã xóa message thành công!"
        return redirect(url_for('view_contact_mess'))
    except Exception as e: 
        return str(e), 500

#View Users Admin Function
@app.route("/admin/user")
def view_users():
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.commit()
    conn.close()
    return render_template("Template_Admin/user.html", users=users)

# Delete Users Funtion Admin 
@app.route("/deleteUserAdmin", methods=['POST'])
def deleteUserAdmin():
  try:
        # Lấy product_id từ dữ liệu gửi đi
        user_id = request.form.get('user_id')
        if not user_id:
            return "User ID is required", 400

        conn = sqlite3.connect(sqldbweb)
        cursor = conn.cursor()
        # Sử dụng tham số trong truy vấn để tránh injection SQL
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        session['delete_success_user'] = "Bạn đã xóa người dùng thành công!"
        return redirect(url_for('view_users'))
  except Exception as e:
      return str(e), 500
#View order Admin Function
@app.route("/admin/orders")
def view_orders():
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders ORDER BY create_at ASC')
    orders = cursor.fetchall()
    conn.commit()
    conn.close()
    return render_template("Template_Admin/order.html", orders = orders)
@app.route("/admin/order_details/<int:order_id>")
def admin_order_details(order_id):
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM orders
        WHERE orders.order_id = ? COLLATE NOCASE 
    """, (order_id,))
    order = cursor.fetchone()
    # Lấy tất cả các chi tiết đơn hàng cho đơn hàng này
    order_details = get_order_details_by_order_id(order_id)
    conn.close()
    return render_template("Template_Admin/order-show.html", order=order, order_details=order_details)
#Update Status Order Admin Function
@app. route("/update_status_order/<int:order_id>",methods=["POST"])
def update_status_order(order_id):
    if request.method == 'POST':
        status = request.form['status']
        conn = sqlite3.connect(sqldbweb)
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status= ? where order_id=? ",(status, order_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_orders'))
    else:
        return "Method not allowed"
#View Blog and Function
@app.route("/admin/blogs")
def view_blogs():
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts ORDER BY create_at DESC')
    blogs = cursor.fetchall()
    conn.commit()
    conn.close()
    return render_template("Template_Admin/blogs.html", blogs = blogs)
#add blog admin
@app.route("/blog-create.html")
def view_create_blog():
    return render_template('Template_Admin/blog-create.html')
@app.route('/blog-create', methods=['POST'])
def create_blog():
        # Lấy thông tin sản phẩm từ biểu mẫu
    title = request.form['Title']
    name = request.form['name']
    image = request.form['blog-img']
    description = request.form['description']
    main_content = request.form['Main Content']
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()

    # Chèn dữ liệu vào bảng posts
    cursor.execute('''
        INSERT INTO posts (title, user_name, description, img_post, content)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, name, description, image, main_content))
    conn.commit()
    conn.close()
    return redirect(url_for("view_blogs"))
# Delete Post Funtion Admin 
@app.route("/deletePostAdmin", methods=['POST'])
def deletePostAdmin():
  try:
        # Lấy post_id từ dữ liệu gửi đi
        post_id = request.form.get('post_id')
        if not post_id:
            return "Post ID is required", 400
        conn = sqlite3.connect(sqldbweb)
        cursor = conn.cursor()
        # Sử dụng tham số trong truy vấn để tránh injection SQL
        cursor.execute("DELETE FROM posts WHERE post_id = ?", (post_id,))
        conn.commit()
        conn.close()
       
        return redirect(url_for('view_blogs'))
  except Exception as e:
      return str(e), 500
#Admin DashBoard 
@app.route("/dashboard")
def ad_dashboard():
    conn = sqlite3.connect(sqldbweb)
    cursor = conn.cursor()
    cursor.execute('SELECT count(*) FROM users')
    count_user = cursor.fetchall()
    cursor.execute('SELECT SUM(total_price) FROM orders')
    revenue = cursor.fetchall()
    cursor.execute('SELECT count(*) FROM contact_mess')
    count_mess = cursor.fetchall()
    cursor.execute('SELECT count(*) FROM orders')
    orders = cursor.fetchall()
    cursor.execute('SELECT count(*) FROM posts')
    post = cursor.fetchall()
    cursor.execute("SELECT count(*) FROM orders WHERE status ='Đã hoàn thành'")
    delivered = cursor.fetchall()
    cursor.execute("SELECT count(*) FROM orders WHERE status ='Hủy'")
    cancel = cursor.fetchall()
    cursor.execute("SELECT count(*) FROM orders WHERE status ='Đang giao hàng'")
    shipping = cursor.fetchall()
    cursor.execute("SELECT count(*) FROM orders WHERE status ='Đang xử lý'")
    processing = cursor.fetchall()
    cursor.execute('SELECT SUM(quantity) FROM order_detail')
    sum_quantity = cursor.fetchall()
    cursor.execute("SELECT count(*) FROM product_reviews WHERE rating ='5'")
    star5 = cursor.fetchall()
    cursor.execute("SELECT count(*) FROM product_reviews WHERE rating ='4'")
    star4 = cursor.fetchall()
    cursor.execute("SELECT count(*) FROM product_reviews WHERE rating ='3'")
    star3 = cursor.fetchall()
    cursor.execute("SELECT count(*) FROM product_reviews WHERE rating ='2'")
    star2 = cursor.fetchall()
    cursor.execute("SELECT count(*) FROM product_reviews WHERE rating ='1'")
    star1 = cursor.fetchall()
    cursor.execute('''
        SELECT 
            SUM(rating) AS total_rating, 
            COUNT(*) AS num_reviews
        FROM 
            product_reviews
        
    ''')
    result = cursor.fetchone()
    if result and result[1] > 0:
        average_rating = result[0] / result[1]
        average_rating = round(average_rating, 1)
    else:
        average_rating = 0.0
    conn.commit()
    conn.close()
    return render_template("Template_Admin/dashboard.html", count_user=count_user,revenue=revenue, count_mess=count_mess, orders=orders, 
                           posts = post, count_delivered=delivered,
                           cancel=cancel,
                           shipping = shipping,
                           processing =processing,
                           sum_quantity = sum_quantity,
                           star5 =star5, star4 =star4, star3 =star3, star2 =star2, star1 =star1, average_rating=average_rating
                           )
if __name__ == '__main__':
    app.run(debug=True) 