import streamlit as st
import pandas as pd
from simple_salesforce import Salesforce
import requests
import io
from io import StringIO
from datetime import datetime
import math
import folium
from streamlit_folium import st_folium
from folium.features import DivIcon


APP_TITLE = "SFDC Maps"
SR_list = ['Mokhtaria Touhami',
        'Antoine Lejard',
        'Thibaut Sternitzky',
        'Florence QUERE',
        'Carole CHAPUIS',
        'Rosemarie Menard',
        'ABDARAZAK NHARI',
        'Annie GARNIER',
        'Audrey Poirier',
        'Christelle Fortier',
        'Caroline Mollet',
        'Christophe Pendon',
        'STEPHANIE LEPERE',
        'CHRISTELLE VAUCHELET',
        'Emmanuelle BARD',
        'Marc Emsalem',
        'BLANDINE DINGREVILLE',
        'Marie MORIN',
        'Olivier BERGERON',
        'Florian Darcel',
        'Stephanie GUILLERME',
        'CATHERINE PERROT',
        'Sophie LE PEUTREC',
        'Agnès Devignac',
        'Laure BOIDOT',
        'Daliny MEY-SIGAUD',
        'Sylvie Blanchet',
        'Frederic LELEYTER',
        'Carine BOUSSANT',
        'Marine HERVE',
        'Edwige Dato',
        'Natacha GRANGE',
        'Anaïs ESTRADA',
        'Arnaud PRYS',
        'Fabienne CAMPOS',
        'Yanis Bordelanne',
        'Stephane Combret',
        'CHARBONNIER MAGALI',
        'LINDA MEGHARBI',
        ]

@st.cache_data
def display_map(df):
    zoom_var = 6
    
    #lat_center = (df['Lat'].max() + df['Lat'].min())/2
    #lon_center = (df['Lon'].max() + df['Lon'].min())/2

    m = folium.Map(location=[46.65551064717039, 2.437741286674764], tiles='OpenStreetMap', zoom_start = zoom_var)

    for i, row in df.iterrows():
        lat = df.at[i, 'Lat']
        lon = df.at[i, 'Lon']
        segment = df.at[i, 'Segment']
        name = df.at[i, 'Name']
        brick = df.at[i, 'Brick Code']
        city = df.at[i, 'Primary City']
        street = df.at[i, 'Primary Street']
        date = df.at[i, 'Last Visit Date']
        id = df.at[i, 'ID']
        visited = df.at[i, 'Visited']
        rate = df.at[i, 'Visit_rate']
        size = df.at[i, 'Target Call Frequency']
        new = df.at[i, 'NEW']
        channel = df.at[i, 'Account Category']

        if segment == 'Gold':
            color = 'gold'
        elif segment == 'Silver':
            color = 'silver'
        elif segment == 'Bronze':
            color = 'orange'
        elif segment == 'Platinum':
            color = 'cadetblue'
        else:
            color = 'beige'
        
        if visited == 'Y':
            visited_color = 'darkgreen'
        else:
            visited_color = 'darkred'

        html = '''
                <b style="color:gray;font-family:verdana;font-size:80%;">{}</b><br>
                <b style="color:gray;font-family:verdana;font-size:80%;">{}</b><br>
                <em style="color:gray;font-family:verdana;font-size:80%;">Coverage: </em><b style="color:gray;font-family:verdana;font-size:80%;">{}</b><br>
                <em style="color:gray;font-family:verdana;font-size:80%;">Last visited date: </em><b style="color:gray;font-family:verdana;font-size:80%;">{}</b><br>
                <em style="color:gray;font-family:verdana;font-size:80%;">Channel: </em><b style="color:gray;font-family:verdana;font-size:80%;">{}</b><br>
                <b style="color:gray;font-family:verdana;font-size:80%;">{}</b><br>
                <b style="color:gray;font-family:verdana;font-size:80%;">{}</b><br>
                <b style="color:gray;font-family:verdana;font-size:80%;">{}</b><br>
                <em style="color:gray;font-family:verdana;font-size:80%;">ID: </em><b style="color:gray;font-family:verdana;font-size:80%;">{}</b><br>
                '''.format(name, segment, rate, date, channel, brick, city, street, id)

        iframe = folium.IFrame(html,
                            width=300,
                            height=180)

        popup = folium.Popup(iframe,
                            max_width=300)

        
        if new == "NEW":
            folium.Marker([lat,lon], icon=folium.Icon(icon='dove', prefix='fa'), popup=popup).add_to(m)
            folium.CircleMarker(location=[lat,lon],
                            color=visited_color,
                            fill=True,
                            fill_color=color,
                            fill_opacity=1,
                            radius=size*2).add_to(m)
        else:
            folium.CircleMarker(location=[lat,lon],
                            popup=popup,
                            color=visited_color,
                            fill=True,
                            fill_color=color,
                            fill_opacity=1,
                            radius=size*2).add_to(m)
    
    return m

