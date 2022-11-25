import snowflake.connector
import config
import streamlit as st
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
from geopy.geocoders import Nominatim


ctx = snowflake.connector.connect(
    user=config.USER,
    password=config.PASSWORD,
    account=config.ACCOUNT,
    warehouse=config.WAREHOUSE,
    database=config.DATABASE,
    schema=config.SCHEMA
)
cur = ctx.cursor()

# Get event metadata


@st.cache
def load_event_data(event_id):
    # Execute a query to extract the data
    sql = f"""select
                event_id,
                name,
                subcategory,
                city,
                state,
                convert_timezone('UTC', 'America/Mexico_City', started_at) as started_at,
                bookings_completed,
                tickets_sold,
                total_ticket_sales
            from EVENTS.EVENTS
            where event_id = {event_id}
            """
    cur.execute(sql)
    # Converting data into a dataframe
    df = cur.fetch_pandas_all()
    return df.to_dict('records')[0] if len(df) > 0 else None

# Get comparable events


@st.cache
def load_similar_events(event_id, price_threshold):
    # Execute a query to extract the data
    sql = f"""with base_event as
                (select event_id, subcategory, city, state, average_ticket_price, channel_type
                from PROD.EVENTS.EVENTS
                where event_id = {event_id}
                )
            select
                event_id,
                name,
                subcategory,
                city,
                state,
                average_ticket_price,
                channel_type
            from PROD.EVENTS.EVENTS
            where subcategory = (select subcategory from base_event)
            --and state = (select state from base_event)
            and channel_type = (select channel_type from base_event)
            and average_ticket_price between (select average_ticket_price from base_event) * {1.0 - price_threshold} and (select average_ticket_price from base_event) * {1.0 + price_threshold}
            and tickets_sold_with_cost > 0
            and event_id <> (select event_id from base_event)
            and ended_at < current_timestamp
            """
    cur.execute(sql)
    # Converting data into a dataframe
    df = cur.fetch_pandas_all()
    return df

# Function to get the total number of bookings by date


@st.cache
def load_bookings_by_date(event_id):
    # Execute a query to extract the data
    sql = f"""
            select
                timestampdiff(
                    day,
                    convert_timezone('America/Mexico_City', coalesce(e.activated_at, e.created_at)),
                    convert_timezone('America/Mexico_City', cb.paid_at)
                    ) as dias_a_la_venta,
                count(*) as compras
            from PROD.EVENTS.COMPLETED_BOOKINGS cb
            left join prod.events.events e on e.event_id = cb.event_id
            where cb.event_id in ({','.join(event_id)})
            and cb.paid_at > coalesce(e.activated_at, e.created_at)
            group by 1
            order by 1
            """
    cur.execute(sql)
    # Converting data into a dataframe
    df = cur.fetch_pandas_all()
    return df

@st.cache
def load_bookings_by_payment_method(event_id):
    # Execute a query to extract the data
    sql = f"""
            select
                payment_method,
                count(*) as compras
            from PROD.EVENTS.COMPLETED_BOOKINGS cb
            left join prod.events.events e on e.event_id = cb.event_id
            where cb.event_id in ({','.join(event_id)})
            and cb.paid_at > coalesce(e.activated_at, e.created_at)
            group by 1
            order by 1
            """
    cur.execute(sql)
    # Converting data into a dataframe
    df = cur.fetch_pandas_all()
    return df

# Function to get the total number of customers by age bracket


@st.cache
def load_customers_by_age(event_id):
    # Execute a query to extract the data
    sql = f"""select *
                from EVENTS.CUSTOMER_DEMOGRAPHICS_AGE
                where event_id in ({','.join(event_id)})
                order by age_bracket
                """
    cur.execute(sql)
    # Converting data into a dataframe
    df = cur.fetch_pandas_all()
    return df

# Function to get the total number of customer by gender


@st.cache
def load_customers_by_gender(event_id):
    # Execute a query to extract the data
    sql = f"""select *
                    from EVENTS.CUSTOMER_DEMOGRAPHICS_GENDER
                    where event_id in ({','.join(event_id)})
                    """
    cur.execute(sql)
    # Converting data into a dataframe
    df = cur.fetch_pandas_all()
    return df

# Function to get the total number of bookings by day of the week


@st.cache
def load_bookings_by_week_day(event_id):
    # Execute a query to extract the data
    sql = f"""select dayname(convert_timezone('America/Mexico_City', paid_at)) as dia, count(booking_id) as total_bookings
                from EVENTS.COMPLETED_BOOKINGS
                where event_id in ({','.join(event_id)})
                group by dia
                order by total_bookings
                """
    cur.execute(sql)
    # Converting data into a dataframe
    df = cur.fetch_pandas_all()
    return df


# Function to get the coordinates (lat and long) of each city
@st.cache
def get_coordinates(df):
    geolocator = Nominatim(user_agent='Boletia_GA')
    df['LAT'] = np.nan
    df['LON'] = np.nan
    for i in df.index:
        location = geolocator.geocode(df['CITY'][i])
        df['LAT'][i] = location.latitude
        df['LON'][i] = location.longitude
    return df


# Function to get the events pageviews
@st.cache
def load_pageviews(event_id):
    # Execute a query to extract the data
    sql = f"""select
                case
                    when PAGE_PATH like '%/finish' then 'Pago'
                    when PAGE_PATH like '%/pay' then 'Checkout'
                    when PAGE_PATH like '%/info' then 'Info'
                    else 'Inicio'
                end as PAGE_PATH,
                SOURCE_MEDIUM,
                PAGEVIEWS
                from EVENTS.SALES_FUNNELS
                where SUBDOMAIN =
                    (select subdomain
                    from EVENTS.EVENTS
                    where EVENT_ID = {event_id})
                and PAGE_PATH in (
                                  SUBDOMAIN || '.boletia.com/',
                                  SUBDOMAIN || '.boletia.com/info',
                                  SUBDOMAIN || '.boletia.com/pay',
                                  SUBDOMAIN || '.boletia.com/finish')
                order by PAGEVIEWS desc
                    """
    cur.execute(sql)
    # Converting data into a dataframe
    df = cur.fetch_pandas_all()
    return df


# Function to pivot the data and process the table
@st.cache
def get_funnel(df):
    stages = CategoricalDtype(["Inicio", "Info", "Checkout", "Pago"], ordered=True)
    df["PAGE_PATH"] = df["PAGE_PATH"].astype(stages)
    df.sort_values('PAGE_PATH')
    # pivot the source_medium values into columns
    df = df.pivot_table('PAGEVIEWS', 'PAGE_PATH', 'SOURCE_MEDIUM')
    # replacing nan values to zeros
    df = df.fillna(0)
    df = df.T
    df['Tasa de conversión'] = df.apply(lambda x: f"{round(x['Pago'] / x['Inicio'] * 100,2)}%", axis = 1)
    df = df.astype('str')
    df = df.T
    return df


# Function to get the total number of bookings by city
@st.cache(allow_output_mutation=True)
def load_bookings_by_city(event_id):
    # Execute a query to extract the data
    sql = f"""select *
                from EVENTS.CUSTOMER_DEMOGRAPHICS_CITY
                where event_id = {event_id}
                order by TOTAL_BOOKINGS DESC
                """
    cur.execute(sql)
    # Converting data into a dataframe
    df = cur.fetch_pandas_all()
    return df
