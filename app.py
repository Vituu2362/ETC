from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode
from io import BytesIO
from flask import send_file
import requests
from datetime import datetime
import random
import uuid

# Initialize Flask application and database
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with your secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///PlateSync.db'  # Replace with your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoid SQLAlchemy warning

db = SQLAlchemy(app)



# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# User model
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    # Relationship to Wallet model
    wallet = db.relationship('Wallet', back_populates='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# User loader function required by Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Pass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pass_type = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    toll_name = db.Column(db.String(100))
    vehicle_number = db.Column(db.String(20))
    owner_name = db.Column(db.String(100))  # Keep this field for the owner's name
    mobile_number = db.Column(db.String(15))
    amount = db.Column(db.Float)

class Wallet(db.Model):
    __tablename__ = 'wallets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    balance = db.Column(db.Float, default=0.0)  # Default balance is 0

    # Relationship to User model
    user = db.relationship('User', back_populates='wallet')

    def add_funds(self, amount):
        """Add funds to the wallet balance."""
        self.balance += amount
        db.session.commit()

    def deduct_funds(self, amount):
        """Deduct funds from the wallet balance."""
        if self.balance >= amount:
            self.balance -= amount
            db.session.commit()
        else:
            raise ValueError("Insufficient balance.")

# Create tables
with app.app_context():
    db.create_all()

@app.route('/generate_qr/<int:pass_id>')
@login_required
def generate_qr(pass_id):
    # Query the pass details by ID
    toll_pass = Pass.query.get_or_404(pass_id)

    # Prepare data to encode in the QR code (pass details)
    qr_data = f"""
    Pass Type: {toll_pass.pass_type}
    Vehicle Number: {toll_pass.vehicle_number}
    Start Date: {toll_pass.start_date}
    End Date: {toll_pass.end_date}
    Toll Gate: {toll_pass.toll_name}
    Amount: Mwk {toll_pass.amount}
    """

    # Generate QR code
    qr_img = qrcode.make(qr_data)

    # Save QR code to a BytesIO object (in-memory)
    img_io = BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)

    # Return the QR code as a file download
    return send_file(img_io, mimetype='image/png', as_attachment=False, download_name='toll_pass_qr.png')


# Routes
@app.route('/')
def loader_welcome():
    return render_template('loader_welcome.html')

@app.route('/welcome')
def welcome():
    weather_api_key = 'b9a10895372dd47e7b0871f75491c038'
    city = 'Mangochi'
    weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric'
    
    try:
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather = weather_response.json()
    except requests.exceptions.RequestException as e:
        weather = None
        print(f"Error fetching weather data: {e}")
    
    news_api_key = '5e38df53c0f8427e80efe099c7d11048'
    news_url = f'https://newsapi.org/v2/top-headlines?country=mw&apiKey={news_api_key}'
    
    try:
        news_response = requests.get(news_url)
        news_response.raise_for_status()
        news = news_response.json()
    except requests.exceptions.RequestException as e:
        news = {'articles': []}
        print(f"Error fetching news data: {e}")

    return render_template('welcome.html', weather=weather, news=news)





@app.route('/loader')
def loader():
    return render_template('user/loader.html')

@app.route('/developer')
def developer():
    return render_template('developer.html')

@app.route('/create_dept', methods=['GET', 'POST'])
@login_required
def create_dept():
    # Send a request to PayChangu to get supported operators
    response = requests.get('https://api.paychangu.com/mobile-money/', headers={
        'Authorization': 'Bearer SEC-TEST-zLPnUTHOV621FRoNngepoasIErt1NW9k'
    })

    if response.status_code == 200:
        data = response.json()
        # Access operators from the 'data' key
        if 'data' in data:
            operators = data['data']  # List of operators from the API
        else:
            operators = []
            flash('No operators found in the API response.', 'warning')
    else:
        operators = []
        flash('Failed to fetch operators. Please try again.', 'danger')

    # Render the e_wallet template with the list of operators
    return render_template('user/create_dept.html', operators=operators)

