from flask import Blueprint, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import InsuranceProduct, UserInsurancePolicy
from app.services.insurance_service import purchase_insurance
from app.utils.decorators import admin_required
from app.utils.jwt_utils import get_current_user_id

insurance_bp = Blueprint('insurance_bp', __name__)

class InsuranceProductAPI(MethodView):

    def get(self):
        """
        (Public) Get a list of all available insurance products.
        ---
        tags:
          - Insurance
        description: Retrieves a list of all currently active insurance products that users can purchase. This endpoint is public and requires no authentication.
        responses:
          200:
            description: A list of insurance products.
        """
        products = InsuranceProduct.query.filter_by(is_active=True).all()
        return jsonify([{
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "coverage_amount": float(p.coverage_amount),
            "premium_amount": float(p.premium_amount)
        } for p in products])

    @admin_required()
    def post(self):
        """
        (Admin) Create a new insurance product.
        ---
        tags:
          - Insurance
        description: Allows an admin user to create a new insurance product that will be available for purchase.
        security:
          - bearerAuth: []
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                properties:
                  name:
                    type: string
                    example: "Gadget Protection Plan"
                  description:
                    type: string
                    example: "One year of protection for your new electronic device."
                  coverage_amount:
                    type: number
                    format: float
                    example: 500.00
                  premium_amount:
                    type: number
                    format: float
                    example: 49.99
        responses:
          201:
            description: Insurance product created successfully.
          401:
            description: Unauthorized (only admins can access this).
        """
        data = request.get_json()
        product = InsuranceProduct(**data)
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Insurance product created", "id": product.id}), 201

class PurchaseInsuranceAPI(MethodView):
    decorators = [jwt_required()]

    def post(self, product_id):
        """
        Purchase an insurance policy.
        ---
        tags:
          - Insurance
        description: Allows an authenticated user to purchase a specific insurance product. The premium is deducted from the user's main wallet.
        security:
          - bearerAuth: []
        parameters:
          - in: path
            name: product_id
            required: true
            schema:
              type: integer
            description: The ID of the insurance product to purchase.
        responses:
          201:
            description: Policy purchased successfully.
          400:
            description: Bad request, usually due to insufficient funds.
          401:
            description: Unauthorized.
          404:
            description: Product not found or is not active.
        """
        user_id = get_current_user_id()
        policy = purchase_insurance(user_id, product_id)
        return jsonify({"message": "Policy purchased successfully", "policy_id": policy.id}), 201

class UserPoliciesAPI(MethodView):
    decorators = [jwt_required()]

    def get(self):
        """
        Get all policies owned by the current user.
        ---
        tags:
          - Insurance
        description: Retrieves a list of all insurance policies currently and previously owned by the authenticated user.
        security:
          - bearerAuth: []
        responses:
          200:
            description: A list of the user's insurance policies.
          401:
            description: Unauthorized.
        """
        user_id = get_current_user_id()
        policies = UserInsurancePolicy.query.filter_by(user_id=user_id).all()
        return jsonify([{
            "id": p.id,
            "product_name": p.product.name,
            "status": p.status,
            "end_date": p.end_date.isoformat()
        } for p in policies])

# Public routes
insurance_bp.add_url_rule('/products', view_func=InsuranceProductAPI.as_view('insurance_product_api'), methods=['GET', 'POST'])
# User-specific routes
insurance_bp.add_url_rule('/purchase/<int:product_id>', view_func=PurchaseInsuranceAPI.as_view('purchase_insurance_api'), methods=['POST'])
insurance_bp.add_url_rule('/policies', view_func=UserPoliciesAPI.as_view('user_policies_api'), methods=['GET'])
