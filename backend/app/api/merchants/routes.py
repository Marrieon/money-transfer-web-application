from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from app.models import Merchant
from app.services.merchant_service import create_merchant_account, process_merchant_payment
from app.utils.jwt_utils import get_current_user_id

merchants_bp = Blueprint('merchants_bp', __name__)

class MerchantAccountAPI(MethodView):
    
    @jwt_required()
    def get(self):
        """
        Get the current user's merchant account details.
        ---
        tags:
          - Merchants
        description: Retrieves the business name, API key, and status for the authenticated user's merchant account.
        security:
          - bearerAuth: []
        responses:
          200:
            description: Merchant account details successfully retrieved.
          401:
            description: Unauthorized.
          404:
            description: The user does not have a merchant account.
        """
        user_id = get_current_user_id()
        merchant = Merchant.query.filter_by(user_id=user_id).first_or_404(description="Merchant account not found.")
        return jsonify({
            "id": merchant.id,
            "business_name": merchant.business_name,
            "api_key": merchant.api_key,
            "is_active": merchant.is_active
        })
        
    @jwt_required()
    def post(self):
        """
        Create a merchant account for the current user.
        ---
        tags:
          - Merchants
        description: Creates a new merchant account linked to the authenticated user. Each user can only have one merchant account.
        security:
          - bearerAuth: []
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  business_name:
                    type: string
                    example: "Newton's Gadgets"
                required:
                  - business_name
        responses:
          201:
            description: Merchant account created successfully. Returns the new API key.
          400:
            description: Bad request, user may already have a merchant account.
          401:
            description: Unauthorized.
        """
        user_id = get_current_user_id()
        data = request.get_json()
        merchant = create_merchant_account(user_id, data.get('business_name'))
        return jsonify({"message": "Merchant account created", "api_key": merchant.api_key}), 201

class MerchantPaymentAPI(MethodView):
    
    def post(self):
        """
        (Public) Process a payment from a customer to a merchant.
        ---
        tags:
          - Merchants
        description: A public endpoint for merchants to process payments. Authentication is handled via an API key passed in the 'X-API-KEY' header.
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  amount:
                    type: string
                    example: "19.99"
                  customer_phone:
                    type: string
                    example: "1111111111"
                required:
                  - amount
                  - customer_phone
        parameters:
          - in: header
            name: X-API-KEY
            required: true
            schema:
              type: string
            description: The merchant's unique API key for authentication.
        responses:
          200:
            description: Payment was processed successfully.
          401:
            description: Unauthorized due to missing or invalid API key.
          404:
            description: Merchant or customer not found.
        """
        data = request.get_json()
        api_key = request.headers.get('X-API-KEY')
        
        if not api_key:
            return jsonify({"message": "API key is missing from headers."}), 401

        transaction = process_merchant_payment(
            api_key=api_key,
            amount=data.get('amount'),
            customer_phone=data.get('customer_phone')
        )
        return jsonify({"message": "Payment successful", "transaction_id": transaction.id})

# Routes for logged-in users to manage their merchant account
merchants_bp.add_url_rule('/account', view_func=MerchantAccountAPI.as_view('merchant_account_api'), methods=['GET', 'POST'])
# Public route for processing payments
merchants_bp.add_url_rule('/pay', view_func=MerchantPaymentAPI.as_view('merchant_payment_api'), methods=['POST'])
