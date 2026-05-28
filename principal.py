# principal.py
import tkinter as tk
from cliente_ui import AplicacionTransporte

def iniciar_programa():
    print("[Sistema] Iniciando aplicacion de escritorio...")
    
    # Levantar ventana raiz de Tkinter
    root = tk.Tk()
    
    # Cargar la aplicacion principal
    AplicacionTransporte(root)
    
    # Mantener el programa abierto
    root.mainloop()

if __name__ == "__main__":
    iniciar_programa()
