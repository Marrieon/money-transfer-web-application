from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from decimal import Decimal
from app.extensions import db
from app.models import User, Transaction
from app.services.transaction_service import create_transfer, create_multicurrency_transfer
from app.services.audit_service import log_action
from app.utils.exceptions import InvalidUsage
from app.utils.jwt_utils import get_current_user_id

transactions_bp = Blueprint('transactions_bp', __name__)

class TransferAPI(MethodView):
    decorators = [jwt_required()]
    def post(self):
        """
        Create a new single-currency peer-to-peer transfer.
        ---
        tags:
          - Transactions
        description: Sends money from the authenticated user to another user identified by their phone number. The transaction occurs in the sender's default currency.
        security:
          - bearerAuth: []
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  receiver_phone:
                    type: string
                    example: "2222222222"
                  amount:
                    type: string
                    example: "25.50"
        responses:
          201:
            description: Transfer was successful.
          400:
            description: Bad request due to invalid input, insufficient funds, or a security flag.
          401:
            description: Unauthorized.
        """
        sender_id = get_current_user_id()
        data = request.get_json()
        
        receiver_phone = data.get('receiver_phone')
        amount_str = data.get('amount')

        if not receiver_phone or not amount_str:
            raise InvalidUsage("receiver_phone and amount are required.")

        try:
            amount = Decimal(amount_str)
        except:
            raise InvalidUsage("Invalid amount format.")
            
        # The service function now handles the commit
        transaction = create_transfer(sender_id=sender_id, receiver_phone=receiver_phone, amount=amount)
        
        log_action("transfer_success", user_id=sender_id, details={
            'transaction_id': transaction.id, 
            'amount': float(amount),
            'receiver_phone': receiver_phone
        })
        
        # The service already commits, so we remove the redundant commit here.
        # db.session.commit()

        return jsonify({
            "message": "Transfer successful",
            "transaction_id": transaction.id,
            "status": transaction.status
        }), 201

class TransactionHistoryAPI(MethodView):
    decorators = [jwt_required()]
    def get(self):
        """
        Get the transaction history for the current user.
        ---
        tags:
          - Transactions
        description: Retrieves a list of all transactions, both sent and received, for the authenticated user, sorted by most recent first.
        security:
          - bearerAuth: []
        responses:
          200:
            description: A list of the user's transactions.
          401:
            description: Unauthorized.
        """
        user_id = get_current_user_id()
        user = db.session.get(User, user_id)
        
        sent = user.transactions_sent.order_by(Transaction.created_at.desc()).all()
        received = user.transactions_received.order_by(Transaction.created_at.desc()).all()
        
        history = [
            {
                "id": t.id,
                "type": "sent",
                "amount": float(t.amount),
                "fee": float(t.fee),
                "to_phone": t.receiver.phone,
                "status": t.status,
                "date": t.created_at.isoformat(),
                "category": t.category
            } for t in sent
        ] + [
            {
                "id": t.id,
                "type": "received",
                "amount": float(t.amount),
                "from_phone": t.sender.phone,
                "status": t.status,
                "date": t.created_at.isoformat(),
                "category": t.category
            } for t in received
        ]
        
        history.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify(history)

class MultiCurrencyTransferAPI(MethodView):
    decorators = [jwt_required()]
    def post(self):
        """
        Create a new multi-currency peer-to-peer transfer.
        ---
        tags:
          - Transactions
        description: Sends money from the authenticated user in their currency to a receiver in a different target currency. Requires a real-time exchange rate lookup.
        security:
          - bearerAuth: []
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  receiver_phone:
                    type: string
                    example: "2222222222"
                  amount:
                    type: string
                    description: "The amount the SENDER is sending in their currency."
                    example: "100.00"
                  target_currency:
                    type: string
                    description: "The currency the RECEIVER should get (e.g., EUR, GBP)."
                    example: "EUR"
        responses:
          201:
            description: Transfer was successful.
          400:
            description: Bad request due to invalid input or failed exchange rate lookup.
          401:
            description: Unauthorized.
        """
        sender_id = get_current_user_id()
        data = request.get_json()

        receiver_phone = data.get('receiver_phone')
        send_amount_str = data.get('amount')
        target_currency = data.get('target_currency')

        if not all([receiver_phone, send_amount_str, target_currency]):
            raise InvalidUsage("receiver_phone, amount, and target_currency are required.")

        try:
            send_amount = Decimal(send_amount_str)
        except:
            raise InvalidUsage("Invalid amount format.")

        transaction = create_multicurrency_transfer(
            sender_id=sender_id,
            receiver_phone=receiver_phone,
            send_amount=send_amount,
            target_currency=target_currency.upper()
        )
        
        log_action("multicurrency_transfer_success", user_id=sender_id, details={
            'transaction_id': transaction.id, 
            'amount': float(send_amount),
            'target_currency': target_currency.upper(),
            'receiver_phone': receiver_phone
        })
        
        # The service already commits, so we remove the redundant commit here.
        # db.session.commit()

        return jsonify({
            "message": "Multi-currency transfer successful",
            "transaction_id": transaction.id
        }), 201

# Registering the URL rules
transactions_bp.add_url_rule('/transfer', view_func=TransferAPI.as_view('transfer_api'))
transactions_bp.add_url_rule('/transfer/multicurrency', view_func=MultiCurrencyTransferAPI.as_view('multicurrency_transfer_api'))
transactions_bp.add_url_rule('/history', view_func=TransactionHistoryAPI.as_view('history_api'))
