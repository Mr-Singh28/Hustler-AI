# src/brand_research/routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src import db
from src.models import User, SimilarBrand
from src.brand_research.brand_search import search_similar_brands

brand_research_bp = Blueprint('brand_research', __name__)

@brand_research_bp.route('/research', methods=['POST'])
@jwt_required()
def research_brand():
    """
    API endpoint to research similar brands based on a given brand name.
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    brand_name = data.get('brand_name')

    if not brand_name:
        return jsonify({"message": "Brand name is required"}), 400

    # Call the function to search for similar brands
    similar_brands = search_similar_brands(brand_name)

    # Store the results in the database
    for brand in similar_brands:
        new_brand = SimilarBrand(
            user_id=current_user_id,
            name=brand['name'],
            description=brand['description']
        )
        db.session.add(new_brand)

    db.session.commit()

    return jsonify({"message": "Brand research completed successfully"}), 200

# Other routes...
