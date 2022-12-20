import streamlit as st
import plotly.express as px
import pandas as pd
import utils
import config
from datetime import datetime

st.set_page_config(layout="wide")

# COLOR MACROS
ORANGE = '#FF8766'
BLUE = '#5E9FEC'
ORANGE_TRANS = '#FFDAD1'
GREY_LIGHT = '#353F48'
WHITE1 = '#FAFAFA'
GREY_DARK = '#545763'
LOGO = 'BoletiaLogoOrange.png'

# Loading CSS
utils.local_css('frontend/streamlit.css')
utils.remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')


# Sidebar
st.sidebar.image(f"frontend/{LOGO}")

# Read variables from config if prod deployment, else let the user write it in
if config.TARGET == 'DEV':
    pages = ["Eventos Similares", "Compras", "Demográfica", "Ventas", "Fuentes"]
    selected_page = st.sidebar.selectbox("Pagina", pages, 0)
    event_id = st.sidebar.text_input("Event ID", "208150")
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

header = st.container()
with header:
    # Streamlit page title
    st.title(f"{event_data['NAME'] if config.TARGET != 'DEMO' else 'Ejemplo'}")

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
        value=f"{event_data['STARTED_AT'].strftime('%d/%m/%Y %H:%M hrs')  if config.TARGET != 'DEMO' else '2023-01-01'}",
        delta=None)

if selected_page == "Eventos Similares":
    similar_events_container = st.container()
    with similar_events_container:
        st.subheader("Eventos similares")
        st.dataframe(similar_events)


