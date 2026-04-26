from app import db
from app.models.product import Product


def get_all_products():
    return Product.query.all()


def get_product(product_id):
    return Product.query.get_or_404(product_id)


def create_product(data, user):
    product = Product(
        title=data["title"],
        price=data["price"],
        seller_id=user.id
    )
    db.session.add(product)
    db.session.commit()
    return product