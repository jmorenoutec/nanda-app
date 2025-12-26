import flet as ft
from supabase import create_client, Client
from datetime import datetime, date

# --- 1. TUS CREDENCIALES ---
url = "https://waxnaegqsaxmjfpzxobc.supabase.co"
key = "sb_publishable_V69Vt_OsGA8nDycpIH02rg_C91KLtYu"

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    print(f"⚠️ Error inicializando Supabase: {e}")

# --- COLORES ---
BRAND_COLOR = "#A2C335"
BRAND_SECONDARY = "#5E5E5E"

# --- FUNCIÓN AUXILIAR TIEMPO ---
def calcular_tiempo_texto(fecha_str):
    if not fecha_str: return "-"
    try:
        inicio = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        hoy = date.today()
        dias_totales = (hoy - inicio).days
        if dias_totales < 0: return "Futuro"
        if dias_totales < 30: return f"{dias_totales}d"
        meses = dias_totales // 30
        return f"{meses}m"
    except: return "-"

def main(page: ft.Page):
    page.title = "Nanda App"
    page.window_width = 390
    page.window_height = 844
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#F5F5F5"

    # --- VARIABLES DE VISTAS ---
    vista_finanzas = ft.Column(visible=False, expand=True)
    vista_productos = ft.Column(visible=False, expand=True)
    vista_mascotas = ft.Column(visible=False, expand=True)
    vista_impresoras = ft.Column(visible=False, expand=True)
    vista_tareas = ft.Column(visible=False, expand=True)
    vista_menu = ft.Column(visible=False, expand=True)

    # Funciones placeholder
    def dummy(): pass
    recargar_finanzas = dummy
    recargar_stock = dummy
    recargar_mascotas = dummy
    recargar_impresoras = dummy
    recargar_tareas = dummy

    # --- SISTEMA DE DIÁLOGOS DE EDICIÓN ---
    edit_id = ""
    edit_tabla = ""
    
    # Campos genéricos
    campo1 = ft.TextField(label="Campo 1")
    campo2 = ft.TextField(label="Campo 2")
    campo3 = ft.TextField(label="Campo 3")
    campo4 = ft.TextField(label="Campo 4")
    
    def cerrar_dialogo_edit(e):
        dlg_editar.open = False
        page.update()

    def guardar_edicion_generica(e):
        try:
            data = {}
            if edit_tabla == "productos":
                data = {"nombre": campo1.value, "precio_menor": float(campo2.value or 0), "precio_mayor": float(campo3.value or 0), "stock": int(campo4.value or 0)}
                supabase.table('productos').update(data).eq('id', edit_id).execute(); recargar_stock()
            elif edit_tabla == "mis_mascotas":
                data = {"apodo": campo1.value, "especie": campo2.value, "fecha_nacimiento": campo3.value}
                supabase.table('mis_mascotas').update(data).eq('id', edit_id).execute(); recargar_mascotas()
            elif edit_tabla == "concesion":
                data = {"especie": campo1.value, "cantidad": int(campo2.value or 0)}
                supabase.table('concesion').update(data).eq('id', edit_id).execute(); recargar_mascotas()
            elif edit_tabla == "crias":
                data = {"padre": campo1.value, "madre": campo2.value, "cantidad": int(campo3.value or 0), "fecha": campo4.value}
                supabase.table('crias').update(data).eq('id', edit_id).execute(); recargar_mascotas()
            elif edit_tabla == "impresoras":
                data = {"nombre": campo1.value}
                supabase.table('impresoras').update(data).eq('id', edit_id).execute(); recargar_impresoras()
            elif edit_tabla == "contabilidad": 
                data = {"descripcion": campo1.value, "monto": float(campo2.value or 0)}
                supabase.table('contabilidad').update(data).eq('id', edit_id).execute(); recargar_finanzas()

            dlg_editar.open = False
            page.show_snack_bar(ft.SnackBar(ft.Text("✅ Editado correctamente"), bgcolor="green"))
            page.update()
        except Exception as ex:
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor="red")); page.update()

    def eliminar_desde_edit(e):
        try:
            dlg_editar.open = False
            page.update()
            supabase.table(edit_tabla).delete().eq('id', edit_id).execute()
            
            if edit_tabla == "productos": recargar_stock()
            elif edit_tabla in ["mis_mascotas", "concesion", "crias"]: recargar_mascotas()
            elif edit_tabla == "impresoras": recargar_impresoras()
            elif edit_tabla == "contabilidad": recargar_finanzas()
            
            page.show_snack_bar(ft.SnackBar(ft.Text("🗑️ Elemento eliminado"), bgcolor="orange"))
            page.update()
        except: pass

    dlg_editar = ft.AlertDialog(
        title=ft.Text("Editar / Eliminar"),
        content=ft.Column([campo1, campo2, campo3, campo4], tight=True),
        actions=[
            ft.TextButton("Eliminar 🗑️", on_click=eliminar_desde_edit, style=ft.ButtonStyle(color="red")),
            ft.TextButton("Cancelar", on_click=cerrar_dialogo_edit),
            ft.ElevatedButton("Guardar", on_click=guardar_edicion_generica, bgcolor=BRAND_COLOR, color="white")
        ],
        actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # Funciones abrir editor
    def abrir_edit_producto(item):
        nonlocal edit_id, edit_tabla; edit_id = item['id']; edit_tabla = "productos"
        campo1.label = "Nombre"; campo1.value = item.get('nombre', ''); campo1.visible = True
        campo2.label = "Precio Menor"; campo2.value = str(item.get('precio_menor', 0)); campo2.visible = True
        campo3.label = "Precio Mayor"; campo3.value = str(item.get('precio_mayor', 0)); campo3.visible = True
        campo4.label = "Stock"; campo4.value = str(item.get('stock', 0)); campo4.visible = True
        page.dialog = dlg_editar; dlg_editar.open = True; page.update()

    def abrir_edit_mascota(item):
        nonlocal edit_id, edit_tabla; edit_id = item['id']; edit_tabla = "mis_mascotas"
        campo1.label = "Apodo"; campo1.value = item.get('apodo', ''); campo1.visible = True
        campo2.label = "Especie"; campo2.value = item.get('especie', ''); campo2.visible = True
        campo3.label = "Fecha (YYYY-MM-DD)"; campo3.value = item.get('fecha_nacimiento', ''); campo3.visible = True
        campo4.visible = False; page.dialog = dlg_editar; dlg_editar.open = True; page.update()

    def abrir_edit_concesion(item):
        nonlocal edit_id, edit_tabla; edit_id = item['id']; edit_tabla = "concesion"
        campo1.label = "Especie"; campo1.value = item.get('especie', ''); campo1.visible = True
        campo2.label = "Cantidad"; campo2.value = str(item.get('cantidad', 0)); campo2.visible = True
        campo3.visible = False; campo4.visible = False; page.dialog = dlg_editar; dlg_editar.open = True; page.update()

    def abrir_edit_cria(item):
        nonlocal edit_id, edit_tabla; edit_id = item['id']; edit_tabla = "crias"
        campo1.label = "Padre"; campo1.value = item.get('padre', ''); campo1.visible = True
        campo2.label = "Madre"; campo2.value = item.get('madre', ''); campo2.visible = True
        campo3.label = "Cantidad"; campo3.value = str(item.get('cantidad', 0)); campo3.visible = True
        campo4.label = "Fecha"; campo4.value = item.get('fecha', ''); campo4.visible = True
        page.dialog = dlg_editar; dlg_editar.open = True; page.update()

    def abrir_edit_impresora(item):
        nonlocal edit_id, edit_tabla; edit_id = item['id']; edit_tabla = "impresoras"
        campo1.label = "Nombre"; campo1.value = item.get('nombre', ''); campo1.visible = True
        campo2.visible = False; campo3.visible = False; campo4.visible = False
        page.dialog = dlg_editar; dlg_editar.open = True; page.update()

    def abrir_edit_finanza(item):
        nonlocal edit_id, edit_tabla; edit_id = item['id']; edit_tabla = "contabilidad"
        campo1.label = "Descripción"; campo1.value = item.get('descripcion', ''); campo1.visible = True
        campo2.label = "Monto"; campo2.value = str(item.get('monto', 0)); campo2.visible = True
        campo3.visible = False; campo4.visible = False
        page.dialog = dlg_editar; dlg_editar.open = True; page.update()

    # --- NAVEGACIÓN ---
    def navegar(destino):
        nonlocal vista_finanzas, vista_productos, vista_mascotas, vista_impresoras, vista_tareas, vista_menu
        vista_finanzas.visible = False; vista_productos.visible = False; vista_mascotas.visible = False
        vista_impresoras.visible = False; vista_tareas.visible = False; vista_menu.visible = False

        if destino == "Finanzas": vista_finanzas.visible = True; recargar_finanzas()
        elif destino == "Stock": vista_productos.visible = True; recargar_stock()
        elif destino == "Mascotas": vista_mascotas.visible = True; recargar_mascotas()
        elif destino == "3D": vista_impresoras.visible = True; recargar_impresoras()
        elif destino == "Tareas": vista_tareas.visible = True; recargar_tareas()
        page.update()

    def abrir_menu(e):
        vista_finanzas.visible = False; vista_productos.visible = False; vista_mascotas.visible = False
        vista_impresoras.visible = False; vista_tareas.visible = False; vista_menu.visible = True
        page.update()

    def crear_header(titulo):
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor="white",
            shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.with_opacity(0.1, "black")),
            content=ft.Row([
                ft.Row([ft.Image(src="/logo.png", width=35, height=35, fit=ft.ImageFit.CONTAIN), ft.Text(titulo, size=20, weight="bold", color=BRAND_COLOR)], spacing=10),
                ft.IconButton(ft.icons.MENU, icon_color=BRAND_SECONDARY, icon_size=28, on_click=abrir_menu)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

    # --- DIÁLOGOS EXTRA ---
    ajuste_id_stock = ""; ajuste_val_stock = 0; txt_ajuste = ft.TextField(label="Cant", keyboard_type=ft.KeyboardType.NUMBER, autofocus=True)
    dlg_ajuste_rapido = ft.AlertDialog(title=ft.Text("Ajuste Rápido Stock"), content=txt_ajuste, actions=[
        ft.Row([ft.ElevatedButton("-", bgcolor="#E57373", color="white", on_click=lambda e: exec_ajuste(-1)), ft.ElevatedButton("+", bgcolor=BRAND_COLOR, color="white", on_click=lambda e: exec_ajuste(1))])
    ])
    def exec_ajuste(factor):
        try: 
            cant = int(txt_ajuste.value) * factor; nuevo = ajuste_val_stock + cant
            supabase.table('productos').update({'stock': nuevo}).eq('id', ajuste_id_stock).execute()
            dlg_ajuste_rapido.open=False; page.update(); recargar_stock()
        except: pass
    def abrir_ajuste_stock(id_p, s_p): nonlocal ajuste_id_stock, ajuste_val_stock; ajuste_id_stock=id_p; ajuste_val_stock=s_p; txt_ajuste.value=""; page.dialog=dlg_ajuste_rapido; dlg_ajuste_rapido.open=True; page.update()

    # --- HISTORIALES (CON CARGA RÁPIDA) ---
    dlg_hist_masc = ft.AlertDialog(title=ft.Text("Cargando...")); txt_nota_masc = ft.TextField(label="Nota", expand=True); list_logs_masc = ft.Column(scroll="AUTO", height=200); masc_sel_apodo = ""
    def guardar_log_masc(e):
        if not txt_nota_masc.value: return
        try: supabase.table('bitacora').insert({"apodo": masc_sel_apodo, "actividad": txt_nota_masc.value}).execute(); txt_nota_masc.value=""; cargar_logs_masc_data(masc_sel_apodo)
        except: pass
    def abrir_historial_mascota(apodo):
        nonlocal masc_sel_apodo; masc_sel_apodo = apodo; list_logs_masc.controls.clear(); list_logs_masc.controls.append(ft.ProgressBar(width=100, color=BRAND_COLOR))
        dlg_hist_masc.title.value = f"Bitácora: {apodo}"
        dlg_hist_masc.content = ft.Column([ft.Row([txt_nota_masc, ft.IconButton(ft.icons.SEND, icon_color=BRAND_COLOR, on_click=guardar_log_masc)]), ft.Divider(), list_logs_masc], height=300)
        page.dialog = dlg_hist_masc; dlg_hist_masc.open = True; page.update(); cargar_logs_masc_data(apodo)
    def cargar_logs_masc_data(apodo):
        list_logs_masc.controls.clear()
        try:
            res = supabase.table('bitacora').select("*").eq('apodo', apodo).order('created_at', desc=True).execute()
            if not res.data: list_logs_masc.controls.append(ft.Text("Sin historial.", italic=True))
            for log in res.data: list_logs_masc.controls.append(ft.Container(padding=10, bgcolor="white", border_radius=5, content=ft.Column([ft.Text(log['created_at'][:10], size=10, color="grey"), ft.Text(log['actividad'])])))
        except: pass
        page.update()

    dlg_hist_imp = ft.AlertDialog(title=ft.Text("Cargando...")); txt_nota_imp = ft.TextField(label="Servicio", expand=True); list_logs_imp = ft.Column(scroll="AUTO", height=200); imp_sel_nom = ""
    def guardar_log_imp(e):
        if not txt_nota_imp.value: return
        try: supabase.table('mantenimiento_imp').insert({"impresora": imp_sel_nom, "detalle": txt_nota_imp.value}).execute(); txt_nota_imp.value=""; cargar_logs_imp_data(imp_sel_nom)
        except: pass
    def abrir_historial_imp(nom):
        nonlocal imp_sel_nom; imp_sel_nom = nom; list_logs_imp.controls.clear(); list_logs_imp.controls.append(ft.ProgressBar(width=100, color=BRAND_COLOR))
        dlg_hist_imp.title.value = f"Mantenimiento: {nom}"
        dlg_hist_imp.content = ft.Column([ft.Row([txt_nota_imp, ft.IconButton(ft.icons.BUILD, icon_color=BRAND_COLOR, on_click=guardar_log_imp)]), ft.Divider(), list_logs_imp], height=300)
        page.dialog = dlg_hist_imp; dlg_hist_imp.open = True; page.update(); cargar_logs_imp_data(nom)
    def cargar_logs_imp_data(nom):
        list_logs_imp.controls.clear()
        try:
            res = supabase.table('mantenimiento_imp').select("*").eq('impresora', nom).order('created_at', desc=True).execute()
            if not res.data: list_logs_imp.controls.append(ft.Text("Sin mantenimientos.", italic=True))
            for log in res.data: list_logs_imp.controls.append(ft.Container(padding=10, bgcolor="white", border_radius=5, content=ft.Column([ft.Text(log['created_at'][:10], size=10, color="grey"), ft.Text(log['detalle'])])))
        except: pass
        page.update()

    # ==============================================================================
    # 1. FINANZAS
    # ==============================================================================
    txt_monto = ft.TextField(label="Monto", keyboard_type=ft.KeyboardType.NUMBER, prefix_text="$ ")
    txt_desc = ft.TextField(label="Descripción")
    lista_finanzas = ft.ListView(expand=True, spacing=10, padding=20)

    def cargar_finanzas():
        try:
            res = supabase.table('contabilidad').select("*").order('created_at', desc=True).execute()
            lista_finanzas.controls.clear()
            for i in res.data:
                col = "green" if i['tipo']=="Venta" else "red"
                icon = ft.icons.ARROW_UPWARD if i['tipo']=="Venta" else ft.icons.ARROW_DOWNWARD
                card = ft.Container(
                    padding=15, bgcolor="white", border_radius=10, ink=True,
                    on_long_press=lambda e, item=i: abrir_edit_finanza(item),
                    content=ft.Row([
                        ft.Row([ft.Icon(icon, color=col), ft.Column([ft.Text(i.get('descripcion','-'), weight="bold"), ft.Text(i['created_at'][:10], size=10, color="grey")])]),
                        ft.Text(f"${i.get('monto',0)}", size=16, weight="bold", color=col)
                    ], alignment="spaceBetween")
                )
                lista_finanzas.controls.append(card)
            page.update()
        except: pass
    recargar_finanzas = cargar_finanzas

    def guardar_finanza(tipo):
        if not txt_monto.value: return
        try: supabase.table('contabilidad').insert({"descripcion": txt_desc.value, "monto": float(txt_monto.value), "tipo": tipo}).execute(); txt_monto.value=""; txt_desc.value=""; recargar_finanzas()
        except: pass

    vista_finanzas.controls = [crear_header("Finanzas"), ft.Container(padding=20, bgcolor="white", content=ft.Column([txt_desc, txt_monto, ft.Row([ft.ElevatedButton("Ingreso", bgcolor=BRAND_COLOR, color="white", expand=True, on_click=lambda e: guardar_finanza("Venta")), ft.Container(width=10), ft.ElevatedButton("Gasto", bgcolor="#E57373", color="white", expand=True, on_click=lambda e: guardar_finanza("Gasto"))])])), ft.Container(expand=True, content=lista_finanzas)]

    # ==============================================================================
    # 2. STOCK
    # ==============================================================================
    txt_p_nom = ft.TextField(label="Producto")
    txt_p_menor = ft.TextField(label="$ Menor", width=160, keyboard_type=ft.KeyboardType.NUMBER)
    txt_p_mayor = ft.TextField(label="$ Mayor", width=160, keyboard_type=ft.KeyboardType.NUMBER)
    txt_p_stock = ft.TextField(label="Stock", keyboard_type=ft.KeyboardType.NUMBER)
    lista_productos = ft.ListView(expand=True, spacing=10, padding=20)

    def cargar_stock():
        try:
            res = supabase.table('productos').select("*").order('nombre').execute()
            lista_productos.controls.clear()
            for p in res.data:
                pm = p.get('precio_menor', 0); pM = p.get('precio_mayor', 0); stk = p.get('stock', 0)
                # Stock sigue igual (Click Card -> Ajustar, Long Press -> Editar)
                card = ft.Container(
                    padding=15, bgcolor="white", border_radius=12, ink=True,
                    shadow=ft.BoxShadow(blur_radius=2, color=ft.colors.with_opacity(0.05, "black")),
                    on_click=lambda e, i=p['id'], s=stk: abrir_ajuste_stock(i,s), 
                    on_long_press=lambda e, item=p: abrir_edit_producto(item),
                    content=ft.Row([
                        ft.Column([ft.Text(p.get('nombre', 'Sin Nombre'), weight="bold"), ft.Row([ft.Text(f"${pm}", color="green"), ft.Text(f"M:${pM}", color="blue", size=12)])]),
                        ft.Column([ft.Text(f"Stk: {stk}", weight="bold"), ft.Text("Tocar para ajustar", size=8, color="grey")])
                    ], alignment="spaceBetween")
                )
                lista_productos.controls.append(card)
            page.update()
        except: pass
    recargar_stock = cargar_stock

    def guardar_prod(e):
        if not txt_p_nom.value: return
        try: supabase.table('productos').insert({"nombre": txt_p_nom.value, "precio_menor": float(txt_p_menor.value or 0), "precio_mayor": float(txt_p_mayor.value or 0), "stock": int(txt_p_stock.value or 0)}).execute(); txt_p_nom.value=""; txt_p_stock.value=""; recargar_stock()
        except: pass

    vista_productos.controls = [crear_header("Inventario"), ft.Container(padding=20, bgcolor="white", content=ft.Column([txt_p_nom, ft.Row([txt_p_menor, txt_p_mayor], alignment="spaceBetween"), txt_p_stock, ft.Container(height=5), ft.ElevatedButton("Guardar", bgcolor=BRAND_COLOR, color="white", width=400, on_click=guardar_prod)])), ft.Container(expand=True, content=lista_productos)]

    # ==============================================================================
    # 3. MASCOTAS
    # ==============================================================================
    txt_ma_apodo = ft.TextField(label="Apodo")
    txt_ma_esp = ft.TextField(label="Especie")
    txt_ma_nac = ft.TextField(label="Fecha (YYYY-MM-DD)", hint_text="2023-01-01")
    lista_mis_masc = ft.ListView(expand=True, spacing=10, padding=10)

    def cargar_mis_animales():
        try:
            res = supabase.table('mis_mascotas').select("*").execute()
            lista_mis_masc.controls.clear()
            for a in res.data:
                tiempo = calcular_tiempo_texto(a.get('fecha_nacimiento'))
                
                # BOTÓN DEDICADO PARA HISTORIAL
                btn_historial = ft.IconButton(
                    icon=ft.icons.HISTORY, 
                    icon_color="grey", 
                    icon_size=30,
                    on_click=lambda e, nom=a.get('apodo',''): abrir_historial_mascota(nom) # ESTE ES EL CLICK SIMPLE
                )

                card = ft.Container(
                    padding=15, bgcolor="white", border_radius=12, ink=True,
                    on_long_press=lambda e, item=a: abrir_edit_mascota(item), # ESTE ES EL CLICK LARGO
                    content=ft.Row([
                        ft.Row([ft.Icon(ft.icons.PETS, color=BRAND_COLOR), ft.Column([ft.Text(a.get('apodo','-'), weight="bold"), ft.Text(f"{a.get('especie','-')} • {tiempo}", size=12, color="grey")])]),
                        btn_historial
                    ], alignment="spaceBetween")
                )
                lista_mis_masc.controls.append(card)
        except: pass

    def add_mi_animal(e):
        if not txt_ma_apodo.value: return
        supabase.table('mis_mascotas').insert({"apodo": txt_ma_apodo.value, "especie": txt_ma_esp.value, "fecha_nacimiento": txt_ma_nac.value}).execute(); txt_ma_apodo.value=""; recargar_mascotas()

    # CONCESION
    txt_conc_esp = ft.TextField(label="Especie"); txt_conc_cant = ft.TextField(label="Cantidad", keyboard_type=ft.KeyboardType.NUMBER)
    lista_concesion = ft.ListView(expand=True, spacing=10, padding=10)
    def cargar_concesion():
        try:
            res = supabase.table('concesion').select("*").execute()
            lista_concesion.controls.clear()
            for c in res.data:
                card = ft.Container(
                    padding=15, bgcolor="white", border_radius=12, ink=True,
                    on_long_press=lambda e, item=c: abrir_edit_concesion(item),
                    content=ft.Row([
                        ft.Text(c.get('especie','-'), weight="bold"), 
                        ft.Container(padding=5, bgcolor="#FFF3E0", border_radius=5, content=ft.Text(f"Cant: {c.get('cantidad',0)}", color="orange", weight="bold"))
                    ], alignment="spaceBetween")
                )
                lista_concesion.controls.append(card)
        except: pass
    def add_concesion(e):
        if not txt_conc_esp.value: return
        supabase.table('concesion').insert({"especie": txt_conc_esp.value, "cantidad": int(txt_conc_cant.value or 0)}).execute(); txt_conc_esp.value=""; txt_conc_cant.value=""; recargar_mascotas()

    # CRIAS
    txt_cria_padre = ft.TextField(label="Padre", expand=True); txt_cria_madre = ft.TextField(label="Madre", expand=True); txt_cria_cant = ft.TextField(label="Cant", width=80); txt_cria_fecha = ft.TextField(label="Fecha", expand=True)
    lista_crias = ft.ListView(expand=True, spacing=10, padding=10)
    def cargar_crias():
        try:
            res = supabase.table('crias').select("*").execute()
            lista_crias.controls.clear()
            for c in res.data:
                tiempo = calcular_tiempo_texto(c.get('fecha'))
                card = ft.Container(
                    padding=15, bgcolor="white", border_radius=12, ink=True,
                    on_long_press=lambda e, item=c: abrir_edit_cria(item),
                    content=ft.Row([
                        ft.Column([ft.Text(f"{c.get('padre','?')} x {c.get('madre','?')}", weight="bold", size=14), ft.Text(f"Tiempo: {tiempo}", color="green", size=12)]),
                        ft.Text(f"#{c.get('cantidad',0)}", weight="bold", size=16)
                    ], alignment="spaceBetween")
                )
                lista_crias.controls.append(card)
        except: pass
    def add_cria(e):
        if not txt_cria_padre.value: return
        supabase.table('crias').insert({"padre": txt_cria_padre.value, "madre": txt_cria_madre.value, "cantidad": int(txt_cria_cant.value or 0), "fecha": txt_cria_fecha.value}).execute(); txt_cria_padre.value=""; recargar_mascotas()

    def recargar_mascotas_logica():
        try: cargar_mis_animales(); cargar_concesion(); cargar_crias(); page.update()
        except: pass
    recargar_mascotas = recargar_mascotas_logica

    tabs_masc = ft.Tabs(selected_index=0, animation_duration=300, expand=True, tabs=[
        ft.Tab(text="Mis Animales", content=ft.Container(expand=True, content=ft.Column([ft.Container(padding=20, bgcolor="white", content=ft.Column([txt_ma_apodo, txt_ma_esp, txt_ma_nac, ft.ElevatedButton("Agregar Mascota", bgcolor=BRAND_COLOR, color="white", width=400, on_click=add_mi_animal)])), ft.Container(expand=True, content=lista_mis_masc)]))),
        ft.Tab(text="Concesión", content=ft.Container(expand=True, content=ft.Column([ft.Container(padding=20, bgcolor="white", content=ft.Column([txt_conc_esp, txt_conc_cant, ft.ElevatedButton("Agregar Stock Venta", bgcolor="orange", color="white", width=400, on_click=add_concesion)])), ft.Container(expand=True, content=lista_concesion)]))),
        ft.Tab(text="Crías", content=ft.Container(expand=True, content=ft.Column([ft.Container(padding=20, bgcolor="white", content=ft.Column([ft.Row([txt_cria_padre, txt_cria_madre]), ft.Row([txt_cria_cant, txt_cria_fecha]), ft.ElevatedButton("Registrar Cruce", bgcolor="purple", color="white", width=400, on_click=add_cria)])), ft.Container(expand=True, content=lista_crias)])))
    ])
    vista_mascotas.controls = [crear_header("Mascotas"), ft.Container(expand=True, content=tabs_masc)]

    # ==============================================================================
    # 4. IMPRESORAS
    # ==============================================================================
    txt_imp_nom = ft.TextField(label="Nombre Impresora")
    lista_impresoras = ft.ListView(expand=True, spacing=10, padding=20)
    def cargar_impresoras():
        try:
            res = supabase.table('impresoras').select("*").execute()
            lista_impresoras.controls.clear()
            for imp in res.data:
                # BOTÓN DEDICADO PARA MANTENIMIENTO
                btn_mant = ft.IconButton(
                    icon=ft.icons.BUILD_CIRCLE, 
                    icon_color="grey", 
                    icon_size=30,
                    on_click=lambda e, nom=imp.get('nombre','-'): abrir_historial_imp(nom) # CLICK SIMPLE
                )

                card = ft.Container(
                    padding=15, bgcolor="white", border_radius=12, ink=True,
                    on_long_press=lambda e, item=imp: abrir_edit_impresora(item), # CLICK LARGO
                    content=ft.Row([
                        ft.Row([ft.Icon(ft.icons.PRINT, color="blue"), ft.Text(imp.get('nombre','-'), weight="bold", size=16)]),
                        btn_mant
                    ], alignment="spaceBetween")
                )
                lista_impresoras.controls.append(card)
            page.update()
        except: pass
    recargar_impresoras = cargar_impresoras
    def add_impresora(e):
        if not txt_imp_nom.value: return
        supabase.table('impresoras').insert({"nombre": txt_imp_nom.value}).execute(); txt_imp_nom.value=""; recargar_impresoras()

    vista_impresoras.controls = [crear_header("Impresoras 3D"), ft.Container(padding=20, bgcolor="white", content=ft.Column([txt_imp_nom, ft.ElevatedButton("Agregar Máquina", bgcolor="blue", color="white", width=400, on_click=add_impresora)])), ft.Container(expand=True, content=lista_impresoras)]

    # ==============================================================================
    # 5. TAREAS
    # ==============================================================================
    txt_tarea = ft.TextField(label="Nueva Tarea")
    lista_tareas = ft.ListView(expand=True, spacing=10, padding=20)
    def cargar_tareas():
        try:
            res = supabase.table('tareas').select("*").order('id', desc=True).execute(); lista_tareas.controls.clear()
            for t in res.data:
                lista_tareas.controls.append(ft.Container(padding=15, bgcolor="white", border_radius=10, content=ft.Row([
                    ft.Text(t['descripcion'], size=16, expand=True),
                    ft.IconButton(ft.icons.CHECK_CIRCLE, icon_color=BRAND_COLOR, data=t['id'], on_click=lambda e: del_tarea(e.control.data))
                ])))
            page.update()
        except: pass
    recargar_tareas = cargar_tareas
    def del_tarea(uid): supabase.table('tareas').delete().eq('id', uid).execute(); recargar_tareas()
    def add_tarea(e): 
        if txt_tarea.value: supabase.table('tareas').insert({"descripcion": txt_tarea.value}).execute(); txt_tarea.value=""; recargar_tareas()

    vista_tareas.controls = [crear_header("Tareas"), ft.Container(padding=20, bgcolor="white", content=ft.Column([txt_tarea, ft.ElevatedButton("Agregar Tarea", bgcolor=BRAND_SECONDARY, color="white", width=400, on_click=add_tarea)])), ft.Container(expand=True, content=lista_tareas)]

    # ==============================================================================
    # MENÚ
    # ==============================================================================
    def item_menu(texto, icono, destino): return ft.Container(padding=20, bgcolor="white", border_radius=15, margin=ft.margin.only(bottom=10), on_click=lambda _: navegar(destino), content=ft.Row([ft.Row([ft.Icon(icono, color=BRAND_COLOR), ft.Text(texto, size=18, weight="bold")], spacing=15), ft.Icon(ft.icons.CHEVRON_RIGHT, color="grey")], alignment="spaceBetween"))
    vista_menu.controls = [ft.Container(padding=30, content=ft.Column([ft.Row([ft.Text("MENÚ", size=28, weight="bold", color=BRAND_COLOR), ft.IconButton(ft.icons.CLOSE, icon_size=30, on_click=lambda _: navegar("Finanzas"))], alignment="spaceBetween"), ft.Divider(height=20, color="transparent"), item_menu("Finanzas", ft.icons.MONETIZATION_ON, "Finanzas"), item_menu("Inventario", ft.icons.INVENTORY, "Stock"), item_menu("Mascotas", ft.icons.PETS, "Mascotas"), item_menu("Impresoras 3D", ft.icons.PRINT, "3D"), item_menu("Tareas", ft.icons.CHECKLIST, "Tareas")]))]

    page.add(ft.Container(expand=True, content=ft.Stack([vista_finanzas, vista_productos, vista_mascotas, vista_impresoras, vista_tareas, vista_menu])))
    navegar("Finanzas")

ft.app(target=main, assets_dir="assets")