if selected_page == "Compras":
    # Metrics
    c1, c2, c3 = st.columns(3, gap="large")
    c1.metric(
        label="Total de compras",
        value=event_data['BOOKINGS_COMPLETED'],
        delta=None
    )
    c1.caption('Número de transacciones completadas')
    c2.metric(
        label="Boletos vendidos",
        value=event_data['TICKETS_SOLD'],
        delta=None
    )
    c2.caption('Total de boletos vendidos')
    c3.metric(
        label="Total de ventas",
        value="${:0,.2f}".format(event_data['TOTAL_TICKET_SALES']),
        delta=None
    )
    c3.caption('Ventas netas por concepto de boletos')


    # SALES BY DAYS
    bookings_container = st.container()
    with bookings_container:
        st.subheader('Momento de compra')
        st.caption('Compra de boletos por cada día desde el inicio de la venta')
        data = utils.load_bookings_by_date([event_id])
        similar_data = utils.load_bookings_by_date(
            similar_events["EVENT_ID"].astype(str).values.tolist())
        comp_data = utils.join_data(data.copy(), similar_data.copy())

        t1, t2, t3 = st.tabs(["Este evento", "Eventos similares", "Comparativa"])

        with t1:
            if len(data) > 0:
                fig = px.line(data, x="DIAS_A_LA_VENTA", y="COMPRAS", color_discrete_sequence=[ORANGE],
                              labels={"DIAS_A_LA_VENTA": "DIAS A LA VENTA"})
                fig.update_layout({
                            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        })
                fig.update_yaxes(gridcolor="rgba(0,0,0,0.1)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos en este momento.")

        with t2:
            if len(similar_data) > 0:
                fig = px.line(similar_data, x="DIAS_A_LA_VENTA", y="COMPRAS", color_discrete_sequence=[ORANGE],
                              labels={"DIAS_A_LA_VENTA": "DIAS A LA VENTA"})
                fig.update_layout({
                            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        })
                fig.update_yaxes(gridcolor="rgba(0,0,0,0.1)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos en este momento.")

        with t3:
            if len(comp_data) > 0:
                fig = px.line(comp_data, x="DIAS_A_LA_VENTA", y="COMPRAS", color='EVENTO',
                              color_discrete_sequence=[ORANGE, BLUE], labels={"DIAS_A_LA_VENTA": "DIAS A LA VENTA"})
                fig.update_layout({
                            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        })
                fig.update_yaxes(gridcolor="rgba(0,0,0,0.1)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos en este momento.")


    # SALES BY DAY OF THE WEEK
    dow_container = st.container()
    with dow_container:
        st.subheader('Compras por día de la semana')
        st.caption('Preferencia de compra por dia de la semana.')
        dow_order = {"DIA": ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]}
        data = utils.load_bookings_by_week_day([event_id])
        similar_data = utils.load_bookings_by_week_day(
            similar_events["EVENT_ID"].astype(str).values.tolist())

        # Normalizing data for comparing
        normalized_data = data.copy()
        normalized_similar_data = similar_data.copy()
        normalized_data['TOTAL_BOOKINGS'] = normalized_data['TOTAL_BOOKINGS'] / normalized_data['TOTAL_BOOKINGS'].sum() * 100
        normalized_data['TOTAL_BOOKINGS'] = round(normalized_data['TOTAL_BOOKINGS'], 2)
        normalized_similar_data['TOTAL_BOOKINGS'] = normalized_similar_data['TOTAL_BOOKINGS'] / normalized_similar_data['TOTAL_BOOKINGS'].sum() * 100
        normalized_similar_data['TOTAL_BOOKINGS'] = round(normalized_similar_data['TOTAL_BOOKINGS'], 2)
        comp_data = utils.join_data(normalized_data, normalized_similar_data)

        t1, t2, t3 = st.tabs(["Este evento", "Eventos similares", "Comparativa"])

        with t1:
            if len(data) > 0:
                fig = px.bar(data, x="DIA", y="TOTAL_BOOKINGS",
                            orientation='v', category_orders=dow_order, color_discrete_sequence=[ORANGE],
                             labels={"TOTAL_BOOKINGS": "COMPRAS"})
                fig.update_layout({
                            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        })
                fig.update_yaxes(gridcolor="rgba(0,0,0,0.1)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos en este momento.")

        with t2:
            if len(similar_data) > 0:
                fig = px.bar(similar_data, x="DIA", y="TOTAL_BOOKINGS",
                            orientation='v', category_orders=dow_order, color_discrete_sequence=[ORANGE],
                             labels={"TOTAL_BOOKINGS": "COMPRAS"})
                fig.update_layout({
                            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        })
                fig.update_yaxes(gridcolor="rgba(0,0,0,0.1)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos en este momento.")

        with t3:
            if len(comp_data) > 0:
                fig = px.bar(comp_data, x="DIA", y="TOTAL_BOOKINGS", color='EVENTO', barmode='group',
                              category_orders=dow_order, color_discrete_sequence=[ORANGE, BLUE],
                             labels={"TOTAL_BOOKINGS": "% DE VENTAS"})
                fig.update_layout({
                            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        })
                fig.update_yaxes(gridcolor="rgba(0,0,0,0.1)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos en este momento.")
    
    # PAYMENT METHOD PIE CHART  
    payment_method_container = st.container()
    with payment_method_container:
        st.subheader('Métodos de pago')
        st.caption('Preferencia en métodos de pago.')
        data = utils.load_bookings_by_payment_method([event_id])
        similar_data = utils.load_bookings_by_payment_method(
            similar_events["EVENT_ID"].astype(str).values.tolist())
        comp_data = utils.join_data(data.copy(), similar_data.copy()).sort_values(by='COMPRAS', ascending=False).reset_index()

        # Normalizing data for comparing
        normalized_data = data.copy()
        normalized_similar_data = similar_data.copy()
        normalized_data['COMPRAS'] = normalized_data['COMPRAS'] / normalized_data['COMPRAS'].sum() * 100
        normalized_data['COMPRAS'] = round(normalized_data['COMPRAS'], 2)
        normalized_similar_data['COMPRAS'] = normalized_similar_data['COMPRAS'] / normalized_similar_data['COMPRAS'].sum() * 100
        normalized_similar_data['COMPRAS'] = round(normalized_similar_data['COMPRAS'], 2)
        normalized_comp_data = utils.join_data(normalized_data, normalized_similar_data)

        # Building the legend for te plot
        comp_data['PM'] = ''
        for i in comp_data.index:
            comp_data['PM'][i] = comp_data['PAYMENT_METHOD'][i] + '\t' + str(comp_data['COMPRAS'][i])

        t1, t2, t3 = st.tabs(["Este evento", "Eventos similares", "Comparativa"])

        with t1:
            # Metrics
            info_1, info_2, info_3 = st.columns(3, gap="small")
            info_1.metric(
                label="Total de pagos realizados",
                value=f"{data['COMPRAS'].sum()}",
                delta=None)
            info_1.caption('Número de pagos realizados durante el evento')
            info_2.metric(
                label="Método de pago más popular",
                value=f"{data['PAYMENT_METHOD'][data['COMPRAS'].idxmax()]}",
                delta=None)
            info_2.caption(
                f"Se han realizado {data['COMPRAS'][data['COMPRAS'].idxmax()]} pagos con {data['PAYMENT_METHOD'][data['COMPRAS'].idxmax()]}")
            info_3.metric(
                label="Métodos de pago disponibles",
                value=f"{len(pd.unique(data['PAYMENT_METHOD']))}",
                delta=None)
            info_3.caption('Opciones de pago disponibles para este evento')

            # Visualization
            if len(data) > 0:
                fig = px.bar(comp_data[comp_data['EVENTO']=='Este evento'], y='EVENTO', x="COMPRAS", barmode='stack',
                             color='PM', labels={"PAYMENT_METHOD": "METODO DE COMPRA", "PM": "METODO DE PAGO"},
                             hover_name='PAYMENT_METHOD', hover_data={'PM': False, 'COMPRAS': True, 'EVENTO': False})
                # Option-3: using fig.update_layout() + dict-flattening shorthand
                fig.update_layout({
                        "yaxis_visible": False, 
                        "xaxis_visible": False,
                        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        })
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos en este momento.")

        with t2:
            # Metrics
            info_1, info_2, info_3 = st.columns(3, gap="small")
            info_1.metric(
                label="Total de pagos realizados",
                value=f"{similar_data['COMPRAS'].sum()}",
                delta=None)
            info_1.caption('Número de pagos realizados durante el evento')
            info_2.metric(
                label="Método de pago más popular",
                value=f"{similar_data['PAYMENT_METHOD'][similar_data['COMPRAS'].idxmax()]}",
                delta=None)
            info_2.caption(
                f"Se han realizado {similar_data['COMPRAS'][similar_data['COMPRAS'].idxmax()]} pagos con {similar_data['PAYMENT_METHOD'][similar_data['COMPRAS'].idxmax()]}")
            info_3.metric(
                label="Métodos de pago disponibles",
                value=f"{len(pd.unique(similar_data['PAYMENT_METHOD']))}",
                delta=None)
            info_3.caption('Opciones de pago disponibles para este evento')

            # Visualization
            if len(similar_data) > 0:
                fig = px.bar(comp_data[comp_data['EVENTO']=='Similares'], y='EVENTO', x="COMPRAS", barmode='stack',
                             color='PM', labels={"PAYMENT_METHOD": "METODO DE COMPRA", "PM": "METODO DE PAGO"},
                             hover_name='PAYMENT_METHOD', hover_data={'PM': False, 'COMPRAS': True, 'EVENTO': False})
                fig.update_layout({
                        "yaxis_visible": False, 
                        "xaxis_visible": False,
                        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        })
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos en este momento.")

        with t3:
            if len(normalized_comp_data) > 0:
                fig = px.bar(normalized_comp_data.sort_values(by='COMPRAS', ascending=False), y='EVENTO', x='COMPRAS', barmode='stack', color='PAYMENT_METHOD',
                             labels={'PAYMENT_METHOD': 'METODO DE COMPRA', 'COMPRAS': '% DE VENTAS'},
                             hover_name='PAYMENT_METHOD', hover_data={'COMPRAS': True, 'EVENTO': False, 'PAYMENT_METHOD': False})
                fig.update_layout({
                        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        })
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos en este momento.")