@st.cache_data(show_spinner="Downloading accounts and contacts from SFDC...")
def get_data(Rep_name):
    sf = Salesforce(
        username='nmatyash@lifescan.com', 
        password='KLbq57fa31!',
        security_token='')

    sf_org = 'https://jjds-sunrise.my.salesforce.com/'
    report_id_accounts = '00OQv00000As39dMAB'
    report_id_contacts = '00OQv00000AtiDxMAJ'
    report_id_visits = '00OQv00000As58DMAR'
    report_id_prev_visits = '00OQv00000AryJfMAJ'
    report_id_visits_contact = '00OQv00000AuI69MAF'
    report_id_prev_visits_contact = '00OQv00000AuHurMAF'
    export_params = '?isdtp=p1&export=1&enc=UTF-8&xf=csv'

    sf_report_url_accounts = sf_org + report_id_accounts + export_params
    response_accounts = requests.get(sf_report_url_accounts, headers=sf.headers, cookies={'sid': sf.session_id})
    report_accounts = response_accounts.content.decode('utf-8')
    All_Accounts = pd.read_csv(StringIO(report_accounts))
    All_Accounts = All_Accounts[All_Accounts['Account ID'].map(lambda x: str(x)[0]) == '0']

    sf_report_url_contacts = sf_org + report_id_contacts + export_params
    response_contacts = requests.get(sf_report_url_contacts, headers=sf.headers, cookies={'sid': sf.session_id})
    report_contacts = response_contacts.content.decode('utf-8')
    All_Contacts = pd.read_csv(StringIO(report_contacts))
    All_Contacts = All_Contacts[All_Contacts['Contact ID'].map(lambda x: str(x)[0]) == '0']
    All_Contacts['Name'] = All_Contacts['First Name'] + " " + All_Contacts['Last Name']
    All_Contacts['Lat'] = All_Contacts['Lat'].fillna(0)
    All_Contacts['Lon'] = All_Contacts['Lon'].fillna(0)
    All_Contacts['Len fName'] = All_Contacts['First Name'].map(lambda x: len(str(x)))
    All_Contacts['Len lName'] = All_Contacts['Last Name'].map(lambda x: len(str(x)))
    All_Contacts['Lat'] = All_Contacts['Lat'] + All_Contacts['Len fName'].map(lambda x: int(math.log10(x)*10)*0.0001)
    All_Contacts['Lon'] = All_Contacts['Lon'] + All_Contacts['Len lName'].map(lambda x: int(math.log10(x)*10)*0.0001)
    All_Contacts = All_Contacts[['Contact ID', 'Contact Owner', 'Name',
        'Contact  Type', 'ABCD Grid BGM (Contact) - current', 'Status',
        'Call Status (Contact)', 'Brick Code', 'Primary State/Province',
        'Primary City', 'Primary Street', 'Account Category',
        'Target Call Frequency / Cycle (Contact)', 'Lat', 'Lon', 'Last Visit',
        'Last Call Date (Contact)', 'Last Activity']]

    sf_report_url_visits = sf_org + report_id_visits + export_params
    response_visits = requests.get(sf_report_url_visits, headers=sf.headers, cookies={'sid': sf.session_id})
    report_visits = response_visits.content.decode('utf-8')
    visits = pd.read_csv(StringIO(report_visits))
    visits = visits[visits['Account ID'].map(lambda x: str(x)[0]) == '0']

    sf_report_url_prev_visits = sf_org + report_id_prev_visits + export_params
    response_prev_visits = requests.get(sf_report_url_prev_visits, headers=sf.headers, cookies={'sid': sf.session_id})
    report_prev_visits = response_prev_visits.content.decode('utf-8')
    prev_visits = pd.read_csv(StringIO(report_prev_visits))
    prev_visits = prev_visits[prev_visits['Account ID'].map(lambda x: str(x)[0]) == '0']

    sf_report_url_visits_contact = sf_org + report_id_visits_contact + export_params
    response_visits_contact = requests.get(sf_report_url_visits_contact, headers=sf.headers, cookies={'sid': sf.session_id})
    report_visits_contact = response_visits_contact.content.decode('utf-8')
    visits_contact = pd.read_csv(StringIO(report_visits_contact))
    visits_contact = visits_contact[visits_contact['Contact ID'].map(lambda x: str(x)[0]) == '0']

    sf_report_url_prev_visits_contact = sf_org + report_id_prev_visits_contact + export_params
    response_prev_visits_contact = requests.get(sf_report_url_prev_visits_contact, headers=sf.headers, cookies={'sid': sf.session_id})
    report_prev_visits_contact = response_prev_visits_contact.content.decode('utf-8')
    prev_visits_contact = pd.read_csv(StringIO(report_prev_visits_contact))
    prev_visits_contact = prev_visits_contact[prev_visits_contact['Contact ID'].map(lambda x: str(x)[0]) == '0']    

    All_Accounts = All_Accounts.rename(columns = {
        'Account ID': 'ID',
        'Account Owner': 'Owner',
        'Account Name': 'Name',
        'Account Type': 'Type',
        'Account Segment': 'Segment',
        'Account Status': 'Status',
        'Call Status (Account)': 'Call Status',
        'Target Call Frequency / Cycle (Account)': 'Target Call Frequency',
        'Last Call Date (Account)': 'Last Call Date'    
    })

    All_Contacts = All_Contacts.rename(columns = {
        'Contact ID': 'ID',
        'Contact Owner': 'Owner',
        'Contact  Type': 'Type',
        'ABCD Grid BGM (Contact) - current': 'Segment',
        'Call Status (Contact)': 'Call Status',
        'Target Call Frequency / Cycle (Contact)': 'Target Call Frequency',
        'Last Call Date (Contact)': 'Last Call Date'    
    })

    visits_pivot = visits.groupby('Account ID').agg({'Date': 'nunique'}).reset_index()
    visits_pivot = visits_pivot.rename(columns={'Date': 'Visit_count', 'Account ID': 'ID'})
    All_Accounts = All_Accounts.merge(visits_pivot[['ID','Visit_count']], on = 'ID', how = 'left')
    All_Accounts['Visit_count'] = All_Accounts['Visit_count'].fillna(0)
    All_Accounts['Account Category'] = All_Accounts['Account Category'].fillna("-")
    All_Accounts['Visit_rate'] = All_Accounts['Visit_count'].map(lambda x: str(int(x))) + "/" + All_Accounts['Target Call Frequency'].map(lambda x: str(int(x)))
    All_Accounts['Visit_percentage'] = All_Accounts['Visit_count'] / All_Accounts['Target Call Frequency']
    All_Accounts['Visited'] = All_Accounts['Visit_count'].map(lambda x: "Y" if x > 0 else "N")

    visits_pivot_contact = visits_contact.groupby('Contact ID').agg({'Date': 'nunique'}).reset_index()
    visits_pivot_contact = visits_pivot_contact.rename(columns={'Date': 'Visit_count', 'Contact ID': 'ID'})
    All_Contacts = All_Contacts.merge(visits_pivot_contact[['ID','Visit_count']], on = 'ID', how = 'left')
    All_Contacts['Visit_count'] = All_Contacts['Visit_count'].fillna(0)
    All_Contacts['Account Category'] = All_Contacts['Account Category'].fillna("-")
    All_Contacts['Visit_rate'] = All_Contacts['Visit_count'].map(lambda x: str(int(x))) + "/" + All_Contacts['Target Call Frequency'].map(lambda x: str(int(x)))
    All_Contacts['Visit_percentage'] = All_Contacts['Visit_count'] / All_Contacts['Target Call Frequency']
    All_Contacts['Visited'] = All_Contacts['Visit_count'].map(lambda x: "Y" if x > 0 else "N")

    prev_visits_pivot = prev_visits.groupby('Account ID').agg({'Date': 'count'}).reset_index()
    prev_visits_pivot = prev_visits_pivot.rename(columns={'Date': 'Visit_count_prev', 'Account ID': 'ID'})
    All_Accounts = All_Accounts.merge(prev_visits_pivot[['ID','Visit_count_prev']], on = 'ID', how = 'left')
    All_Accounts['Visit_count_prev'] = All_Accounts['Visit_count_prev'].fillna(0)
    All_Accounts['NEW'] = All_Accounts['Visit_count_prev'].map(lambda x: "NEW" if x == 0 else " ")

    prev_visits_pivot_contact = prev_visits_contact.groupby('Contact ID').agg({'Date': 'count'}).reset_index()
    prev_visits_pivot_contact = prev_visits_pivot_contact.rename(columns={'Date': 'Visit_count_prev', 'Contact ID': 'ID'})
    All_Contacts = All_Contacts.merge(prev_visits_pivot_contact[['ID','Visit_count_prev']], on = 'ID', how = 'left')
    All_Contacts['Visit_count_prev'] = All_Contacts['Visit_count_prev'].fillna(0)
    All_Contacts['NEW'] = All_Contacts['Visit_count_prev'].map(lambda x: "NEW" if x == 0 else " ")

    All_Accounts['Client Type'] = "Account"
    All_Contacts['Client Type'] = "Contact"
    All_Accounts = All_Accounts[['ID', 'Owner', 'Client Type', 'Name', 'Type', 'Segment', 'Status', 'Call Status',
        'Brick Code', 'Primary State/Province', 'Primary City',
        'Primary Street', 'Account Category', 'Target Call Frequency', 'Lat',
        'Lon', 'Last Visit', 'Last Call Date', 'Last Activity', 'Visit_count',
        'Visit_rate', 'Visit_percentage', 'Visited', 'Visit_count_prev', 'NEW']]
    All_Contacts = All_Contacts[['ID', 'Owner', 'Client Type', 'Name', 'Type', 'Segment', 'Status', 'Call Status',
        'Brick Code', 'Primary State/Province', 'Primary City',
        'Primary Street', 'Account Category', 'Target Call Frequency', 'Lat',
        'Lon', 'Last Visit', 'Last Call Date', 'Last Activity', 'Visit_count',
        'Visit_rate', 'Visit_percentage', 'Visited', 'Visit_count_prev', 'NEW']]

    df_combine = pd.concat([All_Accounts, All_Contacts])
    data = df_combine[df_combine['Owner'] == Rep_name].reset_index()
    data['Lat'] = data['Lat'].fillna(0)
    data['Lon'] = data['Lon'].fillna(0)
    data['Last Visit'] = data['Last Visit'].map(lambda x: str(x).replace("/", "-"))
    data['Last Visit'] = data['Last Visit'].map(lambda x: datetime.strptime(x, '%d-%m-%Y').date() if x!='nan' else 0)
    data['Last Call Date'] = data['Last Call Date'].map(lambda x: str(x).replace("/", "-"))
    data['Last Call Date'] = data['Last Call Date'].map(lambda x: datetime.strptime(x, '%d-%m-%Y').date() if x!='nan' else 0)
    data['Last Activity'] = data['Last Activity'].map(lambda x: str(x).replace("/", "-"))
    data['Last Activity'] = data['Last Activity'].map(lambda x: datetime.strptime(x, '%d-%m-%Y').date() if x!='nan' else 0)
    data['Last Visit Date'] = ""
    for i in range(data['ID'].shape[0]):
        if (data['Last Visit'][i] == 0) & (data['Last Call Date'][i] != 0):
            data.loc[i, 'Last Visit Date'] = data.loc[i, 'Last Call Date']
        elif (data['Last Visit'][i] == 0) & (data['Last Call Date'][i] == 0):
            data.loc[i, 'Last Visit Date'] = data.loc[i, 'Last Activity']
        else:
            data.loc[i, 'Last Visit Date'] = data.loc[i, 'Last Visit']

    return data


