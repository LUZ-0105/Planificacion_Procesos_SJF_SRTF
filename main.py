import customtkinter as ctk
from tkinter import ttk, messagebox, Scrollbar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# =========================
# CLASE PROCESO
# =========================
class Proceso:
    def __init__(self, nombre, llegada, ejecucion):
        self.nombre = nombre
        self.tiempo_llegada = llegada
        self.tiempo_ejecucion = ejecucion
        self.tiempo_restante = ejecucion  # Se reinicia en cada ejecución
        self.tiempo_comienzo = -1
        self.tiempo_finalizacion = 0
        self.tiempo_retorno = 0
        self.tiempo_espera = 0

# =========================
# APP PRINCIPAL
# =========================
class PlanificadorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Planificador de Procesos | SJF & SRTF")
        self.geometry("1400x850")
        self.minsize(1100, 700)
        
        self.COLORS = {
            'bg_primary': '#0f1115', 'bg_secondary': '#161922', 'bg_card': '#1c212c',
            'bg_input': '#252a36', 'accent': '#3b82f6', 'accent_hover': '#2563eb',
            'success': '#10b981', 'success_hover': '#059669', 'danger': '#ef4444',
            'text_primary': '#f3f4f6', 'text_secondary': '#9ca3af', 'border': '#2d3748'
        }
        self.configure(fg_color=self.COLORS['bg_primary'])
        self.procesos = []
        self.resultados = []
        self.campos_procesos = []
        self._crear_ui()

    # =========================
    # INTERFAZ
    # =========================
    def _crear_ui(self):
        # HEADER
        header = ctk.CTkFrame(self, fg_color=self.COLORS['bg_secondary'], corner_radius=0, height=70, border_width=1, border_color=self.COLORS['border'])
        header.pack(fill="x", side="top")
        ctk.CTkLabel(header, text="⚙️", font=ctk.CTkFont(size=28), text_color=self.COLORS['accent']).pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(header, text="SIMULADOR DE PLANIFICACIÓN", font=ctk.CTkFont(size=20, weight="bold"), text_color=self.COLORS['text_primary']).pack(side="left", pady=15)
        ctk.CTkLabel(header, text="v2.3 • Lógica Aislada & Estable", font=ctk.CTkFont(size=11), text_color=self.COLORS['text_secondary']).pack(side="left", padx=15, pady=15)

        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.main_scroll.pack(fill="both", expand=True, padx=20, pady=15)

        self._crear_config()
        self._crear_procesos()
        self._crear_ejecutar()
        self._crear_resultados()

    def _crear_config(self):
        f = ctk.CTkFrame(self.main_scroll, fg_color=self.COLORS['bg_card'], corner_radius=12, border_width=1, border_color=self.COLORS['border'])
        f.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(f, text="CONFIGURACIÓN", font=ctk.CTkFont(size=15, weight="bold"), text_color=self.COLORS['accent']).pack(anchor="w", padx=20, pady=(15, 10))
        
        c = ctk.CTkFrame(f, fg_color="transparent")
        c.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(c, text="Algoritmo:", text_color=self.COLORS['text_secondary']).grid(row=0, column=0, padx=10, sticky="w")
        self.combo_algo = ctk.CTkComboBox(c, values=["SJF (No Preemptivo)", "SRTF (Preemptivo)"], width=210, fg_color=self.COLORS['bg_input'], dropdown_fg_color=self.COLORS['bg_secondary'])
        self.combo_algo.set("SJF (No Preemptivo)")
        self.combo_algo.grid(row=0, column=1, padx=10, sticky="w")

        ctk.CTkLabel(c, text="Procesos (1-10):", text_color=self.COLORS['text_secondary']).grid(row=0, column=2, padx=10, sticky="w")
        self.entry_cant = ctk.CTkEntry(c, width=80, fg_color=self.COLORS['bg_input'], border_color=self.COLORS['border'])
        self.entry_cant.insert(0, "3")
        self.entry_cant.grid(row=0, column=3, padx=10, sticky="w")

        ctk.CTkButton(c, text="Generar Campos", command=self._generar, height=35, fg_color=self.COLORS['accent'], hover_color=self.COLORS['accent_hover'], font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=10, sticky="w")
        ctk.CTkButton(c, text="Limpiar", command=self._limpiar, height=35, fg_color=self.COLORS['danger'], hover_color="#dc2626", font=ctk.CTkFont(weight="bold")).grid(row=0, column=5, padx=10, sticky="w")

    def _crear_procesos(self):
        f = ctk.CTkFrame(self.main_scroll, fg_color=self.COLORS['bg_card'], corner_radius=12, border_width=1, border_color=self.COLORS['border'])
        f.pack(fill="both", expand=False, pady=(0, 15))
        ctk.CTkLabel(f, text=" ENTRADA DE PROCESOS", font=ctk.CTkFont(size=15, weight="bold"), text_color=self.COLORS['accent']).pack(anchor="w", padx=20, pady=(15, 10))
        self.frame_proc = ctk.CTkScrollableFrame(f, fg_color="transparent", height=220)
        self.frame_proc.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.msg_proc = ctk.CTkLabel(self.frame_proc, text="Haz clic en 'Generar Campos' para agregar procesos...", text_color=self.COLORS['text_secondary'], font=ctk.CTkFont(size=14))
        self.msg_proc.pack(expand=True)

    def _crear_ejecutar(self):
        self.btn_run = ctk.CTkButton(self.main_scroll, text="▶ EJECUTAR PLANIFICACIÓN", command=self._ejecutar, height=45, font=ctk.CTkFont(size=15, weight="bold"), fg_color=self.COLORS['success'], hover_color=self.COLORS['success_hover'], corner_radius=10)
        self.btn_run.pack(fill="x", pady=15, padx=40)

    def _crear_resultados(self):
        f = ctk.CTkFrame(self.main_scroll, fg_color=self.COLORS['bg_card'], corner_radius=12, border_width=1, border_color=self.COLORS['border'])
        f.pack(fill="both", expand=True, pady=(0, 20))
        
        top = ctk.CTkFrame(f, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(top, text="📊 RESULTADOS Y DIAGRAMA", font=ctk.CTkFont(size=15, weight="bold"), text_color=self.COLORS['accent']).pack(side="left")
        self.lbl_algoritmo = ctk.CTkLabel(top, text="", font=ctk.CTkFont(size=13, weight="bold"), text_color="#10b981")
        self.lbl_algoritmo.pack(side="right", padx=20)

        self.res_container = ctk.CTkFrame(f, fg_color="transparent")
        self.res_container.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self._crear_tabla()

        ctk.CTkLabel(self.res_container, text="📈 Diagrama de Gantt", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.COLORS['text_secondary']).pack(anchor="w", pady=(15, 5), padx=10)
        self.canvas_frame = ctk.CTkFrame(self.res_container, fg_color=self.COLORS['bg_secondary'], corner_radius=8, border_width=1, border_color=self.COLORS['border'])
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _crear_tabla(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=self.COLORS['bg_secondary'], fieldbackground=self.COLORS['bg_secondary'], foreground=self.COLORS['text_primary'], rowheight=28, font=("Segoe UI", 11), bordercolor=self.COLORS['border'], borderwidth=1)
        style.configure("Treeview.Heading", background=self.COLORS['accent'], foreground="white", font=("Segoe UI", 12, "bold"), relief="flat", padding=5)
        style.map("Treeview.Heading", background=[('active', self.COLORS['accent_hover'])])

        tf = ctk.CTkFrame(self.res_container, fg_color="transparent")
        tf.pack(fill="x", padx=10, pady=(10, 15))
        self.tabla = ttk.Treeview(tf, columns=("Proceso", "Llegada", "Ejecución", "Comienzo", "Finalización", "Retorno", "Espera"), show="headings", height=6, style="Treeview")
        cols = [("Proceso", 80), ("Llegada", 80), ("Ejecución", 90), ("Comienzo", 90), ("Finalización", 100), ("Retorno", 90), ("Espera", 90)]
        for c, w in cols:
            self.tabla.heading(c, text=c)
            self.tabla.column(c, width=w, anchor="center")
        vsb = Scrollbar(tf, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=vsb.set)
        self.tabla.pack(side="left", fill="x", expand=True)
        vsb.pack(side="right", fill="y")

    # =========================
    # LÓGICA DE INTERFAZ
    # =========================
    def _generar(self):
        for w in self.frame_proc.winfo_children(): w.destroy()
        try:
            cant = int(self.entry_cant.get())
            if not (1 <= cant <= 10): raise ValueError
        except ValueError:
            return messagebox.showerror("Error", "Ingresa entre 1 y 10.")
        self._dibujar_filas(cant, llegada_def=[0,1,3,4,6], ejec_def=[6,4,2,3,5])

    def _dibujar_filas(self, cant, llegada_def, ejec_def):
        self.campos_procesos = []
        colores = ['#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1']
        for i in range(cant):
            row = ctk.CTkFrame(self.frame_proc, fg_color=self.COLORS['bg_secondary'], corner_radius=10, border_width=1, border_color=self.COLORS['border'])
            row.pack(fill="x", pady=5)
            n = chr(65 + i)
            ctk.CTkLabel(row, text=f"P{n}", width=50, fg_color=colores[i], corner_radius=8, font=ctk.CTkFont(size=12, weight="bold"), text_color="white").grid(row=0, column=0, padx=15, pady=8)
            ctk.CTkLabel(row, text="Llegada:", text_color=self.COLORS['text_secondary']).grid(row=0, column=1, padx=(15, 5))
            e_l = ctk.CTkEntry(row, width=70, fg_color=self.COLORS['bg_input'], border_color=self.COLORS['border'])
            e_l.grid(row=0, column=2, padx=5)
            e_l.insert(0, str(llegada_def[i % len(llegada_def)]))
            ctk.CTkLabel(row, text="Ejecución:", text_color=self.COLORS['text_secondary']).grid(row=0, column=3, padx=(20, 5))
            e_e = ctk.CTkEntry(row, width=70, fg_color=self.COLORS['bg_input'], border_color=self.COLORS['border'])
            e_e.grid(row=0, column=4, padx=5)
            e_e.insert(0, str(ejec_def[i % len(ejec_def)]))
            self.campos_procesos.append({"nombre": n, "llegada": e_l, "ejecucion": e_e})

    def _limpiar(self):
        for w in self.frame_proc.winfo_children(): w.destroy()
        for i in self.tabla.get_children(): self.tabla.delete(i)
        for w in self.canvas_frame.winfo_children(): w.destroy()
        self.campos_procesos = []
        self.msg_proc = ctk.CTkLabel(self.frame_proc, text="Haz clic en 'Generar Campos' para agregar procesos...", text_color=self.COLORS['text_secondary'], font=ctk.CTkFont(size=14))
        self.msg_proc.pack(expand=True)
        self.lbl_algoritmo.configure(text="")

    # =========================
    # EJECUCIÓN (BLINDADA)
    # =========================
    def _ejecutar(self):
        if not self.campos_procesos:
            return messagebox.showwarning("Advertencia", "Primero genera los campos de los procesos.")
        
        # 1. Extraer datos crudos
        raw = []
        try:
            for c in self.campos_procesos:
                l, e = int(c["llegada"].get()), int(c["ejecucion"].get())
                if e <= 0 or l < 0: raise ValueError
                raw.append((c["nombre"], l, e))
        except ValueError:
            return messagebox.showerror("Error", "Valores inválidos. Llegada ≥ 0, Ejecución > 0.")

        # 2. Determinar algoritmo EXPLÍCITAMENTE
        sel = self.combo_algo.get().strip()
        es_srtf = "SRTF" in sel
        self.lbl_algoritmo.configure(text=f"▶ Ejecutando: {sel}", text_color="#10b981")

        # 3. Crear objetos NUEVOS (evita contaminación de estado)
        self.procesos = [Proceso(n, l, e) for n, l, e in raw]
        self.procesos.sort(key=lambda x: x.tiempo_llegada)

        # 4. Ejecutar
        if es_srtf:
            self._run_srtf()
        else:
            self._run_sjf()

        # 5. Calcular y mostrar
        self._calcular_metricas()
        self._mostrar_tabla()
        self._mostrar_gantt()

    # =========================
    # ALGORITMOS PURAS
    # =========================
    def _run_sjf(self):
        t, comp, n = 0, 0, len(self.procesos)
        term = [False]*n
        self.resultados = []
        while comp < n:
            idx, min_b = -1, float('inf')
            for i in range(n):
                if not term[i] and self.procesos[i].tiempo_llegada <= t and self.procesos[i].tiempo_ejecucion < min_b:
                    min_b = self.procesos[i].tiempo_ejecucion
                    idx = i
            if idx != -1:
                p = self.procesos[idx]
                p.tiempo_comienzo = t
                t += p.tiempo_ejecucion
                p.tiempo_finalizacion = t
                term[idx] = True
                comp += 1
                self.resultados.append({"proceso": p.nombre, "inicio": p.tiempo_comienzo, "fin": p.tiempo_finalizacion})
            else:
                t += 1

    def _run_srtf(self):
        t, comp, n = 0, 0, len(self.procesos)
        term = [False]*n
        self.resultados = []
        ultimo, inicio_seg = None, 0
        max_t = sum(p.tiempo_ejecucion for p in self.procesos) + max(p.tiempo_llegada for p in self.procesos) + 10
        
        while comp < n and t <= max_t:
            idx, min_r = -1, float('inf')
            for i in range(n):
                if not term[i] and self.procesos[i].tiempo_llegada <= t and self.procesos[i].tiempo_restante < min_r:
                    min_r = self.procesos[i].tiempo_restante
                    idx = i
            if idx != -1:
                p = self.procesos[idx]
                if ultimo != idx:
                    if ultimo is not None:
                        self.resultados.append({"proceso": self.procesos[ultimo].nombre, "inicio": inicio_seg, "fin": t})
                    if p.tiempo_comienzo == -1:
                        p.tiempo_comienzo = t
                    inicio_seg = t
                    ultimo = idx
                p.tiempo_restante -= 1
                t += 1
                if p.tiempo_restante == 0:
                    p.tiempo_finalizacion = t
                    term[idx] = True
                    comp += 1
                    self.resultados.append({"proceso": p.nombre, "inicio": inicio_seg, "fin": t})
                    ultimo = None
            else:
                t += 1
                ultimo = None

    def _calcular_metricas(self):
        for p in self.procesos:
            p.tiempo_retorno = p.tiempo_finalizacion - p.tiempo_llegada
            p.tiempo_espera = p.tiempo_retorno - p.tiempo_ejecucion

    # =========================
    # VISUALIZACIÓN
    # =========================
    def _mostrar_tabla(self):
        for i in self.tabla.get_children(): self.tabla.delete(i)
        for p in self.procesos:
            self.tabla.insert("", "end", values=(p.nombre, p.tiempo_llegada, p.tiempo_ejecucion, p.tiempo_comienzo, p.tiempo_finalizacion, p.tiempo_retorno, p.tiempo_espera))

    def _mostrar_gantt(self):
        for w in self.canvas_frame.winfo_children(): w.destroy()
        fig, ax = plt.subplots(figsize=(12, 3.5), dpi=100)
        fig.patch.set_facecolor(self.COLORS['bg_secondary'])
        ax.set_facecolor(self.COLORS['bg_secondary'])

        colores = {'A': '#ef4444', 'B': '#3b82f6', 'C': '#10b981', 'D': '#f59e0b', 'E': '#8b5cf6', 'F': '#ec4899', 'G': '#06b6d4', 'H': '#84cc16', 'I': '#f97316', 'J': '#6366f1'}
        nombres = [p.nombre for p in self.procesos]
        y_pos = {n: len(nombres)-i for i, n in enumerate(nombres)}
        alt = 0.6

        for r in self.resultados:
            n, i, f = r["proceso"], r["inicio"], r["fin"]
            y = y_pos[n]
            rect = plt.Rectangle((i, y), f-i, alt, facecolor=colores.get(n, '#64748b'), edgecolor=self.COLORS['bg_secondary'], linewidth=2)
            ax.add_patch(rect)
            ax.text(i + (f-i)/2, y + alt/2, n, ha='center', va='center', color='white', fontsize=11, fontweight='bold')

        t_max = max(p.tiempo_finalizacion for p in self.procesos)
        ax.set_xlim(0, t_max + 1)
        ax.set_ylim(0.5, len(nombres) + 1)
        ax.set_xticks(range(0, t_max + 1))
        ax.set_yticks([y_pos[n] + alt/2 for n in nombres])
        ax.set_yticklabels(nombres, color=self.COLORS['text_primary'], fontsize=11)
        ax.tick_params(colors=self.COLORS['text_secondary'])
        ax.grid(axis='x', linestyle='--', alpha=0.2, color=self.COLORS['text_secondary'])
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.set_title(f"Diagrama de Gantt • {self.combo_algo.get()}", color=self.COLORS['text_primary'], fontsize=14, fontweight='bold', pad=10)
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

if __name__ == "__main__":
    app = PlanificadorApp()
    app.mainloop()