from flask import Blueprint, jsonify, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from decimal import Decimal
from app.models import User
from app.extensions import db
from app.services.wallet_service import deposit_to_wallet, withdraw_from_wallet
from app.utils.exceptions import InvalidUsage
from app.utils.jwt_utils import get_current_user_id

wallets_bp = Blueprint('wallets_bp', __name__)

class WalletAPI(MethodView):
    decorators = [jwt_required()]

    def get(self):
        """
        Get current user's wallet details.
        ---
        tags:
          - Wallet
        description: Retrieves the balance, currency, and status of the authenticated user's primary wallet.
        security:
          - bearerAuth: []
        responses:
          200:
            description: Wallet details successfully retrieved.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    id:
                      type: integer
                    currency:
                      type: string
                      example: "USD"
                    balance:
                      type: number
                      format: float
                      example: 100.00
                    status:
                      type: string
                      example: "active"
          401:
            description: Unauthorized.
          404:
            description: Wallet not found for the user.
        """
        user_id = get_current_user_id()
        user = db.session.get(User, user_id)
        if not user or not user.wallet:
            return jsonify({"message": "Wallet not found"}), 404

        wallet = user.wallet
        return jsonify({
            "id": wallet.id,
            "currency": wallet.currency,
            "balance": float(wallet.balance),
            "status": wallet.status
        })

class WalletActionAPI(MethodView):
    decorators = [jwt_required()]
    
    def post(self, action):
        """
        Deposit or withdraw funds from the wallet.
        ---
        tags:
          - Wallet
        description: Performs an action (either 'deposit' or 'withdraw') on the user's wallet.
        security:
          - bearerAuth: []
        parameters:
          - in: path
            name: action
            required: true
            schema:
              type: string
              enum: [deposit, withdraw]
            description: The action to perform on the wallet.
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  amount:
                    type: string
                    example: "50.25"
                required:
                  - amount
        responses:
          200:
            description: Action was successful.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    message:
                      type: string
                      example: "Deposit successful"
                    new_balance:
                      type: number
                      format: float
                      example: 150.25
          400:
            description: Bad request due to invalid action, invalid amount, or insufficient funds.
          401:
            description: Unauthorized.
        """
        user_id = get_current_user_id()
        data = request.get_json()
        
        try:
            amount = Decimal(data.get('amount'))
        except:
            raise InvalidUsage("Invalid amount format.")
            
        if action == 'deposit':
            wallet = deposit_to_wallet(user_id, amount)
        elif action == 'withdraw':
            wallet = withdraw_from_wallet(user_id, amount)
        else:
            return jsonify({"message": "Invalid action"}), 400
        
        db.session.commit()
        return jsonify({
            "message": f"{action.capitalize()} successful",
            "new_balance": float(wallet.balance)
        })

wallets_bp.add_url_rule('/', view_func=WalletAPI.as_view('wallet_api'))
# Allow clients that omit the trailing slash to avoid preflight redirects.
wallets_bp.add_url_rule('', view_func=WalletAPI.as_view('wallet_api_no_slash'))
wallets_bp.add_url_rule('/<string:action>', view_func=WalletActionAPI.as_view('wallet_action_api'))
