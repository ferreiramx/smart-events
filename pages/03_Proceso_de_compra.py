import streamlit as st
import plotly.express as px
import utils
import config

utils.load_css()
utils.draw_header()

event_id = st.session_state["event_id"]
event_data = st.session_state["event_data"]
similar_events = st.session_state["similar_events"]

# SALES FUNNEL GENERAL AND BY MEDIUM
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
    },
    "Sendgrid": {
        "title": "Sendgrid (Mailing)",
        "caption": "Usuarios que entran desde un correo electrónico"
    }
}
funnel_medium_container = st.container()
with funnel_medium_container:
    funnel_order = {"PAGE_PATH": ["Inicio", "Info", "Checkout", "Pago"]}
    st.subheader('Proceso de compra')
    st.caption(
        "Representación visual de la proporción de usuarios que proceden a cada fase del proceso de compra de boletos")
    data = utils.load_pageviews_by_medium(event_id)
    tabs_names = utils.get_5_sources_mediums(data, 'MEDIUM')
    tabs_names.insert(0, 'General')
    tabs = st.tabs(tabs_names)

    for i in range(len(tabs)):

        with tabs[i]:
            if tabs_names[i] in sources_dict.keys():
                st.subheader(sources_dict[tabs_names[i]]["title"])
                st.caption(sources_dict[tabs_names[i]]["caption"])
            else:
                st.subheader(tabs_names[i])

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
                total_users = int(
                    source_data[source_data['PAGE_PATH'] == 'Inicio']['PAGEVIEWS'])
            except Exception:
                total_users = 0
            try:
                total_sells = int(
                    source_data[source_data['PAGE_PATH'] == 'Pago']['PAGEVIEWS'])
            except Exception:
                total_sells = 0
            if total_users == 0:
                CR = 0
            else:
                CR = total_sells / total_users * 100
            CR = "%.2f" % CR  # formating to 2 decimals
            info_1.metric(label='Total de usuarios',
                          value=f'{total_users}')
            info_1.caption(
                'Número de usuarios que inician el flujo de compra')
            info_2.metric(label='Ventas totales', value=f'{total_sells}')
            info_2.caption(
                'Número de usuarios que finalizan el flujo de compra')
            info_3.metric(label="Tasa de conversion",
                          value=f'{CR}%', delta=None)
            info_3.caption(
                'Porcentaje total de usuarios que concretan la compra de boletos')

            # Visualization
            if len(source_data) > 0:
                # Completing the funnel data
                funnel_data = utils.convert_to_funnel(source_data)
                fig = px.bar(funnel_data, x="PAGE_PATH", y="PAGEVIEWS", orientation='v', height=300,
                             color_discrete_sequence=[
                                 config.ORANGE, config.ORANGE_TRANS], category_orders=funnel_order,
                             labels={'PAGE_PATH': 'ETAPA', 'PAGEVIEWS': 'USUARIOS'}, color='DATOS',
                             hover_name='DATOS', hover_data={'DATOS': False, 'PAGEVIEWS': True, 'PAGE_PATH': False})
                fig.update_layout({
                    "showlegend": False,
                    "xaxis_visible": False,
                    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                    'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                    'margin': {"r": 0, "t": 0, "l": 0, "b": 0}
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
                    num_users = int(source_data[source_data["PAGE_PATH"] == "Inicio"]["PAGEVIEWS"].values[0] if len(
                        source_data[source_data["PAGE_PATH"] == "Inicio"]) > 0 else 0)
                    pct_users = "%.1f" % (100 * num_users / total_users)
                    st.markdown(f'**{pct_users}%**')
                    st.caption(f'{num_users}')

                with stage2:
                    st.caption(":orange[Paso 2]")
                    st.caption("**Información del cliente**")
                    num_users = int(source_data[source_data["PAGE_PATH"] == "Info"]["PAGEVIEWS"].values[0] if len(
                        source_data[source_data["PAGE_PATH"] == "Info"]) > 0 else 0)
                    pct_users = "%.1f" % (100 * num_users / total_users)
                    st.markdown(f'**{pct_users}%**')
                    st.caption(f'{num_users}')

                with stage3:
                    st.caption(":orange[Paso 3]")
                    st.caption("**Selección de método de pago**")
                    num_users = int(source_data[source_data["PAGE_PATH"] == "Checkout"]["PAGEVIEWS"].values[0] if len(
                        source_data[source_data["PAGE_PATH"] == "Checkout"]) > 0 else 0)
                    pct_users = "%.1f" % (100 * num_users / total_users)
                    st.markdown(f'**{pct_users}%**')
                    st.caption(f'{num_users}')

                with stage4:
                    st.caption(":orange[Paso 4]")
                    st.caption("**Compra finalizada**")
                    num_users = int(source_data[source_data["PAGE_PATH"] == "Pago"]["PAGEVIEWS"].values[0] if len(
                        source_data[source_data["PAGE_PATH"] == "Pago"]) > 0 else 0)
                    pct_users = "%.1f" % (100 * num_users / total_users)
                    st.markdown(f'**{pct_users}%**')
                    st.caption(f'{num_users}')
