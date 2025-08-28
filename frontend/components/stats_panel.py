"""
Panel de estadísticas para la aplicación de generación de leads.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime
import threading
import time

class StatsPanel:
    def __init__(self, parent):
        self.parent = parent
        self.stats_frame = ttk.Frame(parent)
        self.stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Variables para almacenar datos
        self.system_stats = {}
        self.scraping_stats = {}
        self.performance_stats = {}
        
        # Crear widgets
        self.create_widgets()
        
        # Iniciar actualización automática
        self.auto_update = False
        self.update_thread = None
        # Desactivamos la actualización automática por problemas de threading
        # self.update_thread = threading.Thread(target=self.auto_update_stats, daemon=True)
        # self.update_thread.start()
    
    def create_widgets(self):
        """Crea los widgets del panel de estadísticas."""
        # Título
        title_label = ttk.Label(self.stats_frame, text="Panel de Estadísticas", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.stats_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de Estadísticas del Sistema
        self.system_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.system_frame, text="Sistema")
        self.create_system_widgets()
        
        # Pestaña de Estadísticas de Scraping
        self.scraping_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scraping_frame, text="Scraping")
        self.create_scraping_widgets()
        
        # Pestaña de Rendimiento
        self.performance_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.performance_frame, text="Rendimiento")
        self.create_performance_widgets()
        
        # Botones de control
        control_frame = ttk.Frame(self.stats_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.update_button = ttk.Button(control_frame, text="Actualizar", command=self.update_stats)
        self.update_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.auto_update_var = tk.BooleanVar(value=True)
        self.auto_update_check = ttk.Checkbutton(
            control_frame, 
            text="Actualización automática", 
            variable=self.auto_update_var,
            command=self.toggle_auto_update
        )
        self.auto_update_check.pack(side=tk.LEFT)
        
        # Estado
        self.status_label = ttk.Label(control_frame, text="Última actualización: Nunca")
        self.status_label.pack(side=tk.RIGHT)
    
    def create_system_widgets(self):
        """Crea los widgets para la pestaña de estadísticas del sistema."""
        # Marco principal
        main_frame = ttk.Frame(self.system_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cuadrícula de métricas principales
        metrics_frame = ttk.LabelFrame(main_frame, text="Métricas Principales")
        metrics_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Variables para las etiquetas
        self.active_jobs_var = tk.StringVar(value="0")
        self.total_jobs_var = tk.StringVar(value="0")
        self.total_leads_var = tk.StringVar(value="0")
        self.total_emails_var = tk.StringVar(value="0")
        
        # Etiquetas de métricas
        ttk.Label(metrics_frame, text="Jobs Activos:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(metrics_frame, textvariable=self.active_jobs_var, font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(metrics_frame, text="Jobs Hoy:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(metrics_frame, textvariable=self.total_jobs_var, font=("Arial", 12, "bold")).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(metrics_frame, text="Leads Hoy:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(metrics_frame, textvariable=self.total_leads_var, font=("Arial", 12, "bold")).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(metrics_frame, text="Emails Hoy:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(metrics_frame, textvariable=self.total_emails_var, font=("Arial", 12, "bold")).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Salud del sistema
        health_frame = ttk.LabelFrame(main_frame, text="Salud del Sistema")
        health_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cpu_usage_var = tk.StringVar(value="0%")
        self.memory_usage_var = tk.StringVar(value="0 MB")
        self.disk_usage_var = tk.StringVar(value="0 GB")
        
        ttk.Label(health_frame, text="CPU:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(health_frame, textvariable=self.cpu_usage_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(health_frame, text="Memoria:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(health_frame, textvariable=self.memory_usage_var).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(health_frame, text="Disco:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(health_frame, textvariable=self.disk_usage_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Actividad reciente
        activity_frame = ttk.LabelFrame(main_frame, text="Actividad Reciente")
        activity_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de actividad
        self.activity_listbox = tk.Listbox(activity_frame, height=8)
        self.activity_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar para la lista
        scrollbar = ttk.Scrollbar(self.activity_listbox, orient=tk.VERTICAL, command=self.activity_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.activity_listbox.config(yscrollcommand=scrollbar.set)
    
    def create_scraping_widgets(self):
        """Crea los widgets para la pestaña de estadísticas de scraping."""
        # Marco principal
        main_frame = ttk.Frame(self.scraping_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Métricas de scraping
        metrics_frame = ttk.LabelFrame(main_frame, text="Métricas de Scraping")
        metrics_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.urls_processed_var = tk.StringVar(value="0")
        self.success_rate_var = tk.StringVar(value="0%")
        self.avg_time_var = tk.StringVar(value="0ms")
        self.domains_crawled_var = tk.StringVar(value="0")
        
        ttk.Label(metrics_frame, text="URLs Procesadas:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(metrics_frame, textvariable=self.urls_processed_var, font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(metrics_frame, text="Tasa de Éxito:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(metrics_frame, textvariable=self.success_rate_var, font=("Arial", 12, "bold")).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(metrics_frame, text="Tiempo Promedio:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(metrics_frame, textvariable=self.avg_time_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(metrics_frame, text="Dominios Crawleados:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(metrics_frame, textvariable=self.domains_crawled_var).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        # URLs por hora (gráfico simulado)
        urls_frame = ttk.LabelFrame(main_frame, text="URLs por Hora (Últimas 24 horas)")
        urls_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Canvas para el gráfico
        self.urls_canvas = tk.Canvas(urls_frame, height=150, bg="white")
        self.urls_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Dominios principales
        domains_frame = ttk.LabelFrame(main_frame, text="Dominios Principales")
        domains_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de dominios
        self.domains_listbox = tk.Listbox(domains_frame, height=6)
        self.domains_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar para la lista
        scrollbar = ttk.Scrollbar(self.domains_listbox, orient=tk.VERTICAL, command=self.domains_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.domains_listbox.config(yscrollcommand=scrollbar.set)
    
    def create_performance_widgets(self):
        """Crea los widgets para la pestaña de rendimiento."""
        # Marco principal
        main_frame = ttk.Frame(self.performance_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Rendimiento de scraping
        scraping_perf_frame = ttk.LabelFrame(main_frame, text="Rendimiento de Scraping")
        scraping_perf_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.requests_per_sec_var = tk.StringVar(value="0")
        self.error_rate_var = tk.StringVar(value="0%")
        
        ttk.Label(scraping_perf_frame, text="Solicitudes/Segundo:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(scraping_perf_frame, textvariable=self.requests_per_sec_var, font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(scraping_perf_frame, text="Tasa de Error:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(scraping_perf_frame, textvariable=self.error_rate_var, font=("Arial", 12, "bold")).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Recursos del sistema
        resources_frame = ttk.LabelFrame(main_frame, text="Recursos del Sistema")
        resources_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.sys_cpu_var = tk.StringVar(value="0%")
        self.sys_memory_var = tk.StringVar(value="0%")
        
        ttk.Label(resources_frame, text="CPU del Sistema:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(resources_frame, textvariable=self.sys_cpu_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(resources_frame, text="Memoria del Sistema:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(resources_frame, textvariable=self.sys_memory_var).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        # Estado de la cola
        queue_frame = ttk.LabelFrame(main_frame, text="Estado de la Cola")
        queue_frame.pack(fill=tk.X)
        
        self.pending_urls_var = tk.StringVar(value="0")
        self.processing_urls_var = tk.StringVar(value="0")
        self.completed_urls_var = tk.StringVar(value="0")
        self.failed_urls_var = tk.StringVar(value="0")
        
        ttk.Label(queue_frame, text="Pendientes:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(queue_frame, textvariable=self.pending_urls_var, font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(queue_frame, text="Procesando:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(queue_frame, textvariable=self.processing_urls_var, font=("Arial", 10, "bold")).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(queue_frame, text="Completados:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Label(queue_frame, textvariable=self.completed_urls_var, font=("Arial", 10, "bold")).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(queue_frame, text="Fallidos:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Label(queue_frame, textvariable=self.failed_urls_var, font=("Arial", 10, "bold")).grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
    
    def update_stats(self):
        """Actualiza todas las estadísticas."""
        try:
            # Actualizar estadísticas del sistema
            self.update_system_stats()
            
            # Actualizar estadísticas de scraping
            self.update_scraping_stats()
            
            # Actualizar estadísticas de rendimiento
            self.update_performance_stats()
            
            # Actualizar estado usando after() para asegurar que se ejecute en el hilo principal
            self.stats_frame.after(0, self._update_status_label)
            
        except Exception as e:
            # Usar after() para mostrar el mensaje de error en el hilo principal
            self.stats_frame.after(0, lambda: messagebox.showerror("Error", f"Error al actualizar estadísticas: {str(e)}"))
    
    def _update_status_label(self):
        """Actualiza la etiqueta de estado en el hilo principal."""
        try:
            self.status_label.config(text=f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"Error al actualizar la etiqueta de estado: {e}")
    
    def update_system_stats(self):
        """Actualiza las estadísticas del sistema."""
        try:
            response = requests.get("http://devactivo.com/api/v1/stats/system", timeout=5)
            if response.status_code == 200:
                self.system_stats = response.json()
                
                # Actualizar variables
                self.active_jobs_var.set(str(self.system_stats.get("active_jobs", 0)))
                self.total_jobs_var.set(str(self.system_stats.get("total_jobs_today", 0)))
                self.total_leads_var.set(str(self.system_stats.get("total_leads_today", 0)))
                self.total_emails_var.set(str(self.system_stats.get("total_emails_today", 0)))
                
                # Actualizar salud del sistema
                health = self.system_stats.get("system_health", {})
                self.cpu_usage_var.set(f"{health.get('cpu_usage_percent', 0)}%")
                self.memory_usage_var.set(f"{health.get('memory_usage_mb', 0)} MB")
                self.disk_usage_var.set(f"{health.get('disk_usage_gb', 0)} GB")
                
                # Actualizar actividad reciente
                self.activity_listbox.delete(0, tk.END)
                recent_activity = self.system_stats.get("recent_activity", [])
                for activity in recent_activity[:10]:  # Mostrar solo las 10 más recientes
                    timestamp = activity.get("timestamp", "")[:19]  # Solo la parte de la fecha
                    level = activity.get("level", "")
                    message = activity.get("message", "")
                    self.activity_listbox.insert(tk.END, f"[{timestamp}] {level}: {message}")
            else:
                print(f"Error al obtener estadísticas del sistema: {response.status_code}")
        except Exception as e:
            print(f"Error de conexión al obtener estadísticas del sistema: {e}")
    
    def update_scraping_stats(self):
        """Actualiza las estadísticas de scraping."""
        try:
            response = requests.get("http://devactivo.com/api/v1/stats/scraping", timeout=5)
            if response.status_code == 200:
                self.scraping_stats = response.json()
                
                # Actualizar variables
                self.urls_processed_var.set(str(self.scraping_stats.get("total_urls_processed", 0)))
                self.success_rate_var.set(f"{self.scraping_stats.get('success_rate', 0)}%")
                self.avg_time_var.set(f"{self.scraping_stats.get('avg_processing_time', 0)}ms")
                self.domains_crawled_var.set(str(self.scraping_stats.get("domains_crawled", 0)))
                
                # Actualizar URLs por hora (gráfico simulado)
                self.draw_urls_chart()
                
                # Actualizar dominios principales
                self.domains_listbox.delete(0, tk.END)
                top_domains = self.scraping_stats.get("top_domains", [])
                for domain in top_domains[:10]:  # Mostrar solo los 10 principales
                    domain_name = domain.get("domain", "")
                    count = domain.get("count", 0)
                    self.domains_listbox.insert(tk.END, f"{domain_name}: {count} websites")
            else:
                print(f"Error al obtener estadísticas de scraping: {response.status_code}")
        except Exception as e:
            print(f"Error de conexión al obtener estadísticas de scraping: {e}")
    
    def update_performance_stats(self):
        """Actualiza las estadísticas de rendimiento."""
        try:
            response = requests.get("http://devactivo.com/api/v1/stats/performance", timeout=5)
            if response.status_code == 200:
                self.performance_stats = response.json()
                
                # Actualizar rendimiento de scraping
                scraping_perf = self.performance_stats.get("scraping_performance", {})
                self.requests_per_sec_var.set(str(scraping_perf.get("requests_per_second", 0)))
                self.error_rate_var.set(f"{scraping_perf.get('error_rate_percent', 0)}%")
                
                # Actualizar recursos del sistema
                sys_resources = self.performance_stats.get("system_resources", {})
                self.sys_cpu_var.set(f"{sys_resources.get('cpu_percent', 0)}%")
                self.sys_memory_var.set(f"{sys_resources.get('memory_percent', 0)}%")
                
                # Actualizar estado de la cola
                queue_status = self.performance_stats.get("queue_status", {})
                self.pending_urls_var.set(str(queue_status.get("pending_urls", 0)))
                self.processing_urls_var.set(str(queue_status.get("processing_urls", 0)))
                self.completed_urls_var.set(str(queue_status.get("completed_urls", 0)))
                self.failed_urls_var.set(str(queue_status.get("failed_urls", 0)))
            else:
                print(f"Error al obtener estadísticas de rendimiento: {response.status_code}")
        except Exception as e:
            print(f"Error de conexión al obtener estadísticas de rendimiento: {e}")
    
    def draw_urls_chart(self):
        """Dibuja un gráfico simulado de URLs por hora."""
        self.urls_canvas.delete("all")
        
        # Obtener datos de URLs por hora
        urls_by_hour = self.scraping_stats.get("urls_by_hour", [])
        if not urls_by_hour:
            return
        
        # Encontrar el valor máximo para escalar
        max_count = max([item.get("count", 0) for item in urls_by_hour], default=1)
        if max_count == 0:
            max_count = 1
        
        # Dimensiones del canvas
        canvas_width = self.urls_canvas.winfo_width()
        canvas_height = self.urls_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 400
            canvas_height = 150
        
        # Dibujar barras
        bar_width = canvas_width / len(urls_by_hour)
        for i, item in enumerate(urls_by_hour):
            count = item.get("count", 0)
            hour = item.get("hour", 0)
            
            # Calcular altura de la barra
            bar_height = (count / max_count) * (canvas_height - 20)
            
            # Coordenadas de la barra
            x1 = i * bar_width + 2
            y1 = canvas_height - bar_height - 10
            x2 = (i + 1) * bar_width - 2
            y2 = canvas_height - 10
            
            # Dibujar barra
            self.urls_canvas.create_rectangle(x1, y1, x2, y2, fill="steelblue", outline="white")
            
            # Etiqueta de hora (cada 3 horas)
            if i % 3 == 0:
                self.urls_canvas.create_text(
                    (x1 + x2) / 2, 
                    canvas_height - 5, 
                    text=str(hour), 
                    anchor=tk.S,
                    font=("Arial", 8)
                )
    
    def auto_update_stats(self):
        """Actualiza automáticamente las estadísticas."""
        # Esta función está desactivada por problemas de threading
        pass
        # while self.auto_update:
        #     self.update_stats()
        #     time.sleep(30)  # Actualizar cada 30 segundos
    
    def toggle_auto_update(self):
        """Activa/desactiva la actualización automática."""
        self.auto_update = self.auto_update_var.get()
        # Desactivamos la funcionalidad de actualización automática por problemas de threading
        # if self.auto_update and (not hasattr(self, 'update_thread') or not self.update_thread.is_alive()):
        #     self.update_thread = threading.Thread(target=self.auto_update_stats, daemon=True)
        #     self.update_thread.start()
    
    def destroy(self):
        """Limpia recursos antes de destruir el panel."""
        self.auto_update = False
        # Desactivamos la funcionalidad de actualización automática por problemas de threading
        # if hasattr(self, 'update_thread') and self.update_thread.is_alive():
        #     self.update_thread.join(timeout=1)
        self.stats_frame.destroy()

# Función para probar el panel
def test_stats_panel():
    """Función para probar el panel de estadísticas."""
    root = tk.Tk()
    root.title("Panel de Estadísticas - Generador de Leads")
    root.geometry("800x600")
    
    # Crear panel de estadísticas
    stats_panel = StatsPanel(root)
    
    # Botón para cerrar
    close_button = ttk.Button(root, text="Cerrar", command=root.destroy)
    close_button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_stats_panel()