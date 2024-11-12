import streamlit as st
from backend.order_mgr import OrderManager as Manager
from models.orders import Order, OrderStatus, PlushieType
from io import BytesIO
from datetime import datetime

def app():
    st.title("Edit Order")
    
    if 'selected_order_for_edit' not in st.session_state:
        st.error("No order selected for editing")
        return
        
    order = st.session_state['selected_order_for_edit']
    env = st.secrets['ENV']['ENV']
    manager = Manager(env)
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 7])
    with col1:
        if order.get('image_path'):
            st.image(manager.get_image_by_path(order['image_path'], cache=False), width=250)
        new_image = st.file_uploader("Update Image", type=["jpg", "png"])
        if new_image:
            st.image(new_image, width=250)
            
    with col2:
        with st.form(key='edit_order_form', border=False):
            name = st.text_input("Name", value=order.get('name', ''))
            
            cols = st.columns(2)
            with cols[0]:
                seller = st.text_input("Seller", value=order.get('seller', ''))
            with cols[1]:
                preset_seller = st.selectbox(
                    "Preset Seller", 
                    [None, "Temu", "New York"],
                    index=[None, "Temu", "New York"].index(order.get('seller')) if order.get('seller') in ["Temu", "New York"] else 0
                )
                
            status = st.selectbox(
                "Status", 
                [status.value for status in OrderStatus],
                index=[s.value for s in OrderStatus].index(order.get('status'))
            )
            
            tracking_number = st.text_input("Tracking Number", value=order.get('tracking_number', ''))
            amount = st.number_input("Amount", min_value=1, step=1, value=order.get('amount', 1))
            
            plushie_type = st.selectbox(
                "Plushie Type", 
                [type.value for type in PlushieType],
                index=[t.value for t in PlushieType].index(order.get('plushie_type'))
            )
            
            price = st.number_input("Price", min_value=0.0, step=0.01, format="%.2f", value=float(order.get('price', 0)))
            shipping_cost = st.number_input("Shipping Cost", min_value=0.0, step=0.01, format="%.2f", value=float(order.get('shipping_cost', 0)))
            
            # Convert string dates back to datetime if needed
            shipping_date = order.get('shipping_date')
            if isinstance(shipping_date, str):
                shipping_date = datetime.strptime(shipping_date, '%Y-%m-%d').date()
            shipping_date = st.date_input("Shipping Date", value=shipping_date)
            
            expected_deliver_date = order.get('expected_deliver_date')
            if isinstance(expected_deliver_date, str):
                expected_deliver_date = datetime.strptime(expected_deliver_date, '%Y-%m-%d').date()
            expected_deliver_date = st.date_input("Expected Delivery Date", value=expected_deliver_date)
            
            notes = st.text_area("Notes", value=order.get('notes', ''))
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.form_submit_button("Save Changes"):
                    updates = {
                        'name': name,
                        'seller': preset_seller if not seller else seller,
                        'status': status,
                        'tracking_number': tracking_number,
                        'amount': amount,
                        'plushie_type': plushie_type,
                        'price': price,
                        'shipping_cost': shipping_cost,
                        'shipping_date': datetime.combine(shipping_date, datetime.min.time()),  # Convert date to datetime
                        'expected_deliver_date': datetime.combine(expected_deliver_date, datetime.min.time()),  # Convert date to datetime
                        'notes': notes
                    }

                    # remove None values from updates
                    updates = {k: v for k, v in updates.items() if v is not None}
                    
                    if new_image:
                        img_bytesio = BytesIO(new_image.getvalue())
                        # Delete old image if exists
                        if order.get('image_path'):
                            manager.blob_db.delete_file(order['image_path'])
                        # Upload new image
                        image_path = f"images/orders/{order['id']}.jpg"
                        manager.blob_db.upload_file(img_bytesio, image_path, compress=True)
                        updates['image_path'] = image_path
                    
                    manager.update_order(order['id'], updates)
                    st.success("Order updated successfully")
                    # Clear the selected order and return to order status page
                    del st.session_state['selected_order_for_edit']
                    st.session_state['page'] = 'order_status'
                    st.rerun()
                    
            with col2:
                if st.form_submit_button("Delete Order"):
                    manager.delete_order(order['id'])
                    st.success("Order deleted successfully")
                    del st.session_state['selected_order_for_edit']
                    st.session_state['page'] = 'order_status'
                    st.rerun()
                    
            with col3:
                if st.form_submit_button("Cancel"):
                    del st.session_state['selected_order_for_edit']
                    st.session_state['page'] = 'order_status'
                    st.rerun()
