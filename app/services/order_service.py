from app import db
from app.models.order import Order
from app.models.product import Product


def place_order(user, product_id):
    product = Product.query.get_or_404(product_id)

    if product.seller_id == user.id:
        return None, "You cannot buy your own product."

    existing = Order.query.filter_by(
        buyer_id=user.id,
        product_id=product.id
    ).first()

    if existing:
        return None, "You already ordered this product."

    new_order = Order(
        buyer_id=user.id,
        product_id=product.id,
        status="Pending"
    )

    db.session.add(new_order)
    db.session.commit()

    return new_order, None


def get_user_orders(user):
    return Order.query.filter_by(
        buyer_id=user.id
    ).order_by(Order.ordered_at.desc()).all()


def get_seller_orders(user):
    return Order.query.join(Product).filter(
        Product.seller_id == user.id
    ).order_by(Order.ordered_at.desc()).all()


def complete_order(user, order_id):
    order = Order.query.get_or_404(order_id)

    if order.product.seller_id != user.id:
        return "Unauthorized"

    order.status = "Completed"
    db.session.commit()

    return None