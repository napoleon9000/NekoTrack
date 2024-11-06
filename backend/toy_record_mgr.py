from typing import Optional
from dataclasses import dataclass
from tinydb import Query
from models.machines import Record, Machine
from backend.base_manager import Manager as BaseManager
from utils import get_image_by_path
from io import BytesIO
import streamlit as st
import uuid
from dataclasses import field
from datetime import datetime
import pandas as pd
import logging
from dataclasses import asdict
from models.machines import IncomeRecord
logger = logging.getLogger(__name__)


class Manager(BaseManager):
    def __init__(self, env):
        super().__init__(env)

    def create_income_record(self, date: str, POS_machine: int, auto_machine: int):
        record = IncomeRecord(date=date, POS_machine=POS_machine, auto_machine=auto_machine, total=0)
        self.firestore_db.create_income_record(asdict(record))
    
    def get_all_income_records(self):
        records = self.firestore_db.get_all_income_records()
        df = pd.DataFrame(records)
        if df.empty:
            return None
        df['date'] = pd.to_datetime(df['date']).dt.strftime("%Y-%m-%d")
        df = df.sort_values(by='date', ascending=True)
        auto_machine_records = df['auto_machine'].tolist()
        diff_records = [auto_machine_records[0]]
        for i in range(1, len(auto_machine_records)):
            if auto_machine_records[i] < auto_machine_records[i-1]:
                diff_records.append(auto_machine_records[i])
            else:
                diff_records.append(auto_machine_records[i] - auto_machine_records[i-1])
        df['auto_machine'] = pd.Series(diff_records)
        df['total'] = df['POS_machine'] + df['auto_machine']
        selected_columns = ['date', 'POS_machine', 'auto_machine', 'total']
        return df[selected_columns]


    def create_machine(self, machine: Machine, image: BytesIO):
        if image is not None:
            # upload image to blob storage
            image_path = f"images/machines/{machine.id}.jpg"
            self.blob_db.upload_file(image, image_path, compress=True)
            machine.image = image_path
        
        self.firestore_db.create_machine(asdict(machine))

    def get_all_machines(self):
        all_machines = self.firestore_db.get_all_machines()
        # sort by id, only keep the numbers in the id
        numbers = '1234567890'
        all_machines = sorted(all_machines, key=lambda x: int(''.join(filter(lambda c: c in numbers, x['id']))))
        return all_machines

    def get_all_machines_obj(self):
        machines = self.get_all_machines()
        return [Machine(**machine) for machine in machines]

    def get_image_by_machine_id(self, machine_id):
        machine = self.get_machine_by_id(machine_id)
        path = machine['image']
        if path is None:
            return None
        image = get_image_by_path(path, self.blob_db)
        return image

    def get_machine_by_id(self, machine_id):
        return self.firestore_db.get_machine_by_id(machine_id)

    def get_machine_obj_by_id(self, machine_id):
        machine = self.get_machine_by_id(machine_id)
        return Machine(**machine) if machine else None

    def update_machine(self, machine_id, machine):
        self.firestore_db.update_machine(machine_id, machine)

    def delete_machine(self, machine_id):
        machine = self.get_machine_by_id(machine_id)
        self.firestore_db.delete_machine(machine_id)
        if machine['image'] is not None:
            self.blob_db.delete_file(machine['image'])

    def create_record(self, record: Record):
        self.firestore_db.create_record(asdict(record))

        # update machine parameters
        machine_id = record.machine_id
        machine = self.get_machine_by_id(machine_id)
        machine['param_strong_strength'] = record.param_strong_strength
        machine['param_medium_strength'] = record.param_medium_strength
        machine['param_weak_strength'] = record.param_weak_strength
        machine['param_award_interval'] = record.param_award_interval
        machine['param_mode'] = record.param_mode
        self.update_machine(machine_id, machine)

    def get_all_records(self):
        return self.firestore_db.get_all_records()

    def get_all_records_df(self):
        records = self.get_all_records()
        return pd.DataFrame(records)

    def get_records_by_machine_id(self, machine_id):
        keys = ['date', 'coins_in', 'toys_payout', 'param_strong_strength', 
                'param_medium_strength', 'param_weak_strength', 
                'param_award_interval', 'param_mode', 'notes']
        records = self.firestore_db.get_records_by_machine_id(machine_id)
        df = pd.DataFrame(records)
        # sort by date
        df = df.sort_values(by='date', ascending=False)
        return df[keys]

    def save_record(self, record: Record):
        self.firestore_db.save_record(asdict(record))

    def get_all_machines_payout_rate(self):
        machines = self.get_all_machines_obj()
        all_results = []
        for machine in machines:
            machine_id = machine.id
            analyze_result, all_time_payout_rate, last_3_days_payout_rate = self.calculate_machine_payout_rate(machine_id)
            all_results.append({
                'machine_id': machine_id,
                'last_day_payout_rate': analyze_result['daily_payout_rate'].iloc[-1],
                'all_time_payout_rate': all_time_payout_rate,
                'last_3_days_payout_rate': last_3_days_payout_rate
            })
        return all_results

    def calculate_machine_payout_rate(self, machine_id):
        records = self.get_records_by_machine_id(machine_id)
        processed_records = []
        # daily payout rate
        records['date'] = pd.to_datetime(records['date'])
        records_sorted = records.sort_values(by='date', ascending=True)
        for i in range(1, records.shape[0]):
            yesterday_coins_in = records_sorted.iloc[i-1]['coins_in']
            yesterday_toys_payout = records_sorted.iloc[i-1]['toys_payout']
            today_coins_in = records_sorted.iloc[i]['coins_in']
            today_toys_payout = records_sorted.iloc[i]['toys_payout']
            
            if today_coins_in < yesterday_coins_in:
                yesterday_coins_in = 0
            if today_toys_payout < yesterday_toys_payout:
                yesterday_toys_payout = 0

            coins_diff = today_coins_in - yesterday_coins_in
            toys_diff = today_toys_payout - yesterday_toys_payout
            if coins_diff == 0 or toys_diff == 0:
                daily_payout_rate = 0
            else:
                daily_payout_rate = coins_diff / toys_diff

            processed_records.append({
                'date': records_sorted.iloc[i]['date'],
                'daily_coins_in': coins_diff,
                'daily_toys_payout': toys_diff,
                'daily_payout_rate': daily_payout_rate,
            })

        processed_records = pd.DataFrame(processed_records)
        # all time payout rate
        total_coins_in = processed_records['daily_coins_in'].sum()
        total_toys_payout = processed_records['daily_toys_payout'].sum()
        if total_coins_in == 0 or total_toys_payout == 0:
            all_time_payout_rate = 0.0
        else:
            all_time_payout_rate = total_coins_in / total_toys_payout 

        # last 3-day payout rate
        last_3_days_records = processed_records.tail(3)
        last_3_days_coins_in = last_3_days_records['daily_coins_in'].sum()
        last_3_days_toys_payout = last_3_days_records['daily_toys_payout'].sum()
        if last_3_days_coins_in == 0 or last_3_days_toys_payout == 0:
            last_3_days_payout_rate = 0.0
        else:
            last_3_days_payout_rate = last_3_days_coins_in / last_3_days_toys_payout

        result = {
            'daily_payout_rate': processed_records['daily_payout_rate'].tolist(),
            'daily_coins_in': processed_records['daily_coins_in'].tolist(),
            'daily_toys_payout': processed_records['daily_toys_payout'].tolist(),
            'date': processed_records['date'].tolist()
        }

        return pd.DataFrame(result), all_time_payout_rate, last_3_days_payout_rate


    def plot_analyze_result(self, analyze_result):
        # Combine daily_coins_in and daily_toys_payout into a single DataFrame
        combined_df = pd.DataFrame({
            'daily_coins_in': analyze_result['daily_coins_in'],
            'daily_toys_payout': analyze_result['daily_toys_payout'],
            'date': analyze_result['date']
        })
        
        # Plot daily_coins_in and daily_toys_payout on the same plot
        import matplotlib.pyplot as plt

        col1, col2 = st.columns(2)
        combined_df['date'] = pd.to_datetime(combined_df['date'])
        combined_df['day_of_week'] = combined_df['date'].dt.strftime('%a')
        combined_df['date_with_day'] = combined_df['date'].dt.strftime('%m-%d') + '_' + combined_df['day_of_week']
        
        with col1:
            fig, ax = plt.subplots()
            combined_df.plot(x='date_with_day', y=['daily_coins_in', 'daily_toys_payout'], ax=ax, style='-o')
            ax.set_title('Coins In & Toys Payout')
            ax.grid(True)
            st.pyplot(fig)
            st.write('coins in & toys payout')
            # close the plot
            plt.close(fig)
        
        analyze_result_df = pd.DataFrame(analyze_result)
        analyze_result_df['date'] = pd.to_datetime(analyze_result_df['date'])
        analyze_result_df['day_of_week'] = analyze_result_df['date'].dt.strftime('%a')
        analyze_result_df['date_with_day'] = analyze_result_df['date'].dt.strftime('%m-%d') + '_' + analyze_result_df['day_of_week']
        
        with col2:
            fig, ax = plt.subplots()
            analyze_result_df.plot(x='date_with_day', y='daily_payout_rate', ax=ax, style='-o')
            ax.set_title('Payout Rate')
            ax.set_ylim(0, 15)
            ax.grid(True)
            st.pyplot(fig)
            st.write('payout rate')
            plt.close(fig)

    def plot_overall_analyze_result(self, all_results):
        n_days_to_plot = 30
        if len(all_results[0]['date']) > n_days_to_plot:
            all_dates = all_results[0]['date'][-n_days_to_plot:]
        else:
            all_dates = all_results[0]['date']

        data_by_date = {k: {
            'daily_payout_rate': [],    
            'daily_coins_in': [],
            'daily_toys_payout': []
        } for k in all_dates}

        for result in all_results:
            for date in all_dates:
                if date in result['date'].values:
                    daily_payout_rate = result['daily_payout_rate'].loc[result['date'] == date].values[0]
                    daily_coins_in = result['daily_coins_in'].loc[result['date'] == date].values[0]
                    daily_toys_payout = result['daily_toys_payout'].loc[result['date'] == date].values[0]
                    
                    data_by_date[date]['daily_payout_rate'].append(daily_payout_rate)
                    data_by_date[date]['daily_coins_in'].append(daily_coins_in)
                    data_by_date[date]['daily_toys_payout'].append(daily_toys_payout)
            
        # sum each date
        for date in all_dates:
            data_by_date[date]['daily_coins_in'] = sum(data_by_date[date]['daily_coins_in'])
            data_by_date[date]['daily_toys_payout'] = sum(data_by_date[date]['daily_toys_payout'])
            data_by_date[date]['daily_payout_rate'] = data_by_date[date]['daily_coins_in'] / data_by_date[date]['daily_toys_payout']

        # for plot
        df_all = pd.DataFrame(data_by_date).T.reset_index()
        df1 = pd.DataFrame({
            'daily_coins_in': df_all['daily_coins_in'],
            'daily_toys_payout': df_all['daily_toys_payout'],
            'date': all_dates.values
        })
        df2 = pd.DataFrame({
            'daily_payout_rate': df_all['daily_payout_rate'],
            'date': all_dates.values
        })

        return df1, df2