if selected_page == "Demográfica":
    # SALES MAP
    cities_container = st.container()
    with cities_container:
        st.subheader('Ubicación de los compradores')
        st.caption('Mapa de tus compradores por ubicación geográfica')
        data = utils.load_bookings_by_city(event_id)
        data = utils.get_coordinates(data)

        # Metrics
        info_1, info_2, info_3 = st.columns(3, gap="small")
        info_1.metric(
            label="País con más compras",
            value=f"{data['COUNTRY'][data['TOTAL_BOOKINGS'].idxmax()]}",
            delta=None)
        info_1.caption('País donde los usuarios realizan la mayor cantidad de compras')
        info_2.metric(
            label="Ciudad con mayor número de compras",
            value=f"{data['CITY'][data['TOTAL_BOOKINGS'].idxmax()]}",
            delta=None)
        info_2.caption('La ciudad desde donde se realizan el mayor número de compra de boletos')
        info_3.metric(
            label="Países con compra",
            value=f"{len(pd.unique(data['COUNTRY']))}",
            delta=None)
        info_3.caption('Total de países desde donde se han comprado boletos para el evento')

        # Visualization
        if len(data) > 0:
            fig = px.scatter_geo(data, lat='LAT', lon='LON', size='TOTAL_BOOKINGS',
                                 hover_name='CITY', hover_data={'LAT': False, 'LON': False}, size_max=18,
                                 color_discrete_sequence=[ORANGE], 
                                 labels={'TOTAL_BOOKINGS': 'COMPRAS'},
                                 fitbounds="geojson",
            )
            fig.update_geos(showcountries=True, showsubunits=True)
            fig.update_layout({
                        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        'margin':{"r":0, "t":0, "l":0, "b":0}
                        })
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos en este momento.")

    # SALES BY AGE AND GENDER
    age_container = st.container()
    with age_container:
        st.subheader('Rango de edad')
        data = utils.load_customers_by_gender_age([event_id])
        similar_data = utils.load_customers_by_gender_age(similar_events["EVENT_ID"].astype(str).values.tolist())
        comp_data = utils.join_data(data.copy(), similar_data.copy())

        t1, t2, t3 = st.tabs(["Este evento", "Eventos similares", "Comparativa"])

        with t1:
            # Metrics
            total_female = data[data['GENDER']=='Mujeres']['TOTAL_BOOKINGS'].sum()
            total_male = data[data['GENDER']=='Hombres']['TOTAL_BOOKINGS'].sum()
            total = data['TOTAL_BOOKINGS'].sum()
            info_1, info_2, info_3 = st.columns(3, gap="small")
            info_1.metric(
                label="Total de usuarios",
                value=f"{total}",
                delta=None)
            info_1.caption('Total de usuarios que finalizaron el proceso de compra')

            info_2.metric(
                label="Mujeres",
                value=f"{total_female}",
                delta=None)
            info_2.caption(f'Representan el {"%.2f" % (total_female  * 100 / total)}% del total de usuarios')
            info_3.metric(
                label="Hombres",
                value=f"{total_male}",
                delta=None)
            info_3.caption(f'Representan el {"%.2f" % (total_male  * 100 / total)}% del total de usuarios')

            # Visualization
            if len(data) > 0:
                fig = px.histogram(data, x="AGE_BRACKET", y="TOTAL_BOOKINGS", orientation='v', barmode='group',
                             color='GENDER', color_discrete_map={'Hombres': BLUE, 'Mujeres': ORANGE},
                             labels={'AGE_BRACKET': 'RANGOS DE EDAD', 'TOTAL_BOOKINGS': 'COMPRAS', 'GENDER': 'GENERO'})
                fig.update_layout({
                            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        })
                fig.update_yaxes(gridcolor="rgba(0,0,0,0.1)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos en este momento.")

        with t2:
            # Metrics
            total_female = similar_data[similar_data['GENDER'] == 'Mujeres']['TOTAL_BOOKINGS'].sum()
            total_male = similar_data[similar_data['GENDER'] == 'Hombres']['TOTAL_BOOKINGS'].sum()
            total = similar_data['TOTAL_BOOKINGS'].sum()
            info_1, info_2, info_3 = st.columns(3, gap="small")
            info_1.metric(
                label="Total de usuarios",
                value=f"{total}",
                delta=None)
            info_1.caption('Total de usuarios que finalizaron el proceso de compra')

            info_2.metric(
                label="Mujeres",
                value=f"{total_female}",
                delta=None)
            info_2.caption(f'Representan el {"%.2f" % (total_female * 100 / total)}% del total de usuarios')
            info_3.metric(
                label="Hombres",
                value=f"{total_male}",
                delta=None)
            info_3.caption(f'Representan el {"%.2f" % (total_male * 100 / total)}% del total de usuarios')

            # Visualization
            if len(similar_data) > 0:
                fig = px.histogram(similar_data, x="AGE_BRACKET", y="TOTAL_BOOKINGS", orientation='v', barmode='group',
                             color='GENDER', color_discrete_map={'Hombres': BLUE, 'Mujeres': ORANGE},
                             labels={'AGE_BRACKET': 'RANGOS DE EDAD', 'TOTAL_BOOKINGS': 'COMPRAS', 'GENDER': 'GENERO'})
                fig.update_layout({
                            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        })
                fig.update_yaxes(gridcolor="rgba(0,0,0,0.1)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos en este momento.")
                st.empty()

        with t3:
            if len(comp_data) > 0:
                fig = px.histogram(comp_data, x="AGE_BRACKET", y="TOTAL_BOOKINGS", facet_col="EVENTO", color="GENDER",
                             color_discrete_map={'Hombres': BLUE, 'Mujeres': ORANGE},
                             labels={'AGE_BRACKET': 'RANGOS DE EDAD', 'TOTAL_BOOKINGS': 'COMPRAS', 'GENDER': 'GENERO'})
                fig.update_layout({
                            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        })
                fig.update_yaxes(gridcolor="rgba(0,0,0,0.1)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos en este momento.")
                st.empty()


