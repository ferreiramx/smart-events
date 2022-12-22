import streamlit as st
import plotly.express as px
import pandas as pd
import utils
import config

utils.load_css()
utils.env_config()

event_id = st.session_state["event_id"]
price_threshold = st.session_state["price_threshold"]
event_data = st.session_state["event_data"]
similar_events = st.session_state["similar_events"]

utils.draw_header()

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

    t1, t2, t3 = st.tabs(
        ["Este evento", "Eventos similares", "Comparativa"])

    with t1:
        if len(data) > 0:
            fig = px.line(data, x="DIAS_A_LA_VENTA", y="COMPRAS", color_discrete_sequence=[config.ORANGE],
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
            fig = px.line(similar_data, x="DIAS_A_LA_VENTA", y="COMPRAS", color_discrete_sequence=[config.ORANGE],
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
                          color_discrete_sequence=[config.ORANGE, config.BLUE], labels={"DIAS_A_LA_VENTA": "DIAS A LA VENTA"})
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
    dow_order = {"DIA": ["Lunes", "Martes", "Miercoles",
                         "Jueves", "Viernes", "Sabado", "Domingo"]}
    data = utils.load_bookings_by_week_day([event_id])
    similar_data = utils.load_bookings_by_week_day(
        similar_events["EVENT_ID"].astype(str).values.tolist())

    # Normalizing data for comparing
    normalized_data = data.copy()
    normalized_similar_data = similar_data.copy()
    normalized_data['TOTAL_BOOKINGS'] = normalized_data['TOTAL_BOOKINGS'] / \
        normalized_data['TOTAL_BOOKINGS'].sum() * 100
    normalized_data['TOTAL_BOOKINGS'] = round(
        normalized_data['TOTAL_BOOKINGS'], 2)
    normalized_similar_data['TOTAL_BOOKINGS'] = normalized_similar_data['TOTAL_BOOKINGS'] / \
        normalized_similar_data['TOTAL_BOOKINGS'].sum() * 100
    normalized_similar_data['TOTAL_BOOKINGS'] = round(
        normalized_similar_data['TOTAL_BOOKINGS'], 2)
    comp_data = utils.join_data(normalized_data, normalized_similar_data)

    t1, t2, t3 = st.tabs(
        ["Este evento", "Eventos similares", "Comparativa"])

    with t1:
        if len(data) > 0:
            fig = px.bar(data, x="DIA", y="TOTAL_BOOKINGS",
                         orientation='v', category_orders=dow_order, color_discrete_sequence=[config.ORANGE],
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
                         orientation='v', category_orders=dow_order, color_discrete_sequence=[config.ORANGE],
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
                         category_orders=dow_order, color_discrete_sequence=[
                             config.ORANGE, config.BLUE],
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
    comp_data = utils.join_data(data.copy(), similar_data.copy()).sort_values(
        by='COMPRAS', ascending=False).reset_index()

    # Normalizing data for comparing
    normalized_data = data.copy()
    normalized_similar_data = similar_data.copy()
    normalized_data['COMPRAS'] = normalized_data['COMPRAS'] / \
        normalized_data['COMPRAS'].sum() * 100
    normalized_data['COMPRAS'] = round(normalized_data['COMPRAS'], 2)
    normalized_similar_data['COMPRAS'] = normalized_similar_data['COMPRAS'] / \
        normalized_similar_data['COMPRAS'].sum() * 100
    normalized_similar_data['COMPRAS'] = round(
        normalized_similar_data['COMPRAS'], 2)
    normalized_comp_data = utils.join_data(
        normalized_data, normalized_similar_data)

    # Building the legend for te plot
    comp_data['PM'] = ''
    for i in comp_data.index:
        comp_data['PM'][i] = comp_data['PAYMENT_METHOD'][i] + \
            '\t' + str(comp_data['COMPRAS'][i])

    t1, t2, t3 = st.tabs(
        ["Este evento", "Eventos similares", "Comparativa"])

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
            fig = px.bar(comp_data[comp_data['EVENTO'] == 'Este evento'], y='EVENTO', x="COMPRAS", barmode='stack',
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
            fig = px.bar(comp_data[comp_data['EVENTO'] == 'Similares'], y='EVENTO', x="COMPRAS", barmode='stack',
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
                         labels={'PAYMENT_METHOD': 'METODO DE COMPRA',
                                 'COMPRAS': '% DE VENTAS'},
                         hover_name='PAYMENT_METHOD', hover_data={'COMPRAS': True, 'EVENTO': False, 'PAYMENT_METHOD': False})
            fig.update_layout({
                'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)',
            })
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos en este momento.")