@app.route('/add_money', methods=['GET', 'POST'])
@login_required
def add_money():
    amount = request.form.get('amount')
    operator = request.form.get('operator')
    mobile = request.form.get('mobile')  # Assuming you're getting the user's mobile from the form
    user_id = current_user.id

    # Validate amount
    try:
        amount = str(float(amount))  # Convert amount to string as required by the API
    except ValueError:
        flash('Invalid amount entered. Please enter a valid number.', 'danger')
        return redirect(url_for('loader'))

    # Ensure operator is selected
    if not operator:
        flash('Please select a mobile operator.', 'danger')
        return redirect(url_for('loader'))

    # Ensure mobile number is provided
    if not mobile:
        flash('Please provide a valid mobile number.', 'danger')
        return redirect(url_for('billing'))

    # Generate a unique charge_id for the transaction
    charge_id = str(uuid.uuid4())

    # Prepare the payload for PayChangu API
    payload = {
        'mobile': mobile,
        'mobile_money_operator_ref_id': operator,  # Operator reference ID from the form
        'amount': amount,
        'charge_id': charge_id,  # Unique identifier for the transaction
        'email': current_user.email,  # Optional: email for transaction notification

    }

    # Define headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'SEC-TEST-zLPnUTHOV621FRoNngepoasIErt1NW9k'  # Replace with your actual secret key
    }

    # Correct PayChangu endpoint for initializing a payout
    url = 'https://api.paychangu.com/mobile-money/payouts/initialize'

    # Send the POST request to PayChangu API
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        transaction_data = response.json()

        if transaction_data.get('status') == 'success':
            # Update the user's wallet balance
            user = User.query.get(user_id)
            user.wallet_balance += float(amount)  # Add the funds to the user's wallet
            db.session.commit()

            flash('Money added successfully!', 'success')
        else:
            # Handle payment failure
            flash('Payment failed: ' + transaction_data.get('message', 'Unknown error'), 'danger')

    except requests.exceptions.HTTPError as http_err:
        flash(f'HTTP error occurred: {http_err}', 'danger')
    except requests.exceptions.Timeout:
        flash('The request timed out. Please try again later.', 'danger')
    except requests.exceptions.RequestException as req_err:
        flash(f'Error processing payment: {str(req_err)}', 'danger')

    return redirect(url_for('billing'))



@app.route('/admin_update_info')
@login_required
def admin_update_info():
    x = "some value"
    return render_template('user/admin_update_info.html', x=x)

# Define toll pass prices
PASS_PRICES = {
    'motorbike': 1000,
    'car': 1000,
    'mini bus': 2000,
    'lorry': 4000,
    'heavy goods vehicle': 5000
}

# Define multipliers for durations
DURATION_MULTIPLIER = {
    'weekly': 7,
    'monthly': 30,
    'annually': 365
}

@app.route('/view_toll_pay', methods=['GET', 'POST'])
def view_toll_pay():
    if request.method == 'POST':
        # Get form data
        pass_type = request.form.get('pass_type')
        duration = request.form.get('duration')

        # Calculate total amount based on pass type and duration
        base_price = PASS_PRICES.get(pass_type)
        duration_multiplier = DURATION_MULTIPLIER.get(duration)
        total_amount = base_price * duration_multiplier

        # Redirect to payment page with the calculated total amount
        return redirect(url_for('pay_toll_ticket', amount=total_amount))

    return render_template('user/view_toll_pay.html')

@app.route('/pay_toll_ticket', methods=['GET'])
def pay_toll_ticket():
    # Get the total amount from query parameters
    amount = request.args.get('amount', type=int)

    # Simulate a unique transaction reference
    tx_ref = str(random.randint(1000000000, 9999999999))

    # Render payment page
    return render_template('user/pay_toll_ticket.html', amount=amount, tx_ref=tx_ref, username=current_user.username, email=current_user.email)

@app.route('/payment-success')
@login_required
def payment_success():
    charge_id = request.args.get('tx_ref')  # Get the charge_id (tx_ref) from the callback
    if charge_id:
        # Redirect to a new page or route where you fetch the transfer details
        return redirect(url_for('fetch_transfer', charge_id=charge_id))
    else:
        flash('Payment failed or invalid charge ID.', 'danger')
        return redirect(url_for('billing'))


@app.route('/fetch_transfer/<charge_id>')
def fetch_transfer(charge_id):
    url = f"https://api.paychangu.com/mobile-money/payments/{charge_id}/details"
    
    # Set up headers
    headers = {
        "Accept": "application/json",
        "Authorization": 'SEC-TEST-zLPnUTHOV621FRoNngepoasIErt1NW9k'
    }

    try:
        # Make GET request to the PayChangu API
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        transfer_data = response.json()

        if transfer_data.get('status') == 'success':
            transaction_details = transfer_data['data']
            return render_template('transaction_details.html', details=transaction_details)
        else:
            flash(f"Error fetching details: {transfer_data.get('message', 'Unknown error')}", 'danger')
            return redirect(url_for('billing'))  # Redirect to a payment page if needed

    except requests.exceptions.RequestException as e:
        flash(f"Error processing request: {str(e)}", 'danger')
        return redirect(url_for('billing'))


@app.route('/my_ticket')
@login_required
def my_ticket():
    x = "some value"
    return render_template('user/my_ticket.html', x=x)

