import streamlit as st
import pandas as pd
import os


st.set_page_config(layout="wide", page_title='Sound Pressure Level Dashboard')
st.title('Sound Pressure Level Dashboard')

if spl_path := st.text_input('SPL Folder Path', '/Users/lars/Desktop/SPL'):
    st.session_state['spl_path'] = spl_path
    try:
        file_options = {}
        for root, dirs, files in os.walk(spl_path):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    friendly_name = os.path.relpath(file_path, spl_path)
                    friendly_name = friendly_name[:-4] if friendly_name.endswith('.txt') else friendly_name
                    friendly_name = friendly_name.replace('/', ' | ')
                    file_options[friendly_name] = file_path
        file_options = dict(sorted(file_options.items(), key=lambda x: x[0][:4], reverse=True))
        selected_file_name = st.selectbox('Select a file', list(file_options.keys()))

        if selected_file_name:
            selected_file_path = file_options[selected_file_name]
            with open(selected_file_path, 'r') as f:
                next(f) # Skip the first row if it's a header
                df = pd.read_csv(f, sep=',', names=['date', 'time', 'dB', 'units'])
                df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
                df['time_only'] = df['datetime'].dt.time

                min_time = df['time_only'].min()
                max_time = df['time_only'].max()

                start_time, end_time = st.slider(
                    "Select a time range",
                    min_value=min_time,
                    max_value=max_time,
                    value=(min_time, max_time),
                    step=pd.Timedelta(minutes=1),
                    format="HH:mm",
                    key=selected_file_name
                )

                filtered_df = df[df['time_only'].between(start_time, end_time)]

                col1, col2 = st.columns(2, gap='small')
                with col1:
                    st.write(filtered_df[['date', 'time', 'dB']])
                with col2:
                    st.write(filtered_df['dB'].describe().to_frame().rename(
                        columns={'dB': 'Statistics'}
                        ,index={'count':'points'
                                ,'mean': 'average'
                                ,'std': 'standard dev'}))
                    
                show_raw_data = st.checkbox('Raw Data', False)
                show_minute_rolling = st.checkbox('Minute Moving Average', True)
                show_ten_minute_rolling = st.checkbox('10 Minute Moving Average', True)

                chart_data = pd.DataFrame()

                if show_raw_data:
                    chart_data['Raw Data'] = filtered_df['dB']
                if show_minute_rolling:
                    chart_data['1 Minute Rolling Average'] = filtered_df['dB'].rolling(60).mean()
                if show_ten_minute_rolling:
                    chart_data['10 Minute Rolling Average'] = filtered_df['dB'].rolling(60*10).mean()
                if not chart_data.empty:
                    st.line_chart(chart_data, use_container_width=True)

    except Exception as e:
        st.write('Error reading files: ', e)
else:
    st.write("Please enter a valid SPL Folder Path.")
