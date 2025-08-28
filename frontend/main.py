"""
Aplicación principal del frontend de escritorio para el sistema de generación de leads.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.simpledialog as simpledialog
import threading
import time
from typing import Dict, Any, Optional
import csv
import os
import sys

# Agregar el directorio frontend al path para resolver importaciones relativas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import FrontendConfig
from api_client import APIClient
from widgets import ScrollingFrame
from components.stats_panel import StatsPanel

class LeadsGeneratorApp:
    """Aplicación principal del frontend de escritorio."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(FrontendConfig.APP_TITLE)
        self.root.geometry(f"{FrontendConfig.APP_WIDTH}x{FrontendConfig.APP_HEIGHT}")
        self.root.minsize(800, 600)
        
        # Configurar estilo
        self.setup_styles()
        
        # Cliente API
        self.api_client = APIClient()
        self.api_client.set_app(self)  # Establecer la referencia a la aplicación
        
        # Variables de estado
        self.current_job_id: Optional[str] = None
        self.is_scraping = False
        self.stats_refresh_job: Optional[str] = None
        self.leads_refresh_job: Optional[str] = None
        
        # Crear interfaz
        self.create_widgets()
        
        # Verificar conexión con la API
        self.check_api_connection()
        
        # Programar actualización periódica
        self.schedule_updates()
    
    def setup_styles(self):
        """Configura los estilos de la aplicación."""
        style = ttk.Style()
        
        # Configurar estilos personalizados
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        style.configure("Success.TButton", foreground=FrontendConfig.SUCCESS_COLOR)
        style.configure("Danger.TButton", foreground=FrontendConfig.DANGER_COLOR)
        
        # Configurar colores para widgets
        self.root.configure(bg="white")
    
    def create_widgets(self):
        """Crea los widgets de la interfaz principal."""
        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear pestañas
        self.create_scraping_tab()
        self.create_leads_tab()
        self.create_stats_tab()
        self.create_logs_tab()
        self.create_advanced_control_tab()
        self.create_statistics_panel_tab()
    
    def create_statistics_panel_tab(self):
        """Crea la pestaña del panel de estadísticas avanzado."""
        self.stats_panel_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_panel_frame, text="Panel de Estadísticas")
        
        # Crear panel de estadísticas
        self.stats_panel = StatsPanel(self.stats_panel_frame)
    
    def create_scraping_tab(self):
        """Crea la pestaña de configuración y control de scraping."""
        self.scraping_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scraping_frame, text="Control de Scraping")
        
        # Título
        title_label = ttk.Label(self.scraping_frame, text="Configuración de Scraping", style="Title.TLabel")
        title_label.pack(pady=10)
        
        # Marco de configuración
        config_frame = ttk.LabelFrame(self.scraping_frame, text="Configuración", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # URL inicial
        ttk.Label(config_frame, text="URL Inicial:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(config_frame, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        self.url_entry.insert(0, "https://example.com")
        
        # Profundidad
        ttk.Label(config_frame, text="Profundidad:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.depth_var = tk.StringVar(value=str(FrontendConfig.DEFAULT_DEPTH))
        depth_spinbox = ttk.Spinbox(config_frame, from_=1, to=10, textvariable=self.depth_var, width=10)
        depth_spinbox.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Delay
        ttk.Label(config_frame, text="Delay (segundos):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.delay_var = tk.StringVar(value=str(FrontendConfig.DEFAULT_DELAY))
        delay_spinbox = ttk.Spinbox(config_frame, from_=0.1, to=10.0, increment=0.1, 
                                   textvariable=self.delay_var, width=10)
        delay_spinbox.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Idiomas
        ttk.Label(config_frame, text="Idiomas:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.languages_entry = ttk.Entry(config_frame, width=50)
        self.languages_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.EW)
        self.languages_entry.insert(0, ",".join(FrontendConfig.DEFAULT_LANGUAGES))
        
        # Configurar expansión de columnas
        config_frame.columnconfigure(1, weight=1)
        
        # Marco de control
        control_frame = ttk.Frame(self.scraping_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Botones de control
        self.start_button = ttk.Button(control_frame, text="Iniciar Scraping", 
                                      command=self.start_scraping, style="Success.TButton")
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Detener Scraping", 
                                     command=self.stop_scraping, style="Danger.TButton")
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.state(['disabled'])
        
        # Estado actual
        self.status_label = ttk.Label(control_frame, text="Estado: No iniciado")
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Marco de estadísticas en tiempo real
        stats_frame = ttk.LabelFrame(self.scraping_frame, text="Estadísticas en Tiempo Real", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Crear marco con scroll para estadísticas
        self.stats_scroll_frame = ScrollingFrame(stats_frame)
        self.stats_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # Etiquetas de estadísticas
        self.stats_labels = {}
        stats_keys = [
            "processed_urls", "queue_size", "leads_found", 
            "emails_found", "errors_count", "avg_response_time"
        ]
        
        for i, key in enumerate(stats_keys):
            label = ttk.Label(self.stats_scroll_frame.frame, text=f"{key}: 0")
            label.pack(anchor=tk.W, pady=2)
            self.stats_labels[key] = label
    
    def create_leads_tab(self):
        """Crea la pestaña de visualización de leads."""
        self.leads_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.leads_frame, text="Leads Encontrados")
        
        # Título
        title_label = ttk.Label(self.leads_frame, text="Leads Encontrados", style="Title.TLabel")
        title_label.pack(pady=10)
        
        # Marco de filtros
        filter_frame = ttk.LabelFrame(self.leads_frame, text="Filtros", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Filtro de idioma
        ttk.Label(filter_frame, text="Idioma:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.language_filter_var = tk.StringVar()
        language_filter_entry = ttk.Entry(filter_frame, textvariable=self.language_filter_var, width=20)
        language_filter_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Filtro de dominio
        ttk.Label(filter_frame, text="Dominio:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.domain_filter_var = tk.StringVar()
        domain_filter_entry = ttk.Entry(filter_frame, textvariable=self.domain_filter_var, width=20)
        domain_filter_entry.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
        
        # Botón de búsqueda
        filter_button = ttk.Button(filter_frame, text="Buscar", command=self.load_leads)
        filter_button.grid(row=0, column=4, padx=10, pady=5, sticky=tk.W)
        
        # Botón de exportar
        export_button = ttk.Button(filter_frame, text="Exportar a CSV", command=self.export_leads)
        export_button.grid(row=0, column=5, padx=10, pady=5, sticky=tk.W)
        
        # Marco de tabla de leads
        table_frame = ttk.Frame(self.leads_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Crear tabla con scroll
        table_container = ttk.Frame(table_frame)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        
        # Treeview para mostrar leads
        self.leads_tree = ttk.Treeview(
            table_container,
            columns=("ID", "URL", "Email", "Idioma", "Estado", "URL Fuente"),
            show="headings",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Configurar scrollbars
        v_scrollbar.config(command=self.leads_tree.yview)
        h_scrollbar.config(command=self.leads_tree.xview)
        
        # Posicionar elementos
        self.leads_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        table_container.columnconfigure(0, weight=1)
        table_container.rowconfigure(0, weight=1)
        
        # Configurar encabezados de columna
        self.leads_tree.heading("ID", text="ID")
        self.leads_tree.heading("URL", text="URL")
        self.leads_tree.heading("Email", text="Email")
        self.leads_tree.heading("Idioma", text="Idioma")
        self.leads_tree.heading("Estado", text="Estado")
        self.leads_tree.heading("URL Fuente", text="URL Fuente")
        
        # Configurar ancho de columnas
        self.leads_tree.column("ID", width=50, anchor=tk.CENTER)
        self.leads_tree.column("URL", width=200)
        self.leads_tree.column("Email", width=150)
        self.leads_tree.column("Idioma", width=80, anchor=tk.CENTER)
        self.leads_tree.column("Estado", width=100, anchor=tk.CENTER)
        self.leads_tree.column("URL Fuente", width=200)
        
        # Marco de paginación
        pagination_frame = ttk.Frame(self.leads_frame)
        pagination_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Información de paginación
        self.pagination_label = ttk.Label(pagination_frame, text="Página 1 de 1")
        self.pagination_label.pack(side=tk.LEFT)
        
        # Botones de paginación
        self.prev_page_button = ttk.Button(pagination_frame, text="Anterior", 
                                          command=self.prev_page, state=tk.DISABLED)
        self.prev_page_button.pack(side=tk.RIGHT, padx=5)
        
        self.next_page_button = ttk.Button(pagination_frame, text="Siguiente", 
                                          command=self.next_page, state=tk.DISABLED)
        self.next_page_button.pack(side=tk.RIGHT, padx=5)
        
        # Variables de paginación
        self.current_page = 1
        self.total_pages = 1
    
    def create_stats_tab(self):
        """Crea la pestaña de estadísticas del sistema."""
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Estadísticas")
        
        # Título
        title_label = ttk.Label(self.stats_frame, text="Estadísticas del Sistema", style="Title.TLabel")
        title_label.pack(pady=10)
        
        # Marco de estadísticas del sistema
        system_stats_frame = ttk.LabelFrame(self.stats_frame, text="Estadísticas del Sistema", padding=10)
        system_stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Crear marco con scroll para estadísticas del sistema
        self.system_stats_scroll_frame = ScrollingFrame(system_stats_frame)
        self.system_stats_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # Etiquetas de estadísticas del sistema
        self.system_stats_labels = {}
        system_stats_keys = [
            "active_jobs", "total_jobs_today", "total_leads_today", 
            "total_emails_today", "database_status", "memory_usage_mb",
            "cpu_usage_percent", "disk_usage_gb"
        ]
        
        for i, key in enumerate(system_stats_keys):
            label = ttk.Label(self.system_stats_scroll_frame.frame, text=f"{key}: -")
            label.pack(anchor=tk.W, pady=2)
            self.system_stats_labels[key] = label
    
    def create_logs_tab(self):
        """Crea la pestaña de logs del sistema."""
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Logs")
        
        # Título
        title_label = ttk.Label(self.logs_frame, text="Logs del Sistema", style="Title.TLabel")
        title_label.pack(pady=10)
        
        # Marco de logs
        logs_container_frame = ttk.Frame(self.logs_frame)
        logs_container_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Crear marco con scroll para logs
        self.logs_scroll_frame = ScrollingFrame(logs_container_frame)
        self.logs_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # Área de texto para logs
        self.logs_text = tk.Text(self.logs_scroll_frame.frame, wrap=tk.WORD, state=tk.DISABLED)
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Botón para limpiar logs
        clear_logs_button = ttk.Button(self.logs_frame, text="Limpiar Logs", command=self.clear_logs)
        clear_logs_button.pack(pady=5)
    
    def check_api_connection(self):
        """Verifica la conexión con la API."""
        try:
            response = self.api_client.health_check()
            if response.get("status") == "healthy":
                self.status_label.config(text="Estado: Conectado a la API")
            else:
                self.status_label.config(text="Estado: Error de conexión")
                messagebox.showwarning("Advertencia", "No se puede conectar con la API del backend")
        except Exception as e:
            self.status_label.config(text="Estado: Error de conexión")
            messagebox.showerror("Error", f"No se puede conectar con la API: {str(e)}")
    
    def start_scraping(self):
        """Inicia el proceso de scraping."""
        # Validar URL
        start_url = self.url_entry.get().strip()
        if not start_url:
            messagebox.showerror("Error", "Por favor, ingrese una URL inicial")
            return
        
        # Validar que sea una URL válida
        if not start_url.startswith(("http://", "https://")):
            messagebox.showerror("Error", "La URL debe comenzar con http:// o https://")
            return
        
        try:
            # Obtener parámetros
            depth = int(self.depth_var.get())
            delay = float(self.delay_var.get())
            languages_str = self.languages_entry.get().strip()
            languages = [lang.strip() for lang in languages_str.split(",") if lang.strip()]
            
            if not languages:
                messagebox.showerror("Error", "Por favor, ingrese al menos un idioma")
                return
            
            # Deshabilitar botón de inicio y habilitar botón de detener
            self.start_button.state(['disabled'])
            self.stop_button.state(['!disabled'])
            self.status_label.config(text="Estado: Iniciando scraping...")
            
            # Crear una barra de progreso para mostrar que está trabajando
            self.progress_frame = ttk.Frame(self.scraping_frame)
            self.progress_frame.pack(fill=tk.X, padx=10, pady=5)
            
            self.progress_label = ttk.Label(self.progress_frame, text="Iniciando proceso de scraping...")
            self.progress_label.pack(side=tk.LEFT)
            
            self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
            self.progress_bar.pack(fill=tk.X, expand=True, padx=(10, 0))
            self.progress_bar.start(10)  # Iniciar la animación de la barra de progreso
            
            # Iniciar scraping en un hilo separado
            def start_job():
                try:
                    response = self.api_client.start_scraping_job(
                        start_url=start_url,
                        depth=depth,
                        languages=languages,
                        delay=delay
                    )
                    
                    self.current_job_id = response.get("job_id")
                    self.is_scraping = True
                    self.status_label.config(text=f"Estado: Scraping en ejecución (ID: {self.current_job_id})")
                    self.progress_label.config(text="Scraping en progreso...")
                    
                    # Actualizar estadísticas inmediatamente
                    self.update_stats()
                except Exception as e:
                    # Detener la barra de progreso y eliminarla
                    self.progress_bar.stop()
                    self.progress_frame.destroy()
                    
                    # Mostrar mensaje de error más descriptivo
                    error_msg = str(e)
                    if "400" in error_msg:
                        messagebox.showerror("Error de Solicitud", f"La solicitud no es válida: {error_msg}")
                    elif "404" in error_msg:
                        messagebox.showerror("Error de Recurso", f"Recurso no encontrado: {error_msg}")
                    else:
                        messagebox.showerror("Error", f"Error al iniciar el scraping: {error_msg}")
                    self.reset_scraping_controls()
                else:
                    # Programar la eliminación de la barra de progreso después de un corto tiempo
                    self.root.after(2000, self._remove_progress_bar)
            
            threading.Thread(target=start_job, daemon=True).start()
            
        except ValueError as e:
            messagebox.showerror("Error", "Por favor, verifique los valores ingresados")
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar el scraping: {str(e)}")
    
    def stop_scraping(self):
        """Detiene el proceso de scraping."""
        if not self.current_job_id:
            messagebox.showwarning("Advertencia", "No hay un proceso de scraping en ejecución.")
            return
        
        # Confirmar detención
        if not messagebox.askyesno("Confirmar", "¿Está seguro de que desea detener el scraping?"):
            return
        
        try:
            # Detener scraping en un hilo separado
            def stop_job():
                try:
                    if self.current_job_id:
                        response = self.api_client.stop_scraping_job(self.current_job_id)
                        self.is_scraping = False
                        self.status_label.config(text="Estado: Scraping detenido")
                        self.reset_scraping_controls()
                except Exception as e:
                    messagebox.showerror("Error", f"Error al detener el scraping: {str(e)}")
            
            threading.Thread(target=stop_job, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al detener el scraping: {str(e)}")
    
    def reset_scraping_controls(self):
        """Reinicia los controles de scraping."""
        self.start_button.state(['!disabled'])
        self.stop_button.state(['disabled'])
        self.current_job_id = None
        self.is_scraping = False
    
    def _remove_progress_bar(self):
        """Elimina la barra de progreso después de que el proceso haya comenzado."""
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.stop()
        if hasattr(self, 'progress_frame') and self.progress_frame:
            self.progress_frame.destroy()
        
        # Limpiar las referencias
        if hasattr(self, 'progress_bar'):
            delattr(self, 'progress_bar')
        if hasattr(self, 'progress_frame'):
            delattr(self, 'progress_frame')
        if hasattr(self, 'progress_label'):
            delattr(self, 'progress_label')
    
    def update_stats(self):
        """Actualiza las estadísticas en tiempo real."""
        if not self.current_job_id:
            return

        try:
            response = self.api_client.get_job_status(self.current_job_id)
            status = response.get("status")

            # Check if job has finished
            if status in ["completed", "failed", "cancelled"]:
                self.is_scraping = False
                self.status_label.config(text=f"Estado: {status}")
                
                # Mostrar mensaje al usuario según el estado
                if status == "completed":
                    messagebox.showinfo("Scraping Completado", "El proceso de scraping ha finalizado exitosamente.")
                elif status == "failed":
                    messagebox.showerror("Scraping Fallido", "El proceso de scraping ha fallado.")
                elif status == "cancelled":
                    messagebox.showinfo("Scraping Cancelado", "El proceso de scraping ha sido cancelado.")
                
                self.reset_scraping_controls()
                return

            stats = response.get("stats", {})

            # Actualizar etiquetas de estadísticas
            for key, label in self.stats_labels.items():
                value = stats.get(key, "N/A")
                label.config(text=f"{key}: {value}")
                
                # Actualizar el progreso si la barra de progreso aún existe
                if hasattr(self, 'progress_label') and self.progress_label:
                    processed = stats.get("processed_urls", 0)
                    queue_size = stats.get("queue_size", 1)
                    if queue_size > 0:
                        progress_text = f"Procesando URLs... ({processed}/{queue_size})"
                        self.progress_label.config(text=progress_text)
        except Exception as e:
            # No mostrar error aquí para no interrumpir la actualización
            pass
    def load_leads(self):
        """Carga los leads encontrados."""
        try:
            # Obtener filtros
            language = self.language_filter_var.get().strip() or None
            domain = self.domain_filter_var.get().strip() or None
            
            # Cargar leads
            response = self.api_client.get_leads(
                page=self.current_page,
                limit=50,
                language=language,
                domain=domain
            )
            
            # Limpiar tabla
            for item in self.leads_tree.get_children():
                self.leads_tree.delete(item)
            
            # Agregar leads a la tabla
            leads = response.get("leads", [])
            for lead in leads:
                self.leads_tree.insert("", tk.END, values=(
                    lead.get("id", ""),
                    lead.get("url", ""),
                    lead.get("contact_email", ""),
                    lead.get("language", ""),
                    lead.get("status", ""),
                    lead.get("source_url", "")
                ))
            
            # Actualizar información de paginación
            pagination = response.get("pagination", {})
            self.total_pages = pagination.get("total_pages", 1)
            self.current_page = pagination.get("current_page", 1)
            self.pagination_label.config(
                text=f"Página {self.current_page} de {self.total_pages}"
            )
            
            # Actualizar estado de botones de paginación
            self.prev_page_button.state(['!disabled' if self.current_page > 1 else 'disabled'])
            self.next_page_button.state(['!disabled' if self.current_page < self.total_pages else 'disabled'])
            
        except Exception as e:
            # Mostrar mensaje de error más descriptivo
            error_msg = str(e)
            if "40" in error_msg:
                messagebox.showerror("Error de Solicitud", f"La solicitud no es válida: {error_msg}")
            elif "404" in error_msg:
                messagebox.showerror("Error de Recurso", f"Recurso no encontrado: {error_msg}")
            else:
                messagebox.showerror("Error", f"Error al cargar leads: {error_msg}")
    
    def prev_page(self):
        """Navega a la página anterior de leads."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_leads()
    
    def next_page(self):
        """Navega a la página siguiente de leads."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_leads()
    
    def export_leads(self):
        """Exporta los leads a un archivo CSV."""
        try:
            # Pedir ubicación del archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
            )
            
            if not filename:
                return
            
            # Obtener todos los leads (esto es una simplificación, en producción se debería
            # implementar una exportación más eficiente)
            all_leads = []
            page = 1
            while True:
                response = self.api_client.get_leads(page=page, limit=100)
                leads = response.get("leads", [])
                if not leads:
                    break
                all_leads.extend(leads)
                pagination = response.get("pagination", {})
                if page >= pagination.get("total_pages", 1):
                    break
                page += 1
            
            # Escribir a CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["id", "url", "contact_email", "language", "status", "source_url"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for lead in all_leads:
                    writer.writerow({
                        "id": lead.get("id", ""),
                        "url": lead.get("url", ""),
                        "contact_email": lead.get("contact_email", ""),
                        "language": lead.get("language", ""),
                        "status": lead.get("status", ""),
                        "source_url": lead.get("source_url", "")
                    })
            
            messagebox.showinfo("Éxito", f"Leads exportados correctamente a {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar leads: {str(e)}")
    
    def add_log_message(self, message: str):
        """Agrega un mensaje a la pestaña de logs."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Agregar el mensaje al área de texto de logs
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.insert(tk.END, formatted_message)
        self.logs_text.config(state=tk.DISABLED)
        
        # Hacer scroll automáticamente al final
        self.logs_text.see(tk.END)
    
    def clear_logs(self):
        """Limpia el área de logs."""
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.delete(1.0, tk.END)
        self.logs_text.config(state=tk.DISABLED)
    
    def schedule_updates(self):
        """Programa actualizaciones periódicas."""
        # Actualizar estadísticas cada 5 segundos si hay un scraping en ejecución
        if self.is_scraping and self.current_job_id:
            self.update_stats()
        
        # Actualizar leads cada 10 segundos
        self.load_leads()
        
        # Programar próxima actualización
        self.root.after(FrontendConfig.STATS_REFRESH_INTERVAL, self.schedule_updates)
    
    def on_closing(self):
        """Maneja el cierre de la aplicación."""
        # Cancelar trabajos programados
        if self.stats_refresh_job:
            self.root.after_cancel(self.stats_refresh_job)
        if self.leads_refresh_job:
            self.root.after_cancel(self.leads_refresh_job)
        
        # Cerrar ventana
        self.root.destroy()
    
    def create_advanced_control_tab(self):
        """Crea la pestaña de control avanzado de jobs."""
        self.advanced_control_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_control_frame, text="Control Avanzado")
        
        # Título
        title_label = ttk.Label(self.advanced_control_frame, text="Control Avanzado de Jobs", style="Title.TLabel")
        title_label.pack(pady=10)
        
        # Marco de control individual
        individual_frame = ttk.LabelFrame(self.advanced_control_frame, text="Control Individual", padding=10)
        individual_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Job ID
        ttk.Label(individual_frame, text="ID del Job:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.job_id_entry = ttk.Entry(individual_frame, width=30)
        self.job_id_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.EW)
        
        # Botones de control individual
        individual_buttons_frame = ttk.Frame(individual_frame)
        individual_buttons_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(individual_buttons_frame, text="Pausar Job",
                       command=self.pause_job).pack(side=tk.LEFT, padx=5)
        ttk.Button(individual_buttons_frame, text="Reanudar Job",
                       command=self.resume_job).pack(side=tk.LEFT, padx=5)
        ttk.Button(individual_buttons_frame, text="Actualizar Prioridad",
                       command=self.update_job_priority).pack(side=tk.LEFT, padx=5)
        ttk.Button(individual_buttons_frame, text="Obtener Progreso",
                       command=self.get_job_progress).pack(side=tk.LEFT, padx=5)
        ttk.Button(individual_buttons_frame, text="Obtener Logs",
                       command=self.get_job_logs).pack(side=tk.LEFT, padx=5)
        
        # Marco de control masivo
        mass_frame = ttk.LabelFrame(self.advanced_control_frame, text="Control Masivo", padding=10)
        mass_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Botones de control masivo
        mass_buttons_frame = ttk.Frame(mass_frame)
        mass_buttons_frame.pack(pady=10)
        
        ttk.Button(mass_buttons_frame, text="Pausar Todos los Jobs",
                       command=self.pause_all_jobs).pack(side=tk.LEFT, padx=5)
        ttk.Button(mass_buttons_frame, text="Reanudar Todos los Jobs",
                       command=self.resume_all_jobs).pack(side=tk.LEFT, padx=5)
        ttk.Button(mass_buttons_frame, text="Cancelar Todos los Jobs Activos",
                       command=self.cancel_all_active_jobs).pack(side=tk.LEFT, padx=5)
        
        # Marco de gestión de cola
        queue_frame = ttk.LabelFrame(self.advanced_control_frame, text="Gestión de Cola", padding=10)
        queue_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Botones de gestión de cola
        queue_buttons_frame = ttk.Frame(queue_frame)
        queue_buttons_frame.pack(pady=10)
        
        ttk.Button(queue_buttons_frame, text="Obtener Estado de Cola",
                       command=self.get_queue_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(queue_buttons_frame, text="Limpiar Cola",
                       command=self.clear_queue).pack(side=tk.LEFT, padx=5)
        
        # Marco de resultados
        results_frame = ttk.LabelFrame(queue_frame, text="Resultados", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Área de texto para mostrar resultados
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=10)
        self.results_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Scrollbar para el área de resultados
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=results_scrollbar.set)
        
        # Configurar expansión de columnas
        individual_frame.columnconfigure(1, weight=1)
    
    def pause_job(self):
        """Pausa un job específico."""
        job_id = self.job_id_entry.get().strip()
        if not job_id:
            messagebox.showerror("Error", "Por favor, ingrese un ID de job")
            return
        
        try:
            response = self.api_client.pause_job(job_id)
            messagebox.showinfo("Éxito", response.get("message", "Job pausado exitosamente"))
        except Exception as e:
            messagebox.showerror("Error", f"Error al pausar el job: {str(e)}")
    
    def resume_job(self):
        """Reanuda un job pausado."""
        job_id = self.job_id_entry.get().strip()
        if not job_id:
            messagebox.showerror("Error", "Por favor, ingrese un ID de job")
            return
        
        try:
            response = self.api_client.resume_job(job_id)
            messagebox.showinfo("Éxito", response.get("message", "Job reanudado exitosamente"))
        except Exception as e:
            messagebox.showerror("Error", f"Error al reanudar el job: {str(e)}")
    
    def update_job_priority(self):
        """Actualiza la prioridad de un job."""
        job_id = self.job_id_entry.get().strip()
        if not job_id:
            messagebox.showerror("Error", "Por favor, ingrese un ID de job")
            return
        
        # Pedir nueva prioridad
        priority_str = simpledialog.askstring("Prioridad", "Ingrese la nueva prioridad (0-10):")
        if not priority_str:
            return
        
        try:
            priority = int(priority_str)
            if priority < 0 or priority > 10:
                raise ValueError("La prioridad debe estar entre 0 y 10")
        except ValueError as e:
            messagebox.showerror("Error", f"Prioridad inválida: {str(e)}")
            return
        
        try:
            response = self.api_client.update_job_priority(job_id, priority)
            messagebox.showinfo("Éxito", response.get("message", "Prioridad actualizada exitosamente"))
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar la prioridad: {str(e)}")
    
    def get_job_progress(self):
        """Obtiene el progreso detallado de un job."""
        job_id = self.job_id_entry.get().strip()
        if not job_id:
            messagebox.showerror("Error", "Por favor, ingrese un ID de job")
            return
        
        try:
            response = self.api_client.get_job_progress(job_id)
            # Mostrar resultados en el área de texto
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Progreso del Job {job_id}:\n")
            self.results_text.insert(tk.END, f"Estado: {response.get('status')}\n")
            self.results_text.insert(tk.END, f"Progreso: {response.get('progress')}%\n")
            self.results_text.insert(tk.END, f"Items totales: {response.get('total_items')}\n")
            self.results_text.insert(tk.END, f"Items procesados: {response.get('processed_items')}\n")
            self.results_text.insert(tk.END, f"Tasa de éxito: {response.get('success_rate'):.2%}\n")
            self.results_text.insert(tk.END, f"Tiempo estimado de finalización: {response.get('estimated_completion')}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener el progreso: {str(e)}")
    
    def get_job_logs(self):
        """Obtiene los logs específicos de un job."""
        job_id = self.job_id_entry.get().strip()
        if not job_id:
            messagebox.showerror("Error", "Por favor, ingrese un ID de job")
            return
        
        try:
            response = self.api_client.get_job_logs(job_id)
            # Mostrar resultados en el área de texto
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Logs del Job {job_id}:\n\n")
            for log in response:
                self.results_text.insert(tk.END, f"[{log.get('created_at', '')}] {log.get('level', '')}: {log.get('message', '')}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener los logs: {str(e)}")
    
    def pause_all_jobs(self):
        """Pausa todos los jobs activos."""
        try:
            response = self.api_client.pause_all_jobs()
            messagebox.showinfo("Éxito", response.get("message", "Todos los jobs pausados exitosamente"))
        except Exception as e:
            messagebox.showerror("Error", f"Error al pausar todos los jobs: {str(e)}")
    
    def resume_all_jobs(self):
        """Reanuda todos los jobs pausados."""
        try:
            response = self.api_client.resume_all_jobs()
            messagebox.showinfo("Éxito", response.get("message", "Todos los jobs reanudados exitosamente"))
        except Exception as e:
            messagebox.showerror("Error", f"Error al reanudar todos los jobs: {str(e)}")
    
    def cancel_all_active_jobs(self):
        """Cancela todos los jobs activos."""
        if not messagebox.askyesno("Confirmar", "¿Está seguro de que desea cancelar todos los jobs activos?"):
            return
        
        try:
            response = self.api_client.cancel_all_active_jobs()
            messagebox.showinfo("Éxito", response.get("message", "Todos los jobs activos cancelados exitosamente"))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cancelar todos los jobs activos: {str(e)}")
    
    def get_queue_status(self):
        """Obtiene el estado de la cola de jobs."""
        try:
            response = self.api_client.get_queue_status()
            # Mostrar resultados en el área de texto
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Estado de la Cola:\n")
            self.results_text.insert(tk.END, f"Total de jobs: {response.get('total_jobs')}\n")
            self.results_text.insert(tk.END, f"Jobs pendientes: {response.get('pending_jobs')}\n")
            self.results_text.insert(tk.END, f"Jobs en proceso: {response.get('processing_jobs')}\n")
            self.results_text.insert(tk.END, f"Jobs pausados: {response.get('paused_jobs')}\n")
            self.results_text.insert(tk.END, f"Jobs completados: {response.get('completed_jobs')}\n")
            self.results_text.insert(tk.END, f"Jobs fallidos: {response.get('failed_jobs')}\n")
            self.results_text.insert(tk.END, f"Jobs cancelados: {response.get('cancelled_jobs')}\n\n")
            self.results_text.insert(tk.END, "Jobs en cola:\n")
            for item in response.get('queue_items', []):
                self.results_text.insert(tk.END, f"  - ID: {item.get('job_id')}, Estado: {item.get('status')}, Prioridad: {item.get('priority')}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener el estado de la cola: {str(e)}")
    
    def clear_queue(self):
        """Limpia la cola de jobs pendientes."""
        if not messagebox.askyesno("Confirmar", "¿Está seguro de que desea limpiar la cola de jobs pendientes?"):
            return
        
        try:
            response = self.api_client.clear_queue()
            messagebox.showinfo("Éxito", response.get("message", "Cola limpiada exitosamente"))
        except Exception as e:
            messagebox.showerror("Error", f"Error al limpiar la cola: {str(e)}")

def main():
    """Función principal para ejecutar la aplicación."""
    root = tk.Tk()
    app = LeadsGeneratorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()