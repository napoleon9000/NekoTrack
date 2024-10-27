import streamlit as st
import pandas as pd
from dataclasses import dataclass
import logging

from backend.toy_record_mgr import Manager, Machine
from io import BytesIO

logger = logging.getLogger(__name__)

def delete_machine(machine_id, manager: Manager):
    manager.delete_machine(machine_id)
    st.success("Machine deleted successfully")

def app():
    st.title("Edit Machine")
    st.markdown("---")

    # show all machines and images
    env = st.secrets['ENV']['ENV']
    manager = Manager(env)
    machine_id = st.session_state['selected_machine_id_for_edit']
    if machine_id is None:
        st.error("Machine not selected")
        return
    machine = manager.get_machine_obj_by_id(machine_id)
    machine_image = manager.get_image_by_machine_id(machine_id)
    col1, col2 = st.columns([2, 7])
    with col1:
        if machine_image is not None:
            st.image(machine_image, width=250)
        else:
            st.image('claw_machine.webp', width=250)
    with col2:
        # edit machine 
        with st.form(key='edit_machine_form', border=False):
            
            name = st.text_input("Name", value=machine.name) 
            location = st.text_input("Location", value=machine.location)
            status = st.text_input("Status", value=machine.status)
            notes = st.text_input("Notes", value=machine.notes)
            strong_strength = st.number_input("Strong Strength", min_value=0.0, max_value=50.0, step=0.2, format="%.1f", value=machine.param_strong_strength)
            medium_strength = st.number_input("Medium Strength", min_value=0.0, max_value=50.0, step=0.2, format="%.1f", value=machine.param_medium_strength)
            weak_strength = st.number_input("Weak Strength", min_value=0.0, max_value=50.0, step=0.2, format="%.1f", value=machine.param_weak_strength)
            award_interval = st.number_input("Award Interval", min_value=1, step=1, value=machine.param_award_interval)
            options = ["1", "2", "3"]
            mode = st.selectbox("Mode", options, index=options.index(machine.param_mode))
            image = st.file_uploader("Image", type=["jpg", "png"])

            if st.form_submit_button("Save"):
                new_machine = Machine(name=name, location=location, status=status, notes=notes,
                                    param_strong_strength=strong_strength, param_medium_strength=medium_strength,
                                    param_weak_strength=weak_strength, param_award_interval=award_interval,
                                    param_mode=mode, id=machine_id)
                if image is not None:   
                    img_bytesio = BytesIO(image.getvalue())
                    manager.create_machine(new_machine, img_bytesio)
                else:
                    new_machine.image = machine.image
                    manager.create_machine(new_machine, None)
                st.success("Machine updated successfully")

    
if __name__ == "__main__":
    app()