if selected_page == "Ventas":
    #SALES FUNNEL GENERAL AND BY MEDIUM
    sources_dict = {
        "General": {
            "title": "General",
            "caption": "Agregado de todas las fuentes de tráfico"
        },
        "Directo": {
            "title": "Tráfico Directo",
            "caption": "Usuarios que entran directamente a Boletia.com y buscan el evento"
        },
        "Orgánico": {
            "title": "Búsqueda Orgánica",
            "caption": "Usuarios que entran a la página del evento desde algún buscador como Google o Bing"
        },
        "Referido": {
            "title": "Referidos",
            "caption": "Usuarios que son dirigidos a la página del evento desde algún sitio web en particular"
        },
        "Social": {
            "title": "Redes Sociales",
            "caption": "Usuarios que entran a la página del evento desde alguna publicación no pagada en redes sociales"
        },
        "Paid Social": {
            "title": "Publicidad en Redes Sociales",
            "caption": "Usuarios que entran a la página del evento desde algún anuncio pagado en redes sociales"
        }
    }
    funnel_medium_container = st.container()
    with funnel_medium_container:
        funnel_order = {"PAGE_PATH": ["Inicio", "Info", "Checkout", "Pago"]}
        st.subheader('Proceso de compra')
        st.caption("Representación visual de la proporción de usuarios que proceden a cada fase del proceso de compra de boletos")
        data = utils.load_pageviews_by_medium(event_id)
        tabs_names = utils.get_5_sources_mediums(data, 'MEDIUM')
        tabs_names.insert(0, 'General')
        tabs = st.tabs(tabs_names)

        for i in range(len(tabs)):

            with tabs[i]:
                st.subheader(sources_dict[tabs_names[i]]["title"])
                st.caption(sources_dict[tabs_names[i]]["caption"])
                # Slicing the specific source data
                if i == 0:
                    # for general funnel
                    source_data = utils.load_pageviews(event_id)
                else:
                    # for mediums funnels
                    source_data = data[data['MEDIUM'] == tabs_names[i]]
                
                # Metrics
                info_1, info_2, info_3 = st.columns(3, gap="small")
                try:
                    total_users = int(source_data[source_data['PAGE_PATH'] == 'Inicio']['PAGEVIEWS'])
                except:
                    total_users = 0
                try:
                    total_sells = int(source_data[source_data['PAGE_PATH'] == 'Pago']['PAGEVIEWS'])
                except:
                    total_sells = 0
                if total_users == 0:
                    CR = 0
                else:
                    CR = total_sells / total_users * 100
                CR = "%.2f" % CR  # formating to 2 decimals
                info_1.metric(label='Total de usuarios', value=f'{total_users}')
                info_1.caption('Número de usuarios que inician el flujo de compra')
                info_2.metric(label='Ventas totales', value=f'{total_sells}')
                info_2.caption('Número de usuarios que finalizan el flujo de compra')
                info_3.metric(label="Tasa de conversion", value=f'{CR}%', delta=None)
                info_3.caption('Porcentaje total de usuarios que concretan la compra de boletos')

                # Visualization
                if len(source_data) > 0:
                    # Completing the funnel data
                    funnel_data = utils.convert_to_funnel(source_data)
                    fig = px.bar(funnel_data, x="PAGE_PATH", y="PAGEVIEWS", orientation='v', height = 300,
                                color_discrete_sequence=[ORANGE, ORANGE_TRANS], category_orders=funnel_order,
                                labels={'PAGE_PATH': 'ETAPA', 'PAGEVIEWS': 'USUARIOS'}, color='DATOS',
                                hover_name='DATOS', hover_data={'DATOS': False, 'PAGEVIEWS': True, 'PAGE_PATH': False})
                    fig.update_layout({
                        "showlegend": False,
                        "xaxis_visible": False,
                        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        'margin':{"r":0, "t":0, "l":0, "b":0}
                        })
                    fig.update_yaxes(gridcolor="rgba(0,0,0,0.1)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No hay datos en este momento.")
                # Dummy container so we can add margin to this info without affecting other containers
                funnel_stages_dummy_container = st.container()
                with funnel_stages_dummy_container:
                    stage1, stage2, stage3, stage4 = st.columns(4)
                    with stage1:
                        st.caption(":orange[Paso 1]")
                        st.caption("**Landing del evento**")
                        num_users = int(source_data[source_data["PAGE_PATH"] == "Inicio"]["PAGEVIEWS"].values[0] if len(source_data[source_data["PAGE_PATH"] == "Inicio"]) > 0 else 0)
                        pct_users = "%.1f" % (100 * num_users / total_users)
                        st.markdown(f'**{pct_users}%**')
                        st.caption(f'{num_users}')

                    with stage2:
                        st.caption(":orange[Paso 2]")
                        st.caption("**Información del cliente**")
                        num_users = int(source_data[source_data["PAGE_PATH"] == "Info"]["PAGEVIEWS"].values[0] if len(source_data[source_data["PAGE_PATH"] == "Info"]) > 0 else 0)
                        pct_users = "%.1f" % (100 * num_users / total_users)
                        st.markdown(f'**{pct_users}%**')
                        st.caption(f'{num_users}')

                    with stage3:
                        st.caption(":orange[Paso 3]")
                        st.caption("**Selección de método de pago**")
                        num_users = int(source_data[source_data["PAGE_PATH"] == "Checkout"]["PAGEVIEWS"].values[0] if len(source_data[source_data["PAGE_PATH"] == "Checkout"]) > 0 else 0)
                        pct_users = "%.1f" % (100 * num_users / total_users)
                        st.markdown(f'**{pct_users}%**')
                        st.caption(f'{num_users}')

                    with stage4:
                        st.caption(":orange[Paso 4]")
                        st.caption("**Compra finalizada**")
                        num_users = int(source_data[source_data["PAGE_PATH"] == "Pago"]["PAGEVIEWS"].values[0] if len(source_data[source_data["PAGE_PATH"] == "Pago"]) > 0 else 0)
                        pct_users = "%.1f" % (100 * num_users / total_users)
                        st.markdown(f'**{pct_users}%**')
                        st.caption(f'{num_users}')


