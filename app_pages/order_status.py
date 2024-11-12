import streamlit as st
from backend.order_mgr import OrderManager
from models.orders import PlushieType
import pandas as pd

env = st.secrets['ENV']['ENV']
manager = OrderManager(env)

def edit_order(order):
    st.session_state['selected_order_for_edit'] = order
    st.session_state['page'] = 'edit_order'

def duplicate_order(order):
    st.session_state['selected_order_for_duplicate'] = order
    st.session_state['page'] = 'add_order'

def delete_order(order):
    manager.delete_order(order['id'])

def render_order_card(order):
    default_image_map = {
        PlushieType.small.value: 'images/small_plushie.png',
        PlushieType.medium.value: 'images/medium_plushie.png',
        PlushieType.large.value: 'images/large_plushie.png',
        PlushieType.keychain.value: 'images/keychain.png',
    }
    with st.container(border=True):
        col1, col2 = st.columns([1, 3]) 
        with col1:
            if order.get('image_path'):
                st.image(manager.get_image_by_path(order['image_path']), width=100)
            else:
                order_type = order['plushie_type']
                st.image(default_image_map[order_type], width=100)
            st.markdown(f"## {order.get('amount', 'N/A')}")
                
        with col2:
            name = order.get('name', None)
            id = order.get('id', None)
            st.markdown(f"### {name if name else f'Order #{id[:8]}'}")
            expected_deliver_date = order.get('expected_deliver_date', None)
            expected_deliver_date_str = expected_deliver_date.strftime('%Y-%m-%d') if expected_deliver_date else 'N/A'
            shipping_date = order.get('shipping_date', None)
            shipping_date_str = shipping_date.strftime('%Y-%m-%d') if shipping_date else 'N/A'

            st.markdown(f"""
                **Seller:** {order.get('seller', 'N/A')} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Price:** ${order.get('price', 0):.2f}  
                **Status:** {order.get('status', 'N/A')} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Shipping Date:** {shipping_date_str}
                **Expected Delivery:** {expected_deliver_date_str}
            """)
            if order.get('notes'):
                st.markdown(order['notes'])
            
        # Create buttons with horizontal layout
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1]) 
        # Place buttons directly (they will be inline due to CSS)
        with col2:
            st.button(key=f"edit_{id}", label="Edit", on_click=edit_order, args=[order])
        with col3:
            st.button(key=f"duplicate_{id}", label="Duplicate", on_click=duplicate_order, args=[order])
        with col4:
            st.button(key=f"delete_{id}", label="Delete", on_click=delete_order, args=[order])


def get_date_amount_df(orders):
    """
    Get a dataframe showing the date and the amount of orders for each date
    """
    df = pd.DataFrame(orders)
    df['expected_deliver_date'] = pd.to_datetime(df['expected_deliver_date']).dt.strftime('%Y-%m-%d')
    df['amount'] = pd.to_numeric(df['amount'])
    df = df.groupby('expected_deliver_date')['amount'].sum().reset_index()
    return df


def app():
    st.title("Order Status") 
    all_orders = manager.get_all_orders()
    # select types to display
    selected_types = st.multiselect("Select Plushie Types", PlushieType.__members__.values(), default=[PlushieType.small, PlushieType.large])
    if len(selected_types) == 0:
        st.warning("Please select at least one plushie type")
        return

    cols = st.columns(len(selected_types))

    for i, selected_type in enumerate(selected_types):
        with cols[i]:
            st.markdown(f"### {selected_type.value}")
            selected_orders = [order for order in all_orders if order['plushie_type'] == selected_type.value]
            if len(selected_orders) == 0:
                st.warning("No orders found")
            else:
                st.write(get_date_amount_df(selected_orders))
                for order in selected_orders:
                    render_order_card(order)


