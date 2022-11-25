import streamlit as st
import plotly.express as px
import utils
from datetime import datetime

st.set_page_config(layout="wide")

# Pages

pages = ["Eventos Similares", "Compras", "Demográfica", "Fuentes"]

# Sidebar
st.sidebar.header("Configuración")
selected_page = st.sidebar.selectbox("Pagina", pages, 0)
event_id = st.sidebar.text_input("Event ID", "201898")
event_data = utils.load_event_data(event_id)
price_threshold = st.sidebar.slider(
    "% rango de precio", min_value=0.0, max_value=1.0, value=0.1)
similar_events = utils.load_similar_events(event_id, price_threshold)


# Streamlit page title
st.title('Boletia Smart Events')
st.metric(label="Evento", value=f"{event_data['NAME']}", delta=None)
#st.metric(label="Evento", value="Ejemplo", delta=None)

# Columns for event info
info_1, info_2, info_3 = st.columns(3, gap="small")
info_1.metric(
    label="Categoría",
    value=f"{event_data['SUBCATEGORY']}",
    delta=None)
info_2.metric(
    label="Ubicación",
    value=f"{event_data['CITY']}, {event_data['STATE']}",
    #value=f"{event_data['CITY']}",
    delta=None)
info_3.metric(
    label="Inicio",
    value=f"{event_data['STARTED_AT'].strftime('%d/%m/%Y %H:%M')}",
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
        if len(data) > 0:
            fig = px.scatter_geo(data, lat='LAT', lon='LON', size='TOTAL_BOOKINGS',
                        hover_name='CITY', color='TOTAL_BOOKINGS', size_max=50,
                        scope='north america', projection="natural earth")
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
    # Create visualization for SALES FUNNEL of the event
    st.subheader('Funnel de ventas por fuente y medio')
    data = utils.load_pageviews(event_id)
    if len(data) > 0:
        data = utils.get_funnel(data)
        
        st.write(data)
    else:
        st.warning("No hay datos en este momento.")
