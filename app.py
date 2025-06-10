from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message
from datetime import datetime, timedelta, timezone
import stripe
import config

app = Flask(__name__)
app.config.from_object(config)

stripe.api_key = app.config['STRIPE_SECRET_KEY']
mail = Mail(app)

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/generate-coupon', methods=['POST'])
def generate_coupon():
    data = request.get_json()

    user_id = data.get("user_id")
    
    user = {"email": "aabakah@caltech.edu", "plan": "free" if user_id == "1" else "paid"}

    discount = 20 if user["plan"] == "paid" else 10
    expiration = datetime.now(timezone.utc) + timedelta(days=7)

    coupon = stripe.Coupon.create(
        percent_off=discount,
        duration="once"
    )

    promo = stripe.PromotionCode.create(
        coupon=coupon.id,
        max_redemptions=1,
        expires_at=int(expiration.timestamp()),
        metadata={"user_id": user_id}
    )

    msg = Message("Your Discount Code",
                  recipients=[user["email"]])
    msg.body = f"Hi there,\n\nHere’s your {discount}% off code: {promo.code}\nIt expires in 7 days.\n\nThanks!"
    mail.send(msg)

    return jsonify({"message": "Coupon sent", "code": promo.code})
