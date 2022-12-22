import streamlit as st
import pandas as pd
import plotly.express as px
import utils
import config

utils.load_css()
utils.draw_header()

event_id = st.session_state["event_id"]
event_data = st.session_state["event_data"]
similar_events = st.session_state["similar_events"]

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
    info_1.caption(
        'País donde los usuarios realizan la mayor cantidad de compras')
    info_2.metric(
        label="Ciudad con mayor número de compras",
        value=f"{data['CITY'][data['TOTAL_BOOKINGS'].idxmax()]}",
        delta=None)
    info_2.caption(
        'La ciudad desde donde se realizan el mayor número de compra de boletos')
    info_3.metric(
        label="Países con compra",
        value=f"{len(pd.unique(data['COUNTRY']))}",
        delta=None)
    info_3.caption(
        'Total de países desde donde se han comprado boletos para el evento')

    # Visualization
    if len(data) > 0:
        fig = px.scatter_geo(data, lat='LAT', lon='LON', size='TOTAL_BOOKINGS',
                             hover_name='CITY', hover_data={'LAT': False, 'LON': False}, size_max=18,
                             color_discrete_sequence=[config.ORANGE],
                             labels={'TOTAL_BOOKINGS': 'COMPRAS'},
                             fitbounds="geojson",
                             )
        fig.update_geos(showcountries=True, showsubunits=True)
        fig.update_layout({
            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
            'margin': {"r": 0, "t": 0, "l": 0, "b": 0}
        })
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos en este momento.")

# SALES BY AGE
age_container = st.container()
with age_container:
    st.subheader('Edades')
    data = utils.load_customers_by_age([event_id])
    similar_data = utils.load_customers_by_age(
        similar_events["EVENT_ID"].astype(str).values.tolist())
    comp_data = utils.join_data(data.copy(), similar_data.copy())

    t1, t2, t3 = st.tabs(
        ["Este evento", "Eventos similares", "Comparativa"])

    with t1:
        total = data['TOTAL_BOOKINGS'].sum()
        best = f'{data.iloc[data["TOTAL_BOOKINGS"].idxmax(), :]["AGE_BRACKET"]} años'
        total_best = data.iloc[data["TOTAL_BOOKINGS"].idxmax(),
                               :]["TOTAL_BOOKINGS"]
        if total < 100:
            st.warning(
                "Los datos demográficos dependen de que Google perfile un volumen suficiente de usuarios, por lo cual no se garantiza tener esta información para todos los compradores.", icon="⚠️")
        info_1, info_2, info_3 = st.columns(3, gap="small")
        info_1.metric(
            label="Total de usuarios",
            value=f"{total}",
            delta=None)
        info_1.caption("Total de compradores perfilados")

        info_2.metric(
            label="Segmento más fuerte",
            value=f"{best}",
            delta=None)
        info_2.caption(
            f'Representan el {"%.2f" % (total_best  * 100 / total)}% del total de compradores')

        # Visualization
        if len(data) > 0:
            fig = px.histogram(data, x="AGE_BRACKET", y="TOTAL_BOOKINGS", orientation='v',
                               color='AGE_BRACKET',
                               labels={'AGE_BRACKET': 'RANGOS DE EDAD', 'TOTAL_BOOKINGS': 'COMPRAS'})
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
        total = similar_data['TOTAL_BOOKINGS'].sum()
        best = f'{similar_data.iloc[similar_data["TOTAL_BOOKINGS"].idxmax(), :]["AGE_BRACKET"]} años'
        total_best = similar_data.iloc[similar_data["TOTAL_BOOKINGS"].idxmax(),
                                       :]["TOTAL_BOOKINGS"]
        info_1, info_2, info_3 = st.columns(3, gap="small")
        info_1.metric(
            label="Total de compradores",
            value=f"{total}",
            delta=None)
        info_1.caption("Compradores con edad reportada")

        info_2.metric(
            label="Segmento más fuerte",
            value=f"{best}",
            delta=None)
        info_2.caption(
            f'Representan el {"%.2f" % (total_best  * 100 / total)}% del total de compradores')

        # Visualization
        if len(similar_data) > 0:
            fig = px.histogram(similar_data, x="AGE_BRACKET", y="TOTAL_BOOKINGS", orientation='v',
                               color='AGE_BRACKET',
                               labels={'AGE_BRACKET': 'RANGOS DE EDAD', 'TOTAL_BOOKINGS': 'COMPRAS'})
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
            fig = px.histogram(comp_data, x="AGE_BRACKET", y="TOTAL_BOOKINGS", facet_col="EVENTO", color="AGE_BRACKET",
                               labels={'AGE_BRACKET': 'RANGOS DE EDAD', 'TOTAL_BOOKINGS': 'COMPRAS'})
            fig.update_layout({
                'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',
            })
            fig.update_yaxes(gridcolor="rgba(0,0,0,0.1)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos en este momento.")
            st.empty()

