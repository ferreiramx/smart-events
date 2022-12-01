import streamlit as st
import plotly.express as px
import pandas as pd
import utils
import config
from datetime import datetime

st.set_page_config(layout="wide")


# Sidebar
st.sidebar.header("Configuración")

# Read variables from config if prod deployment, else let the user write it in
if config.TARGET == 'DEV':
    pages = ["Eventos Similares", "Compras", "Demográfica", "Ventas", "Fuentes"]
    selected_page = st.sidebar.selectbox("Pagina", pages, 0)
    event_id = st.sidebar.text_input("Event ID", "201898")
    price_threshold = st.sidebar.slider("% rango de precio", min_value=0.0, max_value=1.0, value=0.1)
elif config.TARGET in ['PROD', 'DEMO']:
    pages = ["Compras", "Demográfica", "Ventas", "Fuentes"]
    selected_page = st.sidebar.selectbox("Pagina", pages, 0)
    event_id = config.EVENT_ID
    price_threshold = config.PRICE_RANGE
event_data = utils.load_event_data(event_id)

# If hardcoded similar events are set, use them
if config.SIMILAR_EVENTS == '':
    similar_events = utils.load_similar_events(event_id, price_threshold)
else:
    similar_events = utils.load_static_event_list(config.SIMILAR_EVENTS.split(','))


# Streamlit page title
st.title('Boletia Smart Events')
st.metric(label="Evento", value=f"{event_data['NAME'] if config.TARGET != 'DEMO' else 'Ejemplo'}", delta=None)


# Columns for event info
info_1, info_2, info_3 = st.columns(3, gap="small")
info_1.metric(
    label="Categoría",
    value=f"{event_data['SUBCATEGORY']  if config.TARGET != 'DEMO' else 'Evento'}",
    delta=None)
info_2.metric(
    label="Ubicación",
    value=f"{event_data['CITY'] if config.TARGET != 'DEMO' else 'Ciudad'}, {event_data['STATE'] if config.TARGET != 'DEMO' else 'Estado'}",
    delta=None)
info_3.metric(
    label="Inicio",
    value=f"{event_data['STARTED_AT'].strftime('%d/%m/%Y %H:%M')  if config.TARGET != 'DEMO' else '2023-01-01'}",
    delta=None)

st.write("---", unsafe_allow_html=True)


if selected_page == "Eventos Similares":
    st.subheader("Eventos similares")
    st.dataframe(similar_events)


if selected_page == "Compras":
    # Columns for sales info
    c1, c2, c3 = st.columns(3, gap="large")
    c1.metric(
        label="Compras Finalizadas",
        value=event_data['BOOKINGS_COMPLETED'],
        delta=None
    )
    c2.metric(
        label="Boletos Vendidos",
        value=event_data['TICKETS_SOLD'],
        delta=None
    )
    c3.metric(
        label="Ventas Netas",
        value="${:0,.2f}".format(event_data['TOTAL_TICKET_SALES']),
        delta=None
    )

    bookings_container = st.container()
    with bookings_container:
        L, R = st.columns(2, gap="large")
        # Create visualization for COMPRAS
        L.subheader('Momento de compra')
        data = utils.load_bookings_by_date([event_id])
        if len(data) > 0:
            fig = px.line(data, x="DIAS_A_LA_VENTA", y="COMPRAS")
            L.plotly_chart(fig, use_container_width=True)
        else:
            L.warning("No hay datos en este momento.")

        R.subheader('Vs eventos similares')
        comp_data = utils.load_bookings_by_date(
            similar_events["EVENT_ID"].astype(str).values.tolist())
        if len(comp_data) > 0:
            fig = px.line(comp_data, x="DIAS_A_LA_VENTA", y="COMPRAS")
            R.plotly_chart(fig, use_container_width=True)
        else:
            R.warning("No hay datos en este momento.")

    dow_container = st.container()
    with dow_container:
        L, R = st.columns(2, gap="large")
        # Create visualization for COMPRAS POR DIA DE LA SEMANA
        dow_order = {"DIA": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}
        L.subheader('Compras por día de la semana')
        data = utils.load_bookings_by_week_day([event_id])
        if len(data) > 0:
            fig = px.bar(data, y="DIA", x="TOTAL_BOOKINGS",
                        orientation='h', category_orders=dow_order)
            L.plotly_chart(fig, use_container_width=True)
        else:
            L.warning("No hay datos en este momento.")

        R.subheader('Vs eventos similares')
        comp_data = utils.load_bookings_by_week_day(
            similar_events["EVENT_ID"].astype(str).values.tolist())
        if len(comp_data) > 0:
            fig = px.bar(comp_data, y="DIA", x="TOTAL_BOOKINGS",
                        orientation='h', category_orders=dow_order)
            R.plotly_chart(fig, use_container_width=True)
        else:
            R.warning("No hay datos en este momento.")

    payment_method_container = st.container()
    with payment_method_container:
        L, R = st.columns(2, gap="large")
        # Create visualization for COMPRAS
        L.subheader('Métodos de pago')
        data = utils.load_bookings_by_payment_method([event_id])
        if len(data) > 0:
            fig = px.pie(data, names="PAYMENT_METHOD", color="PAYMENT_METHOD", values="COMPRAS", hole=.3)
            L.plotly_chart(fig, use_container_width=True)
        else:
            L.warning("No hay datos en este momento.")

        R.subheader('Vs eventos similares')
        comp_data = utils.load_bookings_by_payment_method(
            similar_events["EVENT_ID"].astype(str).values.tolist())
        if len(comp_data) > 0:
            fig = px.pie(comp_data, names="PAYMENT_METHOD", color="PAYMENT_METHOD", values="COMPRAS", hole=.3)
            R.plotly_chart(fig, use_container_width=True)
        else:
            R.warning("No hay datos en este momento.")


