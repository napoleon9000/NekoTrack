import streamlit as st
from backend.order_mgr import OrderManager as Manager
from models.orders import Order, OrderStatus, PlushieType
from io import BytesIO

import logging
logger = logging.getLogger(__name__)

def create_order(order_id, manager: Manager):
    manager.create_order(order_id)
    st.success("Order created successfully")


def app():
    st.title("Add Order")

    st.markdown("---")

    # show order creation form
    env = st.secrets['ENV']['ENV']
    manager = Manager(env)
    col1, col2 = st.columns([2, 7])
    with col1: 
        image = st.file_uploader("Image", type=["jpg", "png"])
        if image:
            st.image(image, width=250)
    with col2:
        with st.form(key='create_order_form', border=False):
            name = st.text_input("Name")
            cols = st.columns(2)
            with cols[0]:
                seller = st.text_input("Seller")
            with cols[1]:
                preset_seller = st.selectbox("Preset Seller", [None, "Temu", "New York"])
            status = st.selectbox("Status", [status.value for status in OrderStatus])
            tracking_number = st.text_input("Tracking Number")
            amount = st.number_input("Amount", min_value=1, step=1)
            plushie_type = st.selectbox("Plushie Type", [type.value for type in PlushieType])
            price = st.number_input("Price", min_value=0.0, step=0.01, format="%.2f")
            shipping_cost = st.number_input("Shipping Cost", min_value=0.0, step=0.01, format="%.2f")
            shipping_date = st.date_input("Shipping Date")
            expected_deliver_date = st.date_input("Expected Delivery Date")
            notes = st.text_area("Notes")

            if st.form_submit_button("Save"):
                new_order = Order(
                    name=name,
                    seller=preset_seller if not seller else seller,
                    status=OrderStatus(status),
                    tracking_number=tracking_number,
                    amount=amount,
                    plushie_type=PlushieType(plushie_type),
                    price=price,
                    shipping_cost=shipping_cost,
                    shipping_date=shipping_date,
                    expected_deliver_date=expected_deliver_date,
                    notes=notes
                )
                if image is not None:   
                    img_bytesio = BytesIO(image.getvalue())
                    manager.create_order(new_order, img_bytesio)
                else:
                    manager.create_order(new_order, None)
                st.success("Order created successfully")