# SALES BY GENDER
gender_container = st.container()
with gender_container:
    st.subheader('Género')
    data = utils.load_customers_by_gender([event_id])
    similar_data = utils.load_customers_by_gender(
        similar_events["EVENT_ID"].astype(str).values.tolist())
    comp_data = utils.join_data(data.copy(), similar_data.copy())

    t1, t2, t3 = st.tabs(
        ["Este evento", "Eventos similares", "Comparativa"])

    with t1:
        # Metrics
        total_female = data[data['GENDER'] ==
                            'Mujeres']['TOTAL_BOOKINGS'].sum()
        total_male = data[data['GENDER'] ==
                          'Hombres']['TOTAL_BOOKINGS'].sum()
        total = data['TOTAL_BOOKINGS'].sum()
        if total < 100:
            st.warning(
                "Los datos demográficos dependen de que Google perfile un volumen suficiente de usuarios, por lo cual no se garantiza tener esta información para todos los compradores.", icon="⚠️")
        info_1, info_2, info_3 = st.columns(3, gap="small")
        info_1.metric(
            label="Total de usuarios con género reportado",
            value=f"{total}",
            delta=None)
        info_1.caption(
            'Total de compradores perfilados')

        info_2.metric(
            label="Mujeres",
            value=f"{total_female}",
            delta=None)
        info_2.caption(
            f'Representan el {"%.2f" % (total_female  * 100 / total)}% del total de usuarios')
        info_3.metric(
            label="Hombres",
            value=f"{total_male}",
            delta=None)
        info_3.caption(
            f'Representan el {"%.2f" % (total_male  * 100 / total)}% del total de usuarios')

        # Visualization
        if len(data) > 0:
            fig = px.histogram(data, x="GENDER", y="TOTAL_BOOKINGS", orientation='v',
                               color='GENDER', color_discrete_map={'Hombres': config.BLUE, 'Mujeres': config.ORANGE},
                               labels={'TOTAL_BOOKINGS': 'COMPRAS', 'GENDER': 'GENERO'})
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
        total_female = similar_data[similar_data['GENDER']
                                    == 'Mujeres']['TOTAL_BOOKINGS'].sum()
        total_male = similar_data[similar_data['GENDER']
                                  == 'Hombres']['TOTAL_BOOKINGS'].sum()
        total = similar_data['TOTAL_BOOKINGS'].sum()
        info_1, info_2, info_3 = st.columns(3, gap="small")
        info_1.metric(
            label="Total de usuarios con género reportado",
            value=f"{total}",
            delta=None)
        info_1.caption(
            'Total de usuarios que finalizaron el proceso de compra')

        info_2.metric(
            label="Mujeres",
            value=f"{total_female}",
            delta=None)
        info_2.caption(
            f'Representan el {"%.2f" % (total_female * 100 / total)}% del total de usuarios')
        info_3.metric(
            label="Hombres",
            value=f"{total_male}",
            delta=None)
        info_3.caption(
            f'Representan el {"%.2f" % (total_male * 100 / total)}% del total de usuarios')

        # Visualization
        if len(similar_data) > 0:
            fig = px.histogram(similar_data, x="GENDER", y="TOTAL_BOOKINGS", orientation='v',
                               color='GENDER', color_discrete_map={'Hombres': config.BLUE, 'Mujeres': config.ORANGE},
                               labels={'TOTAL_BOOKINGS': 'COMPRAS', 'GENDER': 'GENERO'})
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
            fig = px.histogram(comp_data, x="GENDER", y="TOTAL_BOOKINGS", facet_col="EVENTO", color="GENDER",
                               color_discrete_map={
                                   'Hombres': config.BLUE, 'Mujeres': config.ORANGE},
                               labels={'TOTAL_BOOKINGS': 'COMPRAS', 'GENDER': 'GENERO'})
            fig.update_layout({
                'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',
            })
            fig.update_yaxes(gridcolor="rgba(0,0,0,0.1)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos en este momento.")
            st.empty()

