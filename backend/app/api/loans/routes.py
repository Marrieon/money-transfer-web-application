from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from datetime import date
from decimal import Decimal
from app.extensions import db
from app.models import User, Loan
from app.services.notification_service import create_notification
from app.utils.exceptions import InvalidUsage, NotFound
from app.utils.jwt_utils import get_current_user_id

loans_bp = Blueprint('loans_bp', __name__)

class LoanAPI(MethodView):
    decorators = [jwt_required()]

    def get(self):
        """
        Get all loans involving the user (as lender or borrower).
        ---
        tags:
          - Loans
        description: Retrieves two lists of loans for the authenticated user - one for loans they have lent to others, and one for loans they have borrowed.
        security:
          - bearerAuth: []
        responses:
          200:
            description: Successfully retrieved loan portfolio.
          401:
            description: Unauthorized.
        """
        user_id = get_current_user_id()
        loans_lent = Loan.query.filter_by(lender_id=user_id).all()
        loans_borrowed = Loan.query.filter_by(borrower_id=user_id).all()
        
        return jsonify({
            "lent": [{"id": l.id, "borrower": l.borrower.email, "amount": float(l.amount), "status": l.status} for l in loans_lent],
            "borrowed": [{"id": l.id, "lender": l.lender.email, "amount": float(l.amount), "status": l.status} for l in loans_borrowed]
        })

    def post(self):
        """
        Request a loan from another user.
        ---
        tags:
          - Loans
        description: Creates a new loan request from the authenticated user (borrower) to another user (lender), identified by their phone number. A notification is sent to the lender.
        security:
          - bearerAuth: []
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  lender_phone:
                    type: string
                    example: "2222222222"
                  amount:
                    type: string
                    example: "250.00"
                  interest_rate:
                    type: number
                    format: float
                    example: 5.5
                  repayment_date:
                    type: string
                    format: date
                    example: "2026-01-31"
                required:
                  - lender_phone
                  - amount
                  - repayment_date
        responses:
          201:
            description: Loan requested successfully.
          400:
            description: Bad request due to missing fields or invalid data formats.
          401:
            description: Unauthorized.
          404:
            description: Lender with the specified phone number not found.
        """
        borrower_id = get_current_user_id()
        data = request.get_json()
        
        lender_phone = data.get('lender_phone')
        amount_str = data.get('amount')
        interest_rate = data.get('interest_rate', 5.0)
        repayment_date_str = data.get('repayment_date')

        if not all([lender_phone, amount_str, repayment_date_str]):
            raise InvalidUsage("lender_phone, amount, and repayment_date are required.")

        lender = User.query.filter_by(phone=lender_phone).first()
        if not lender:
            raise NotFound("Lender not found with that phone number.")
        
        borrower = db.session.get(User, borrower_id)

        try:
            amount = Decimal(amount_str)
            repayment_date_obj = date.fromisoformat(repayment_date_str)
        except (ValueError, TypeError):
            raise InvalidUsage("Invalid data format. Please use a valid amount and YYYY-MM-DD for the date.")

        loan = Loan(
            lender_id=lender.id,
            borrower_id=borrower.id,
            amount=amount,
            interest_rate=interest_rate,
            repayment_date=repayment_date_obj
        )
        db.session.add(loan)
        
        message = f"{borrower.first_name} has requested a loan of {amount} from you."
        create_notification(lender.id, message, 'loan_request')
        
        db.session.commit()
        return jsonify({"message": "Loan requested successfully.", "loan_id": loan.id}), 201

loans_bp.add_url_rule('/', view_func=LoanAPI.as_view('loan_api'), methods=['GET', 'POST'])
