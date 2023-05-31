import streamlit as st
import pandas as pd
import numpy as np

# improt recommender.py
import recommender


@st.cache
def load_data_c():
    data = pd.DataFrame(db.finance_data.find())
    data['date'] = pd.to_datetime(data['date']).dt.date
    data = data.sort_values(by=['date'], ascending=False)
    return data 

def load_recommend_songs():
    client = MongoClient('mongodb+srv://merve:6CeO8P2piiTklnA9@cluster0.gu4ru.mongodb.net')
    db = client.get_database('finance_data')
    data = pd.DataFrame(db.currency_data.find())    
    data['date'] = pd.to_datetime(data['date']).dt.date
    data.rename(columns = {'exchange_rate':'close'}, inplace = True)
    data = data.sort_values(by=['date'], ascending=False)
    return data 

def load_all_data():
    data_c = load_data_c()
    data_f = load_data_f()
    data = pd.concat([data_c, data_f], axis=0, ignore_index=True)
    data = data.sort_values(by=['date'], ascending=False)
    return data 

def render_info():
    st.title('Finance data')
    st.header('Comparison of finance data')
    st.markdown('Using streamlit to filter and display data fetched from a mongodb database.')

def filter_by_currency(data, key):
    currency_type = st.selectbox('Filter by different currencies:', [''] + list(data['currency'].drop_duplicates()), key=key)
    if currency_type:
        return data[data['currency']==currency_type]
    return data

def select_currency_conversion(data):
    currency_type = st.selectbox('Filter by different currencies:', [''] + list(data['currency'].drop_duplicates()), index=0)
    return currency_type

def filter_by_price(data, key):
    # adding a range slider, allowing to choose values in range
    range = st.slider('Price', min(data['close'].astype(str).astype(float)), max(data['close'].astype(str).astype(float)), (min(data['close'].astype(str).astype(float)), max(data['close'].astype(str).astype(float))), key=key)
    return data[( (data['close'].astype(str).astype(float)).between(*range))]

def filter_by_date(data, key):
    # adding a range slider, allowing to choose values in range
    range = st.slider('Date', min(data['date']), max(data['date']), (min(data['date']), max(data['date'])), key=key)
    return data[( (data['date']).between(*range))]

def select_date(data, label):
    date = st.date_input(label=label, value= max(data['date']), min_value=min(data['date']), max_value=max(data['date']))
    return date

def conversion(data_all, currency, number, date_from, date_to):
    if(currency != ""):
        data = data_all[(data_all['date'] == date_from) & (data_all['currency'] == currency)]
        #first conversion
        if(data.empty):
            st.write("No data found for this date")
        else:
            if(data.loc[data.index[0], 'currency_type'] == "crypto"):
                convert=number / data.loc[data.index[0], 'close']
            else:
                convert=number * data.loc[data.index[0], 'close']
            st.write("The value of ", number, "€ in ", currency, " is on that date " + date_from.strftime("%d.%m.%Y") + " " + str(convert))

        #second conversion
        data = data_all[(data_all['date'] == date_to) & (data_all['currency'] == currency)]
        if(data.empty):
            st.write("No data found for this date")
        else: 
            if(data.loc[data.index[0], 'currency_type']  == "crypto"):
                value=convert * data.loc[data.index[0], 'close']
            else:
                value=convert / data.loc[data.index[0], 'close']
            st.write("The value of ", convert, " ", currency, " in € is on that date " + date_to.strftime("%d.%m.%Y"), str(value))

        if(value<number):
            st.write("You lost ", number-value, "€")
        else:
            st.write("You won ", value-number, "€")
        
        return data_all[(data_all['date']>=date_from) & (data_all['date']<=date_to) & (data_all['currency'] == currency)]
    else:
        return data_all


render_info()

data_c = load_data_c()
data_f = load_data_f()
data_all = load_all_data()

#data = filter_by_currency(data)

tab1, tab2, tab3, tab4 = st.tabs(["Cryptocurrencies", "Fiat currency","Conversion", "Top 5"])

with tab1:
    st.header("Development of crypto currencies over time")
    data_c = filter_by_date(data_c, key="date_crypto")
    data_c = filter_by_price(data_c, key="price_crypto")
    data_c = filter_by_currency(data_c, key="currency_crypto")
    st.line_chart(data_c, x="date", y="close")
    with st.expander("See data"):
        st.dataframe(data_c)
        st.write("The data above contains the data which is used in the chart above")

with tab2:
    st.header("Development of fiat currencies over time")
    data_f = filter_by_date(data_f, key="date_fiat")
    data_f = filter_by_price(data_f, key="price_fiat")
    data_f = filter_by_currency(data_f, key="currency_fiat")
    st.line_chart(data_f, x="date", y="close")

    with st.expander("See data"):
        st.dataframe(data_f)
        st.write("The data above contains the data which is used in the chart above")


with tab3:
    number = st.number_input('Insert a amount to convert')
    currency = select_currency_conversion(data_all)
    date_from = select_date(data_all, label="From date")
    date_to = select_date(data_all, label="To date")
    data_all = conversion(data_all, currency, number, date_from, date_to)
    st.line_chart(data_all, x="date", y="close")
    with st.expander("See data"):
        st.dataframe(data_all)

with tab4:
    st.header("Top 5 crypto currencies by volume")
    top5 = data_c.groupby('currency').sum().sort_values(by='vol_fiat', ascending=False).head(5)
    st.dataframe(top5)