# SALES BY AGE AND GENDER
gender_and_age_container = st.container()
with gender_and_age_container:
    st.subheader('Edad y género')
    data = utils.load_customers_by_gender_age([event_id])
    similar_data = utils.load_customers_by_gender_age(
        similar_events["EVENT_ID"].astype(str).values.tolist())
    comp_data = utils.join_data(data.copy(), similar_data.copy())

    t1, t2, t3 = st.tabs(
        ["Este evento", "Eventos similares", "Comparativa"])

    with t1:
        # Metrics
        total = data['TOTAL_BOOKINGS'].sum()
        if len(data[data["GENDER"] == "Hombres"]) > 0:
            best_m = f'{data.iloc[data[data["GENDER"] == "Hombres"]["TOTAL_BOOKINGS"].idxmax(), :]["AGE_BRACKET"]} años'
            total_best_m = data.iloc[data[data["GENDER"] == "Hombres"]["TOTAL_BOOKINGS"].idxmax(),
                                     :]["TOTAL_BOOKINGS"]
        else:
            best_m = "N/A"
            total_best_m = 0
        if len(data[data["GENDER"] == "Mujeres"]) > 0:
            best_f = f'{data.iloc[data[data["GENDER"] == "Mujeres"]["TOTAL_BOOKINGS"].idxmax(), :]["AGE_BRACKET"]} años'
            total_best_f = data.iloc[data[data["GENDER"] == "Mujeres"]["TOTAL_BOOKINGS"].idxmax(),
                                     :]["TOTAL_BOOKINGS"]
        else:
            best_f = "N/A"
            total_best_f = 0
        if total < 100:
            st.warning(
                "Los datos demográficos dependen de que Google perfile un volumen suficiente de usuarios, por lo cual no se garantiza tener esta información para todos los compradores.", icon="⚠️")
        info_1, info_2, info_3 = st.columns(3, gap="small")
        info_1.metric(
            label="Total de usuarios",
            value=f"{total}",
            delta=None)
        info_1.caption(
            'Total de compradores perfilados')

        info_2.metric(
            label="Segmento más fuerte en mujeres",
            value=f"{best_f}",
            delta=None)
        info_2.caption(
            f'Representan el {"%.2f" % (total_best_f  * 100 / total)}% del total de usuarios')
        info_3.metric(
            label="Segmento más fuerte en hombres",
            value=f"{best_m}",
            delta=None)
        info_3.caption(
            f'Representan el {"%.2f" % (total_best_m  * 100 / total)}% del total de usuarios')

        # Visualization
        if len(data) > 0:
            fig = px.histogram(data, x="AGE_BRACKET", y="TOTAL_BOOKINGS", orientation='v', barmode='group',
                               color='GENDER', color_discrete_map={'Hombres': config.BLUE, 'Mujeres': config.ORANGE},
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
        total = similar_data['TOTAL_BOOKINGS'].sum()
        if len(similar_data[similar_data["GENDER"] == "Hombres"]) > 0:
            best_m = f'{similar_data.iloc[similar_data[similar_data["GENDER"] == "Hombres"]["TOTAL_BOOKINGS"].idxmax(), :]["AGE_BRACKET"]} años'
            total_best_m = similar_data.iloc[similar_data[similar_data["GENDER"] == "Hombres"]["TOTAL_BOOKINGS"].idxmax(),
                                             :]["TOTAL_BOOKINGS"]
        else:
            best_m = "N/A"
            total_best_m = 0
        if len(similar_data[similar_data["GENDER"] == "Mujeres"]) > 0:
            best_f = f'{similar_data.iloc[similar_data[similar_data["GENDER"] == "Mujeres"]["TOTAL_BOOKINGS"].idxmax(), :]["AGE_BRACKET"]} años'
            total_best_f = similar_data.iloc[similar_data[similar_data["GENDER"] == "Mujeres"]["TOTAL_BOOKINGS"].idxmax(),
                                             :]["TOTAL_BOOKINGS"]
        else:
            best_f = "N/A"
            total_best_f = 0
        if total < 100:
            st.warning(
                "Los datos demográficos dependen de que Google perfile un volumen suficiente de usuarios, por lo cual no se garantiza tener esta información para todos los compradores.", icon="⚠️")
        info_1, info_2, info_3 = st.columns(3, gap="small")
        info_1.metric(
            label="Total de usuarios",
            value=f"{total}",
            delta=None)
        info_1.caption(
            'Total de compradores perfilados')

        info_2.metric(
            label="Segmento más fuerte en mujeres",
            value=f"{best_f}",
            delta=None)
        info_2.caption(
            f'Representan el {"%.2f" % (total_best_f  * 100 / total)}% del total de usuarios')
        info_3.metric(
            label="Segmento más fuerte en hombres",
            value=f"{best_m}",
            delta=None)
        info_3.caption(
            f'Representan el {"%.2f" % (total_best_m  * 100 / total)}% del total de usuarios')

        # Visualization
        if len(similar_data) > 0:
            fig = px.histogram(similar_data, x="AGE_BRACKET", y="TOTAL_BOOKINGS", orientation='v', barmode='group',
                               color='GENDER', color_discrete_map={'Hombres': config.BLUE, 'Mujeres': config.ORANGE},
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
                               color_discrete_map={
                                   'Hombres': config.BLUE, 'Mujeres': config.ORANGE},
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
