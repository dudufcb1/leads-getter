"""
Widgets personalizados para la aplicación de generación de leads.
"""

import tkinter as tk
from tkinter import ttk

class ScrollingFrame(ttk.Frame):
    """Marco con barras de desplazamiento para contenido extenso."""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        # Crear canvas y scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configurar scrollable frame
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Crear ventana en el canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Empaquetar elementos
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con la rueda del mouse
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        
        # Configurar scroll con la barra espaciadora
        self.canvas.bind("<Key>", self._on_key_press)
        self.scrollable_frame.bind("<Key>", self._on_key_press)
        
        # Hacer que el canvas pueda recibir eventos de teclado
        self.canvas.focus_set()
    
    def _on_mousewheel(self, event):
        """Maneja el scroll con la rueda del mouse."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _on_key_press(self, event):
        """Maneja el scroll con el teclado."""
        if event.keysym == "Up":
            self.canvas.yview_scroll(-1, "units")
        elif event.keysym == "Down":
            self.canvas.yview_scroll(1, "units")
        elif event.keysym == "Prior":  # Page Up
            self.canvas.yview_scroll(-10, "units")
        elif event.keysym == "Next":   # Page Down
            self.canvas.yview_scroll(10, "units")
    
    @property
    def frame(self):
        """Devuelve el marco interno para agregar widgets."""
        return self.scrollable_frame