def main():
    #Page settings
    st.set_page_config(layout='wide')
    st.title(APP_TITLE)
    
    placeholder = st.empty()
    placeholder.header('Choose your name')
    SR_list.sort()

    cola, colb = st.columns([10, 1])
        
    with cola:
        uploaded_name = st.selectbox("Rep Name", SR_list, index=None, placeholder="Choose your name...")
        if uploaded_name is None:
            st.stop()
        else:
            placeholder.empty()
            if "Rep_name" not in st.session_state:
                st.session_state.Rep_name = uploaded_name
            else:
                st.session_state.Rep_name = uploaded_name
            df = get_data(st.session_state.Rep_name)
    
    with colb:   
        if st.button("🔄 Refresh data", use_container_width=True):
            get_data.clear()
            df = get_data(st.session_state.Rep_name)
    
    #Display filters
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        client_type_list = df['Client Type'].map(lambda x: str(x)).unique()
        for i, n in enumerate(client_type_list):
            if n == "nan":
                client_type_list[i] = "-"
        client_type_list.sort()
        client_type = st.multiselect('Client Type', client_type_list)
    
    with col2:
        account_type_list = df['Type'].map(lambda x: str(x)).unique()
        for i, n in enumerate(account_type_list):
            if n == "nan":
                account_type_list[i] = "-"
        account_type_list.sort()
        account_type = st.multiselect('Type', account_type_list)

    with col3:
        account_segment_list = df['Segment'].map(lambda x: str(x)).unique()
        for i, n in enumerate(account_segment_list):
            if n == "nan":
                account_segment_list[i] = "-"
        account_segment_list.sort()
        account_segment = st.multiselect('Segment', account_segment_list)

    with col4:
        communication_channel_list = df['Account Category'].map(lambda x: str(x)).unique()
        for i, n in enumerate(communication_channel_list):
            if n == "nan":
                communication_channel_list[i] = "-"
        communication_channel_list.sort()
        communication_channel = st.multiselect('Communication Channel', communication_channel_list)
    
    with col5:
        new_list = df['NEW'].map(lambda x: str(x)).unique()
        for i, n in enumerate(new_list):
            if n == "nan":
                new_list[i] = "-"
        new_list.sort()
        new = st.multiselect('New client', new_list)
    
    col6, col7 = st.columns(2)
    with col6:
        start_coverage, end_coverage = st.select_slider(
            "Select a range of coverage",
            options=['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'],
            value=('0%', '100%'))
    
    with col7:
        target = st.slider("Visit target", 0, int(df['Target Call Frequency'].max()), (0, int(df['Target Call Frequency'].max())))

    if client_type == []:
        client_type_filter = client_type_list
    else:
        client_type_filter = client_type
    if account_type == []:
        account_type_filter = account_type_list
    else:
        account_type_filter = account_type
    if account_segment == []:
        account_segment_filter = account_segment_list
    else:
        account_segment_filter = account_segment
    if communication_channel == []:
        communication_channel_filter = communication_channel_list
    else:
        communication_channel_filter = communication_channel
    if new == []:
        new_filter = new_list
    else:
        new_filter = new
    
    
    
    df_filtered = df[(df['Client Type'].isin(client_type_filter))
                     &(df['Type'].isin(account_type_filter))
                     &(df['Segment'].isin(account_segment_filter))
                     &(df['Account Category'].isin(communication_channel_filter))
                     &(df['Visit_percentage'] >= int(start_coverage[:-1]) / 100)
                     &(df['Visit_percentage'] <= int(end_coverage[:-1]) / 100)
                     &(df['NEW'].isin(new_filter))
                     &(df['Target Call Frequency'] >= target[0])
                     &(df['Target Call Frequency'] <= target[1])]

    #Display map
    fol_map = display_map(df_filtered)
    st_folium(fol_map, width=1000, height=850)
    
    #Download
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_filtered.to_excel(writer, sheet_name='Sheet1', index=False)
    st.download_button(label='📥 Download Current Account List',
                                data=buffer,
                                file_name= 'Accounts.xlsx',
                                mime='application/vnd.ms-excel')




if __name__ == "__main__":
    main()