@app.route('/billing')
@login_required
def billing():
    passes = Pass.query.all()  # Get all passes or filter as needed
    return render_template('user/billing.html', username=current_user.username, email=current_user.email, passes=passes)


@app.route('/edit_pass/<int:pass_id>', methods=['GET', 'POST'])
@login_required
def edit_pass(pass_id):
    # Get the pass to edit
    pass_to_edit = Pass.query.get_or_404(pass_id)
    
    if request.method == 'POST':
        # Update the pass details
        pass_to_edit.pass_type = request.form['pass_type']
        pass_to_edit.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()  # Convert to date
        pass_to_edit.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()      # Convert to date
        pass_to_edit.vehicle_number = request.form['vehicle_number']
        pass_to_edit.toll_name = request.form['toll_name']
        pass_to_edit.amount = float(request.form['amount'])  # Convert amount to float
        
        try:
            db.session.commit()
            flash('Pass updated successfully!', 'success')
            return redirect(url_for('billing'))  # Adjust if you want to stay on the same page
        except:
            db.session.rollback()
            flash('An error occurred while updating the pass.', 'danger')
    
    return render_template('user/edit_pass.html', pass_to_edit=pass_to_edit)



@app.route('/profile')
@login_required
def profile():
    x = "some value"
    return render_template('user/profile.html', x=x, username=current_user.username, email=current_user.email)

@app.route('/create_application')
@login_required
def create_application():
    x = "some value"
    return render_template('user/create_application.html', x=x, username=current_user.username, email=current_user.email)

@app.route('/my_application')
@login_required
def my_application():
    x = "some value"
    return render_template('user/my_application.html', x=x)

@app.route('/view_all_result')
@login_required
def view_all_result():
    x = "some value"
    return render_template('admin/view_all_result.html', x=x)

@app.route('/create_bus')
@login_required
def create_bus():
    x = "some value"
    return render_template('admin/create_bus.html', x=x)

@app.route('/create_employee')
@login_required
def create_employee():
    x = "some value"
    return render_template('admin/create_employee.html', x=x)

@app.route('/view_employee')
@login_required
def view_employee():
    x = "some value"
    return render_template('admin/view_employee.html', x=x)

@app.route('/view_employee_info')
@login_required
def view_employee_info():
    x = "some value"
    return render_template('admin/view_employee_info.html', x=x)

@app.route('/view_toll')
@login_required
def view_toll():
    x = "some value"
    return render_template('admin/view_toll.html', x=x)

@app.route('/view_toll_geo_user')
@login_required
def view_toll_geo_user():
    google_maps_url = "https://www.google.com/maps?client=ubuntu&hs=ejK&sca_esv=f9fa188a74abf180&output=search&q=chingeni+toll+plaza+map&source=lnms&fbs=AEQNm0Aa4sjWe7Rqy32pFwRj0UkWd8nbOJfsBGGB5IQQO6L3J3ppPdoHI1O-XvbXbpNjYYwWUVH6qTfR1Lpek5F-7GS5kHUv-XPg6sWhVG4k1EjbnJtLhBeL57sTXxXmiHxC27t3XXUxCvX_qlf7Bkns-G8lz6MIVRlNzq1Cqfjzvt-wjRfYPf8&entry=mc&ved=1t:200715&ictx=111"
    return render_template('user/view_toll_geo_user.html', google_maps_url=google_maps_url)

@app.route('/price_table')
def price_table():
    return render_template('price_table.html')

@app.route('/about')
def about():
    return render_template('about.html')

from datetime import datetime

@app.route('/add-pass', methods=['POST'])
@login_required
def add_pass():
    data = request.form
    try:
        # Convert date strings to Python date objects
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

        new_pass = Pass(
            pass_type=data['pass_type'],
            start_date=start_date,  # Use the converted date object
            end_date=end_date,      # Use the converted date object
            toll_name=data['toll_name'],
            vehicle_number=data['vehicle_number'],
            owner_name=data['owner_name'],  # Use owner_name from form data
            mobile_number=data['mobile_number'],
            amount=float(data['amount'])
        )
        db.session.add(new_pass)
        db.session.commit()

        return jsonify({"message": "Toll pass added successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400






@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please use a different one.', 'error')
        else:
            new_user = User(email=email, username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully. You can now log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('loader'))

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    return render_template('user/user_dashboard.html', username=current_user.username, email=current_user.email)

@app.route('/user/location')
@login_required
def location():
    return render_template('user/location.html', username=current_user.username, email=current_user.email)


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template('admin/admin_dashboard.html', username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('welcome'))

if __name__ == '__main__':
    app.run(debug=True)