if selected_page == "Demográfica":
    cities_container = st.container()
    with cities_container:
        # Create visualization for CITIES
        st.subheader('Ubicación de los compradores')
        data = utils.load_bookings_by_city(event_id)
        data = utils.get_coordinates(data)
        #st.write(data)
        if len(data) > 0:
            fig = px.scatter_geo(data, lat='LAT', lon='LON', size='TOTAL_BOOKINGS',
                        hover_name='CITY', color='TOTAL_BOOKINGS', size_max=50,
                        projection="natural earth")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos en este momento.")

    age_container = st.container()
    with age_container:
        L, R = st.columns(2, gap="large")
        # Create visualization for EDAD
        L.subheader('Edad')
        data = utils.load_customers_by_age([event_id])
        if len(data) > 0:
            fig = px.bar(data, y="AGE_BRACKET", x="TOTAL_BOOKINGS", orientation='h')
            L.plotly_chart(fig, use_container_width=True)
        else:
            L.warning("No hay datos en este momento.")

        R.subheader('Edad - Eventos similares')
        comp_data = utils.load_customers_by_age(similar_events["EVENT_ID"].astype(str).values.tolist())
        if len(comp_data) > 0:
            fig = px.bar(comp_data, y="AGE_BRACKET", x="TOTAL_BOOKINGS", orientation='h')
            R.plotly_chart(fig, use_container_width=True)
        else:
            R.warning("No hay datos en este momento.")
            R.empty()

    gender_container = st.container()
    with gender_container:
        L, R = st.columns(2, gap="large")
        # Create visualization for Género
        gender_colormap = {"female": "pink", "male": "royalblue"}
        L.subheader('Género')
        data = utils.load_customers_by_gender([event_id])
        if len(data) > 0:
            fig = px.pie(data, values='TOTAL_BOOKINGS', names='GENDER', color='GENDER',
                        hole=.3, color_discrete_map=gender_colormap)
            L.plotly_chart(fig, use_container_width=True)
        else:
            L.warning("No hay datos en este momento.")
        R.subheader('Género - Eventos similares')
        comp_data = utils.load_customers_by_gender(
            similar_events["EVENT_ID"].astype(str).values.tolist())
        if len(comp_data) > 0:
            fig = px.pie(comp_data, values='TOTAL_BOOKINGS', names='GENDER', color='GENDER',
                            hole=.3, color_discrete_map=gender_colormap)
            R.plotly_chart(fig, use_container_width=True)
        else:
            R.warning("No hay datos en este momento.")


if selected_page == "Fuentes":
    funnel_source_medium_container = st.container()
    with funnel_source_medium_container:
        # Create visualization for SALES FUNNEL BY SOURCE/MEDIUM
        st.subheader('Funnel de ventas por fuente y medio')
        data = utils.load_pageviews_by_source_medium(event_id)
        if len(data) > 0:
            data = utils.get_funnel(data, 'SOURCE_MEDIUM')
            st.write(data)
        else:
            st.warning("No hay datos en este momento.")

    piechart_container = st.container()
    with piechart_container:
        # Create visualization for SALES BY SOURCE MEDIUM
        L, R = st.columns(2, gap="large")
        L.subheader('Compras por fuente y medio')
        if len(data) > 0:
            data = pd.DataFrame({'Compras': data.loc['Pago']}).astype('float')
            complete_data = data[data['Compras'] > 0].astype('int')
            if len(complete_data) > 0:
                MIN_PAGEVIEWS = 30
                data = utils.adjust_to_piechart(complete_data.copy(), MIN_PAGEVIEWS)
                fig = px.pie(data, values='Compras', names=data.index)
                L.plotly_chart(fig, use_container_width=True)
                R.subheader('Fuentes y medios completos')
                R.write(complete_data.sort_values(by='Compras', ascending=False))
            else:
                L.warning("No hay datos en este momento.")
        else:
            L.warning("No hay datos en este momento.")


if selected_page == "Ventas":
    sales_funnel_container = st.container()
    with sales_funnel_container:
        # Create visualization for SALES FUNNEL
        L, R = st.columns(2, gap="large")
        L.subheader('Funnel de ventas')
        data = utils.load_pageviews(event_id)
        if data[data['PAGE_PATH'] == 'Inicio']['PAGEVIEWS'].all(0):
            fig = px.funnel(data, x='PAGEVIEWS', y="PAGE_PATH")
            L.plotly_chart(fig, use_container_width=True)
        else:
            L.warning("No hay datos en este momento.")

        # Create metric for SALES CONVERSION RATE
        R.subheader('Tasa de conversion de ventas')
        if data[data['PAGE_PATH'] == 'Inicio']['PAGEVIEWS'].all(0):
            print(data)
            CR = float(data[data['PAGE_PATH'] == 'Pago']["PAGEVIEWS"]) / float(data[data['PAGE_PATH'] == 'Inicio']["PAGEVIEWS"]) * 100
            CR = "%.2f" % CR  # formating to 2 decimals
            R.metric(label="Conversion Rate", value=f'{CR}%', delta=None)
        else:
            R.warning("No hay datos en este momento.")

    funnel_medium_container = st.container()
    with funnel_medium_container:
        # Create visualization for SALES FUNNEL BY MEDIUM
        st.subheader('Funnel de ventas por fuente')
        data = utils.load_pageviews_by_medium(event_id)
        if len(data) > 0:
            data = utils.get_funnel(data, 'MEDIUM')
            st.write(data)
        else:
            st.warning("No hay datos en este momento.")
