import pymem
import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk
from datetime import datetime
import os

# VARIABLES DE ASIGNAMIENTO DE PROCESO/MEMORIA/DIRECCIÓN
Process = "hollow_knight.exe"

#Coloque aqui la direccion de memoria
#Ejemplo: MemoryPath = 0x1EE899C3190
MemoryPath = None

log_path = os.path.join(os.path.dirname(__file__), 'log.txt')


try:
    ProcessMemory = pymem.Pymem(Process)
except pymem.exception.ProcessNotFound:
    print(f"Error: No se encontró el proceso {Process}. Asegúrate de que está en ejecución.")
    exit()


if not os.path.exists(log_path):
    print(f"No se encontró el archivo de log en {log_path}, iniciando desde 0.")


# VARIABLES PARA LA LÓGICA
LogPath = open(log_path, 'a+')
LogPath.seek(0)
LogContent = LogPath.read()
HitCount = 0
Counter = None
LastLife = None

# INTERFAZ GRÁFICA
Window = tk.Tk()
Window.attributes("-topmost", 1)
Window.config(bg='black')


# Registrar la fuente OTF personalizada
font_path = os.path.join(os.path.dirname(__file__), 'Fuente.otf')

# Usamos el método tkFont.Font para registrar la fuente OTF personalizada (requiere instalación previa)
try:
    window_font = tkFont.Font(family="MiFuente", size=30, weight="bold")  # Cambia "MiFuente" por el nombre de la fuente instalada
except tk.TclError:
    print("Error: No se pudo cargar la fuente OTF. Verifica que la fuente esté instalada.")
    window_font = tkFont.Font(family="Arial", size=30, weight="bold")  # Fuente alternativa en caso de error


# transparencia
Window.attributes("-transparentcolor", "black")
Window.overrideredirect(True)

# Canvas
canvas = tk.Canvas(Window, bg="black", bd=0, highlightthickness=0)
canvas.pack(padx=10, pady=10, fill="both", expand=True)

# Usar ruta relativa para la imagen
img_path = os.path.join(os.path.dirname(__file__), 'DeathCounter.png')

try:
    img = Image.open(img_path)
    image = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, anchor="nw", image=image)
except FileNotFoundError:
    print(f"Error: No se encontró el archivo {img_path}.")
    exit()

# Texto con la fuente personalizada
BaseText = canvas.create_text(
    img.width // 2, img.height // 2.5,
    text="0", font=window_font, fill="#8B0000", anchor="center"
)

# FUNCIÓN PARA INICIAR
def Start():
    global Counter
    if LogContent:
        blocks = LogContent.split('========================\n')
        for block in reversed(blocks):
            lines = block.splitlines()
            for line in lines:
                if "Numero de Muertes: " in line:
                    try:
                        Counter = int(line.split("Numero de Muertes: ")[1].strip())
                        canvas.itemconfig(BaseText, text=str(Counter))
                        print("Logs vinculados! " + str(Counter))
                        return
                    except ValueError:
                        print("Error al interpretar los registros previos.")
                        continue
    # Si no hay registros, inicializa en 0
    Counter = 0
    canvas.itemconfig(BaseText, text=str(Counter))
    print("No se encontraron los registros, empezando desde 0.")

# FUNCIÓN PARA MONITOREAR LA VIDA
def MonitorLife():
    global LastLife, Counter
    try:
        CurrentLife = ProcessMemory.read_int(MemoryPath)
    except pymem.exception.MemoryReadError as e:
        print(f"Error al leer la memoria: {e}")
        CurrentLife = LastLife  # Usa el último valor conocido

    if LastLife is None:
        LastLife = CurrentLife

    if CurrentLife < LastLife:  # Detecta pérdida de vida
        Counter += 1
        canvas.itemconfig(BaseText, text=str(Counter))
    LastLife = CurrentLife
    
    Window.after(100, MonitorLife)

# FUNCIONES PARA MOVER LA VENTANA
x_offset, y_offset = 0, 0

def start_move(event):
    global x_offset, y_offset
    x_offset = event.x
    y_offset = event.y

def do_move(event):
    new_x = Window.winfo_x() + event.x - x_offset
    new_y = Window.winfo_y() + event.y - y_offset
    Window.geometry(f"+{new_x}+{new_y}")

# FUNCIONES PARA EL CONTADOR
def AddUpOneToCounter():
    global Counter
    Counter += 1
    canvas.itemconfig(BaseText, text=str(Counter))
    print(f"[+] Nueva cantidad de muertes: {Counter}")

def SubstratOneToCounter():
    global Counter
    if Counter > 0:
        Counter -= 1
    canvas.itemconfig(BaseText, text=str(Counter))
    print(f"[-] Nueva cantidad de muertes: {Counter}")

def ResetCounter():
    global Counter
    print(f"[#] Último valor: {Counter}")
    Counter = 0
    canvas.itemconfig(BaseText, text=str(Counter))
    print(f"[&] Nueva cantidad de muertes: {Counter}")

# FUNCIÓN PARA CERRAR EL PROGRAMA
def CloseCounter():
    global LogPath, Counter
    print("[*] Cerrando contador y escribiendo en el archivo...")
    LogPath.seek(0, 2)
    LogPath.write("========================\n")
    LogPath.write(f"Numero de Muertes: {Counter}\n")
    LogPath.write("Hora: " + datetime.now().strftime("%H:%M:%S") + "\n")
    LogPath.write("Fecha: " + datetime.now().strftime("%d/%m/%Y") + "\n")
    LogPath.write("========================\n\n")
    LogPath.flush()
    LogPath.close()
    exit()

# EVENTOS Y BINDS
Window.bind("0", lambda event: CloseCounter())
Window.bind("1", lambda event: ResetCounter())
Window.bind("2", lambda event: AddUpOneToCounter())
Window.bind("3", lambda event: SubstratOneToCounter())

Window.bind("<ButtonPress-1>", start_move)
Window.bind("<B1-Motion>", do_move)

# INICIA EL MONITOR Y LA INTERFAZ
Start()
MonitorLife()
Window.mainloop()