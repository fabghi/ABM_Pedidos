import sqlite3
import pandas as pd
import streamlit as st


DB_PATH = r"\\ardp.local\Resources\Files\User\AUDITORI\Parametros_ST\BD\AP_Contable.db"

# Función genérica para ejecutar consultas SQL
def ejecutar_consulta(query, params=(), fetch=False):
    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute(query, params)
        if fetch:
            data = cursor.fetchall()
            conexion.close()
            return data
        conexion.commit()
        conexion.close()
    except sqlite3.Error as e:
        st.error(f"Error en la base de datos: {e}")
        return None

# Función para agregar un pedido

def agregar_pedido(c_costo, solicitante):
    if ejecutar_consulta("SELECT 1 FROM Pedidos WHERE C_Costo = ?", (c_costo,), fetch=True):
        st.error("Ya existe un pedido para este centro de costo.")
        return

    ejecutar_consulta('''
        INSERT INTO Pedidos (C_Costo, Solicitante)
        VALUES (?, ?)
    ''', (c_costo, solicitante))
    st.success(f"Pedido agregado correctamente con Centro de Costo: {c_costo}")

# Función para listar pedidos
def listar_pedidos():
    conexion = sqlite3.connect(DB_PATH)
    query = """
        SELECT P.C_Costo, A.APELLIDO || ', ' || A.Nombres || ' (ID: ' || A.User_ID || ')' AS Solicitante 
        FROM Pedidos P 
        JOIN Auditores A ON P.Solicitante = A.User_ID
        ORDER BY P.C_Costo
    """
    df = pd.read_sql_query(query, conexion)
    conexion.close()
    return df

# Función para eliminar pedidos seleccionados
def eliminar_pedidos(c_costos):
    placeholders = ', '.join(['?'] * len(c_costos))
    query = f'DELETE FROM Pedidos WHERE C_Costo IN ({placeholders})'
    ejecutar_consulta(query, c_costos)
    st.success("Pedidos eliminados correctamente.")

# Función para obtener la lista de pedidos a eliminar
def obtener_pedidos():
    query = "SELECT C_Costo FROM Pedidos"
    return [row[0] for row in ejecutar_consulta(query, fetch=True)]

# Función para obtener centros de costo ordenados alfabéticamente
def obtener_centros_de_costo():
    query = "SELECT C_Costo, Nombre_C_Costo FROM C_Costos ORDER BY Nombre_C_Costo"
    return {f"{c_costo} - {nombre}": c_costo for c_costo, nombre in ejecutar_consulta(query, fetch=True)}

# Función para obtener la lista de auditores con User_ID, APELLIDO y Nombres ordenados alfabéticamente
def obtener_auditores():
    query = "SELECT User_ID, APELLIDO, Nombres FROM Auditores ORDER BY APELLIDO, Nombres"
    auditores = ejecutar_consulta(query, fetch=True)
    
    if auditores:
        # Formateamos cada registro para mostrar APELLIDO y Nombres, pero guardamos User_ID
        auditores_dict = {f"{apellido}, {nombre} (ID: {user_id})": user_id for user_id, apellido, nombre in auditores}
        return auditores_dict
    else:
        return {}

# Interfaz de usuario con Streamlit
st.title("Gestión de Pedidos - Controles Contables")


#st.markdown("<h1 style='text-align: center; color: #1f77b4;'>Gestión de Pedidos</h1>", unsafe_allow_html=True)
#st.markdown("<p style='font-size:20px;'>Seleccione una opción en el menú lateral para comenzar.</p>", unsafe_allow_html=True)



menu = st.sidebar.selectbox("Menú", ["Inicio", "Agregar Pedido", "Listar Pedidos", "Eliminar Pedido"])

if menu == "Inicio":
    st.header("Bienvenido a la aplicación de gestión de pedidos")
    st.write("Seleccione una opción en el menú lateral para comenzar.")

elif menu == "Agregar Pedido":
    st.header("Agregar un nuevo pedido")

    # Obtener la lista de centros de costo ordenados y mostrarlos en un combo
    centros_de_costo = obtener_centros_de_costo()
    opciones_c_costo = ["Seleccione una opción"] + sorted(list(centros_de_costo.keys()))
    c_costo_seleccionado = st.selectbox("Centro de Costo", opciones_c_costo)
    c_costo = centros_de_costo.get(c_costo_seleccionado, None)

    # Obtener la lista de auditores ordenados y mostrarlos en un combo
    auditores = obtener_auditores()
    opciones_solicitante = ["Seleccione una opción"] + sorted(list(auditores.keys()))
    solicitante_seleccionado = st.selectbox("Solicitante", opciones_solicitante)
    solicitante = auditores.get(solicitante_seleccionado, None)

    if st.button("Agregar"):
        if c_costo and solicitante:
            agregar_pedido(c_costo, solicitante)
        else:
            st.error("Por favor, seleccione una opción válida para Centro de Costo y Solicitante.")

elif menu == "Listar Pedidos":
    st.header("Lista de Pedidos")
    pedidos = listar_pedidos()
    if not pedidos.empty:
        st.dataframe(pedidos.set_index(pedidos.columns[0]))
    else:
        st.info("No hay pedidos registrados.")

elif menu == "Eliminar Pedido":
    st.header("Eliminar pedidos")
    pedidos = obtener_pedidos()
    seleccionados = st.multiselect("Centro de Costo", ["Seleccione una opción"] + pedidos)
    
    if st.button("Eliminar"):
        eliminar_pedidos(seleccionados)
        st.session_state['centro_costo_seleccionado'] = "Seleccione una opción"
        st.rerun()
        st.session_state['centro_costo_seleccionado'] = "Seleccione una opción"
        if seleccionados:
            eliminar_pedidos(seleccionados)
        else:
            st.error("Por favor, seleccione al menos un pedido para eliminar.")