if selected_page == "Fuentes":
    # SALES FUNNEL BY SOURCE/MEDIUM
    funnel_source_medium_container = st.container()
    with funnel_source_medium_container:
        funnel_order = {"PAGE_PATH": ["Inicio", "Info", "Checkout", "Pago"]}
        st.subheader('Proceso de compra por fuente y medio')
        st.caption("Representación visual de la proporción de usuarios que proceden a cada fase del proceso de compra de boletos, desglosado por fuente")
        data = utils.load_pageviews_by_source_medium(event_id)
        tabs_names = utils.get_5_sources_mediums(data, 'SOURCE_MEDIUM')
        tabs = st.tabs(tabs_names)
        
        for i in range(len(tabs)):

            with tabs[i]:
                # Slicing the specific source data
                source_data = data[data['SOURCE_MEDIUM'] == tabs_names[i]]

                # Metrics
                info_1, info_2, info_3 = st.columns(3, gap="small")
                try:
                    total_users = int(source_data[source_data['PAGE_PATH'] == 'Inicio']['PAGEVIEWS'])
                except:
                    total_users = 0
                try:
                    total_sells = int(source_data[source_data['PAGE_PATH'] == 'Pago']['PAGEVIEWS'])
                except:
                    total_sells = 0
                if total_users == 0:
                    CR = 0
                else:
                    CR = total_sells / total_users * 100
                CR = "%.2f" % CR  # formating to 2 decimals
                info_1.metric(label='Total de usuarios', value=f'{total_users}')
                info_1.caption('Número de usuarios que inician el flujo de compra')
                info_2.metric(label='Ventas totales', value=f'{total_sells}')
                info_2.caption('Número de usuarios que finalizan el flujo de compra')
                info_3.metric(label="Tasa de conversion", value=f'{CR}%', delta=None)
                info_3.caption('Porcentaje total de usuarios que concretan la compra de boletos')

                # Visualization
                if len(source_data) > 0:
                    # Completing the funnel data
                    funnel_data = utils.convert_to_funnel(source_data)
                    fig = px.bar(funnel_data, x="PAGE_PATH", y="PAGEVIEWS", orientation='v', height=300,
                                color_discrete_sequence=[ORANGE, ORANGE_TRANS], category_orders=funnel_order,
                                labels={'PAGE_PATH': 'ETAPA', 'PAGEVIEWS': ''}, color='DATOS',
                                hover_name='DATOS', hover_data={'DATOS': False, 'PAGEVIEWS': True, 'PAGE_PATH': False})
                    fig.update_layout({
                        "showlegend": False,
                        "xaxis_visible": False,
                        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        'margin':{"r":0, "t":0, "l":0, "b":0}
                        })
                    fig.update_yaxes(gridcolor="rgba(0,0,0,0.1)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No hay datos en este momento.")
                # Dummy container so we can add margin to this info without affecting other containers
                funnel_stages_dummy_container = st.container()
                with funnel_stages_dummy_container:
                    stage1, stage2, stage3, stage4 = st.columns(4)
                    with stage1:
                        st.caption(":orange[Paso 1]")
                        st.caption("**Landing del evento**")
                        num_users = int(source_data[source_data["PAGE_PATH"] == "Inicio"]["PAGEVIEWS"].values[0] if len(source_data[source_data["PAGE_PATH"] == "Inicio"]) > 0 else 0)
                        pct_users = "%.1f" % (100 * num_users / total_users)
                        st.markdown(f'**{pct_users}%**')
                        st.caption(f'{num_users}')

                    with stage2:
                        st.caption(":orange[Paso 2]")
                        st.caption("**Información del cliente**")
                        num_users = int(source_data[source_data["PAGE_PATH"] == "Info"]["PAGEVIEWS"].values[0] if len(source_data[source_data["PAGE_PATH"] == "Info"]) > 0 else 0)
                        pct_users = "%.1f" % (100 * num_users / total_users)
                        st.markdown(f'**{pct_users}%**')
                        st.caption(f'{num_users}')

                    with stage3:
                        st.caption(":orange[Paso 3]")
                        st.caption("**Selección de método de pago**")
                        num_users = int(source_data[source_data["PAGE_PATH"] == "Checkout"]["PAGEVIEWS"].values[0] if len(source_data[source_data["PAGE_PATH"] == "Checkout"]) > 0 else 0)
                        pct_users = "%.1f" % (100 * num_users / total_users)
                        st.markdown(f'**{pct_users}%**')
                        st.caption(f'{num_users}')

                    with stage4:
                        st.caption(":orange[Paso 4]")
                        st.caption("**Compra finalizada**")
                        num_users = int(source_data[source_data["PAGE_PATH"] == "Pago"]["PAGEVIEWS"].values[0] if len(source_data[source_data["PAGE_PATH"] == "Pago"]) > 0 else 0)
                        pct_users = "%.1f" % (100 * num_users / total_users)
                        st.markdown(f'**{pct_users}%**')
                        st.caption(f'{num_users}')


    # SALES PIE CHART BY SOURCE/MEDIUM PIE CHART
    piechart_container = st.container()
    with piechart_container:
        st.subheader('Compras por fuente y medio')
        data = utils.get_funnel(data, 'SOURCE_MEDIUM')

        # Visualization
        if len(data) > 0:
            data = pd.DataFrame({'Compras': data.loc['Pago']}).astype('float')
            complete_data = data[data['Compras'] > 0].astype('int')
            if len(complete_data) > 0:
                data = utils.adjust_to_piechart(complete_data.copy(),5)
                fig = px.pie(data, values='Compras', names='SM', hole=0.75, hover_name='SOURCE_MEDIUM',
                             labels={'Compras': 'COMPRAS', 'SOURCE_MEDIUM': 'FUENTE/MEDIO', 'SM': 'FUENTE/MEDIO'},
                             hover_data={'SM': False, 'SOURCE_MEDIUM': True})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos en este momento.")
        else:
            st.warning("No hay datos en este momento.")
