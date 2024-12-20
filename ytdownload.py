import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import re
from PIL import Image, ImageTk

# Función para actualizar la barra de progreso y la velocidad de descarga
def actualizar_progreso(progreso, velocidad):
    progress_bar['value'] = progreso
    label_velocidad.config(text=f"Download speed: {velocidad}")
    ventana.update_idletasks()


# Función para descargar un solo video y actualizar la barra de progreso
def descargar_video(url, ruta_descarga, calidad):
    try:
        # Comando para ejecutar yt-dlp con el formato adecuado según la calidad seleccionada
        if calidad == "Audio only":
            # Descargar solo el audio y convertir a MP3
            comando = ['yt-dlp', '-f', 'bestaudio', '--extract-audio', '--audio-format', 'mp3', 
                       '--audio-quality', '0', '--newline', '-o', f'{ruta_descarga}/%(title)s.%(ext)s', url]
        else:
            # Descargar video en la mejor calidad posible y convertir a MP4
            if calidad == "Low quality (360p)":
                formato = "bestvideo[height<=360]+bestaudio"
            elif calidad == "Medium quality (720p)":
                formato = "bestvideo[height<=720]+bestaudio"
            else:  # Máxima resolución
                formato = "bestvideo+bestaudio"
            
            comando = ['yt-dlp', '-f', formato, '--merge-output-format', 'mp4', 
                       '--newline', '-o', f'{ruta_descarga}/%(title)s.%(ext)s', url]
        
        proceso = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        for linea in proceso.stdout:
            if "Downloading" in linea:
                progress_bar['value'] = 0
                label_velocidad.config(text="Download speed: 0 B/s")
                ventana.update_idletasks()
            elif "%" in linea:
                # Extrae el porcentaje y la velocidad de la línea de salida de yt-dlp
                try:
                    progreso = float(linea.split('%')[0].strip().split()[-1])
                    
                    # Buscar la velocidad usando una expresión regular
                    match_velocidad = re.search(r'[\d\.]+[KMG]iB/s', linea)
                    if match_velocidad:
                        velocidad = match_velocidad.group(0)
                    else:
                        velocidad = "0 B/s"
                    
                    actualizar_progreso(progreso, velocidad)
                except Exception as e:
                    print(f"Error analyzing line: {linea}. Error: {e}")
        
        proceso.wait()
        actualizar_progreso(100, "0 B/s")
        return True  # Indica que la descarga fue exitosa
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return False  # Indica que hubo un error

# Función para manejar la descarga de la lista de videos
def descargar_lista_videos():
    urls = text_urls.get("1.0", tk.END).strip().splitlines()  # Obtener todas las URLs de la lista
    ruta_descarga = entry_ruta.get()
    calidad = calidad_var.get()  # Obtener la calidad seleccionada

    if not urls:
        messagebox.showerror("Error", "Please introduce a YouTube URL.")
        return

    if not ruta_descarga:
        messagebox.showerror("Error", "Please introduce a download route.")
        return

    # Descargar cada video en la lista de URLs
    for idx, url in enumerate(urls, 1):
        label_status.config(text=f"Downloading {idx} of {len(urls)} in {calidad}...")
        descargado = descargar_video(url, ruta_descarga, calidad)
        if descargado:
            label_status.config(text=f"Video {idx} downloaded succesfully.")
        else:
            label_status.config(text=f"Error downloading the video {idx}.")
    
    label_status.config(text="Downloading completed.")

# Función para seleccionar la ruta de descarga
def seleccionar_ruta():
    ruta = filedialog.askdirectory()
    if ruta:
        entry_ruta.delete(0, tk.END)
        entry_ruta.insert(0, ruta)

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Youtube video downloader")
ventana.geometry("500x500")
ventana.minsize(600, 600)  # Establecer el tamaño mínimo de la ventana

# Etiqueta y campo para ingresar las URLs de videos
label_urls = tk.Label(ventana, text="Introduce the YouTube URL (one per line):")
label_urls.pack(pady=10)

text_urls = tk.Text(ventana, height=10, width=50)
text_urls.pack(pady=5)

# Etiqueta y campo para ingresar la ruta de descarga
label_ruta = tk.Label(ventana, text="Select a download route:")
label_ruta.pack(pady=10)

frame_ruta = tk.Frame(ventana)
frame_ruta.pack(pady=5)

entry_ruta = tk.Entry(frame_ruta, width=40)
entry_ruta.pack(side=tk.LEFT)

boton_seleccionar_ruta = tk.Button(frame_ruta, text="Select", command=seleccionar_ruta)
boton_seleccionar_ruta.pack(side=tk.LEFT, padx=5)

# Menú desplegable para seleccionar la calidad de descarga
label_calidad = tk.Label(ventana, text="Select donwload quality:")
label_calidad.pack(pady=10)

calidad_var = tk.StringVar(value="Max quality")
opciones_calidad = ["Audio only", "Low quality (360p)", "Mid quality (720p)", "Max quality"]
menu_calidad = ttk.Combobox(ventana, textvariable=calidad_var, values=opciones_calidad)
menu_calidad.pack(pady=5)

# Barra de progreso
progress_bar = ttk.Progressbar(ventana, orient='horizontal', length=300, mode='determinate')
progress_bar.pack(pady=20)

# Etiqueta para mostrar la velocidad de descarga
label_velocidad = tk.Label(ventana, text="Download speed: 0 B/s")
label_velocidad.pack(pady=5)

# Etiqueta para mostrar el estado de la descarga
label_status = tk.Label(ventana, text="State: Waiting for start...")
label_status.pack(pady=5)

# Botón para descargar la lista de videos
boton_descargar = tk.Button(ventana, text="Download video list", command=lambda: threading.Thread(target=descargar_lista_videos).start())
boton_descargar.pack(pady=10)

# Iniciar el loop principal de la ventana
ventana.mainloop()
