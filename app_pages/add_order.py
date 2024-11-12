import streamlit as st
from backend.order_mgr import OrderManager as Manager
from models.orders import Order, OrderStatus, PlushieType
from io import BytesIO

import logging
logger = logging.getLogger(__name__)

preset_seller_options = ["Temu", "New York", "1688", "Mengai"]

def create_order(order_id, manager: Manager):
    manager.create_order(order_id)
    st.success("Order created successfully")

def get_value(data, key, default=None):
    return data.get(key, default) if data is not None else default

def app():
    if 'selected_order_for_duplicate' in st.session_state:
        dup_order = st.session_state['selected_order_for_duplicate']
    else:
        dup_order = None

    st.title("Add Order")

    st.markdown("---")

    # show order creation form
    env = st.secrets['ENV']['ENV']
    manager = Manager(env)
    col1, col2 = st.columns([2, 7])
    with col1: 
        if dup_order and dup_order.get('image_path'):
            st.image(manager.get_image_by_path(dup_order['image_path'], cache=False), width=250)
        image = st.file_uploader("New Image", type=["jpg", "png"])
        if image:
            st.image(image, width=250)
    with col2:
        with st.form(key='create_order_form', border=False):
            name = st.text_input("Name", value=get_value(dup_order, 'name'))
            cols = st.columns(2)
            with cols[0]:
                seller = st.text_input("Seller", value=get_value(dup_order, 'seller'))
            with cols[1]:
                preset_seller = st.selectbox(
                    "Preset Seller", 
                    preset_seller_options,
                    index=preset_seller_options.index(get_value(dup_order, 'seller')) if get_value(dup_order, 'seller') in preset_seller_options else 0
                )
            if dup_order:
                status = st.selectbox("Status", [status.value for status in OrderStatus], index=[status.value for status in OrderStatus].index(get_value(dup_order, 'status')))
            else:
                status = st.selectbox("Status", [status.value for status in OrderStatus], index=0)
            tracking_number = st.text_input("Tracking Number", value=get_value(dup_order, 'tracking_number'))
            amount = st.number_input("Amount", min_value=1, step=1, value=get_value(dup_order, 'amount', 1))
            plushie_type_options = [type.value for type in PlushieType] 
            plushie_type = st.selectbox("Plushie Type", plushie_type_options, index=plushie_type_options.index(get_value(dup_order, 'plushie_type', plushie_type_options[0])))
            price = st.number_input("Price", min_value=0.0, step=0.01, format="%.2f", value=float(get_value(dup_order, 'price', 0)))
            shipping_cost = st.number_input("Shipping Cost", min_value=0.0, step=0.01, format="%.2f", value=float(get_value(dup_order, 'shipping_cost', 0)))
            shipping_date = st.date_input("Shipping Date", value=get_value(dup_order, 'shipping_date', None))
            expected_deliver_date = st.date_input("Expected Delivery Date", value=get_value(dup_order, 'expected_deliver_date', None))
            notes = st.text_area("Notes", value=get_value(dup_order, 'notes', ''))

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