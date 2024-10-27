import streamlit as st
import pandas as pd
from dataclasses import dataclass
import logging

from backend.toy_record_mgr import Manager, Machine
from io import BytesIO

logger = logging.getLogger(__name__)

if 'selected_machine_id_for_edit' not in st.session_state:
    st.session_state['selected_machine_id_for_edit'] = None

def delete_machine(machine_id, manager: Manager):
    manager.delete_machine(machine_id)
    st.success("Machine deleted successfully")

def edit_machine(machine_id, manager: Manager):
    st.session_state['selected_machine_id_for_edit'] = machine_id
    st.session_state['page'] = 'edit_machine'
    

def app():
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        st.title("Machines")
    with col2:
        st.button("Refresh")
    st.markdown("---")

    # show all machines and images
    env = st.secrets['ENV']['ENV']
    manager = Manager(env)
    machines = manager.get_all_machines()
    num_columns = 4
    columns = st.columns(num_columns)

    for idx, machine in enumerate(machines):
        name = machine['name']
        location = machine['location']
        status = machine['status']
        notes = machine['notes']
        image = manager.get_image_by_machine_id(machine['id'])
        if 'doc_id' in machine:
            del machine['doc_id']
        machine_obj = Machine(**machine)

        # Determine which column to use
        col = columns[idx % num_columns]

        with col:
            if image is not None:
                st.image(image, width=200)
            else:
                st.image('claw_machine.webp', width=200)

            if name is not None and name != "":
                st.markdown(f"**Name:** {name}")
            else:
                st.markdown(f"**id:** {machine['id']}")
            if location is not None and location != "":
                st.markdown(f"**Location:** {location}")
            if machine_obj.get_params() is not None:
                st.markdown(f"**Params:** {machine_obj.get_params()}")
            if status is not None and status != "":
                st.markdown(f"**Status:** {status}")
            if notes is not None and notes != "":
                st.markdown(f"**Notes:** {notes}")
            col1, col2, _ = st.columns([1, 1, 2])
            with col1:
                st.button("Delete", key=f"delete_{machine['id']}", on_click=delete_machine, args=(machine['id'], manager))
            with col2:
                if st.button("Edit", key=f"edit_{machine['id']}", on_click=edit_machine, args=(machine['id'], manager)):
                    st.rerun()


    # create machine (in an expander)
    with st.expander("Add New Machine"):
        with st.form(key='add_machine_form', border=False):
            name = st.text_input("Name")
            location = st.text_input("Location")
            status = st.text_input("Status")
            notes = st.text_input("Notes")
            strong_strength = st.number_input("Strong Strength", min_value=0.0, max_value=50.0, step=0.2, format="%.1f")
            medium_strength = st.number_input("Medium Strength", min_value=0.0, max_value=50.0, step=0.2, format="%.1f")
            weak_strength = st.number_input("Weak Strength", min_value=0.0, max_value=50.0, step=0.2, format="%.1f")
            award_interval = st.number_input("Award Interval", min_value=1, step=1)
            mode = st.selectbox("Mode", ["1", "2", "3"])
            image = st.file_uploader("Image", type=["jpg", "png"])

            if st.form_submit_button("Save"):
                new_machine = Machine(name=name, location=location, status=status, notes=notes,
                                    param_strong_strength=strong_strength, param_medium_strength=medium_strength,
                                    param_weak_strength=weak_strength, param_award_interval=award_interval,
                                    param_mode=mode)
                if image is not None:   
                    img_bytesio = BytesIO(image.getvalue())
                    manager.create_machine(new_machine, img_bytesio)
                else:
                    manager.create_machine(new_machine, None)
                st.success("Machine created successfully")

    
if __name__ == "__main__":
    app()