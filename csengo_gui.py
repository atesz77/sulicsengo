import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog

from osztalyok import csengo_json

with open("csengo_config.json", "r") as file:
    tartalom = file.read()
    konfiguracio = csengo_json.CsengoKonfiguracio.model_validate_json(tartalom)

# visual constants
ROW_HEIGHT = 32
MAX_VISIBLE_ROWS = 15

# Build list of times every 5 minutes from 07:00 to next day 06:55
TIME_OPTIONS = [f"{((7*60 + i)//60)%24:02d}:{((7*60 + i)%60):02d}" for i in range(0, 24*60, 5)]

root = tk.Tk()

# Make window open maximized to fill the screen and allow resizing
root.update_idletasks()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
root.geometry(f"{screen_w}x{screen_h}+0+0")

# Fonts (larger for labels/buttons; keep Entry default)
# Scale fonts based on screen height so small displays get readable fonts
font_base = max(12, min(24, screen_h // 40))
label_font = tkfont.Font(size=font_base)
button_font = tkfont.Font(size=max(11, font_base - 2))

# Determine the Entry (textbox) default font to match for combobox
_tmp_entry = tk.Entry(root)
entry_font = tkfont.nametofont(_tmp_entry.cget("font"))
_tmp_entry.destroy()

# Create a ttk style so combobox matches Entry exactly
style = ttk.Style()
style.configure("Entry.TCombobox", font=entry_font, padding=(4, 4, 4, 4))

# Header frame (controls)
header = tk.Frame(root)
header.grid(row=0, column=0, sticky="nsew")

# Scrollable content area for rows
content_frame = tk.Frame(root)
content_frame.grid(row=1, column=0, sticky="nsew")

canvas = tk.Canvas(content_frame, height=ROW_HEIGHT * MAX_VISIBLE_ROWS, bd=0, highlightthickness=0, relief="flat")
# Make scrollbar touch-friendly: width scales with screen size (min 18px)
sb_width = max(18, screen_w // 40)
vsb = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview, width=sb_width)
canvas.configure(yscrollcommand=vsb.set)
vsb.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

rows_frame = tk.Frame(canvas)
canvas_window = canvas.create_window((0, 0), window=rows_frame, anchor="nw")

def _on_frame_config(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

def _on_canvas_config(event):
    # Resize the internal window to match canvas width so rows fill full width
    canvas.itemconfigure(canvas_window, width=event.width)

rows_frame.bind("<Configure>", _on_frame_config)
canvas.bind("<Configure>", _on_canvas_config)

def choose_file(var):
    path = filedialog.askopenfilename()
    if path:
        var.set(path)

# Touch / drag scrolling: allow dragging inside the canvas to scroll vertically
drag_data = {"y": 0}

def _start_drag(event):
    drag_data["y"] = event.y

def _do_drag(event):
    dy = event.y - drag_data["y"]
    # scroll by pixels converted to units; negative because dragging up should scroll down
    canvas.yview_scroll(int(-dy/ROW_HEIGHT), "units")
    drag_data["y"] = event.y

def _stop_drag(event):
    drag_data["y"] = 0

canvas.bind("<ButtonPress-1>", _start_drag)
canvas.bind("<B1-Motion>", _do_drag)
canvas.bind("<ButtonRelease-1>", _stop_drag)

alapZene_var = tk.StringVar(value=konfiguracio.alapZene)
ido_vars = []
zene_vars = []

def insert_new_row():
    last_row = rows_frame.grid_size()[1]

    ido_label = tk.Label(rows_frame, text="Időpont:", font=label_font)
    ido_vars.append(tk.StringVar())
    ido_entry = ttk.Combobox(rows_frame, values=TIME_OPTIONS, textvariable=ido_vars[-1], state="readonly", style="Entry.TCombobox")
    zene_label = tk.Label(rows_frame, text="Zene:", font=label_font)
    # create Entry + Browse button inside a container so it fits in the same grid cell
    zene_vars.append(tk.StringVar())
    zene_container = tk.Frame(rows_frame)
    zene_entry = tk.Entry(zene_container, textvariable=zene_vars[-1])
    zene_entry.pack(side="left", fill="x", expand=True)
    zene_browse = tk.Button(zene_container, text="...", command=lambda v=zene_vars[-1]: choose_file(v))
    zene_browse.pack(side="right")

    ido_label.grid(row=last_row, column=0, sticky="nsew", padx=4, pady=4)
    ido_entry.grid(row=last_row, column=1, sticky="nsew", padx=4, pady=4)
    zene_label.grid(row=last_row, column=2, sticky="nsew", padx=4, pady=4)
    zene_container.grid(row=last_row, column=3, sticky="nsew", padx=4, pady=4)

    # Make columns expand — give more weight to entry columns so they take most space
    rows_frame.grid_columnconfigure(0, weight=1)
    rows_frame.grid_columnconfigure(1, weight=3)
    rows_frame.grid_columnconfigure(2, weight=1)
    rows_frame.grid_columnconfigure(3, weight=5)

def mentes():
    ujkonfiguracio = csengo_json.CsengoKonfiguracio(idopontok=[], alapZene=alapZene_var.get())
    for ido_var, zene_var in zip(ido_vars, zene_vars):
        if ido_var.get():  # only include rows where time is set
            idop = csengo_json.CsengoIdopont(idopont=ido_var.get(), \
                zene=zene_var.get() if zene_var.get() else None)
            ujkonfiguracio.idopontok.append(idop)

    print(ujkonfiguracio)
    with open("csengo_config.json", "w") as file:
        file.write(ujkonfiguracio.model_dump_json(indent=4, ensure_ascii=False))

    tk.messagebox.showinfo("Siker", "A konfiguráció mentése sikeres!")


# Header widgets
alapZene_label = tk.Label(header, text="Alap zene:", font=label_font)
alapZene_label.grid(row=0, column=0, sticky="w", padx=6, pady=6)

# Replace single Entry with Entry + Browse button for file selection
alap_frame = tk.Frame(header)
alap_frame.grid(row=0, column=1, sticky="ew", padx=6, pady=6)
alapZene_entry = tk.Entry(alap_frame, textvariable=alapZene_var)
alapZene_entry.pack(side="left", fill="x", expand=True)
alap_browse = tk.Button(alap_frame, text="Browse", command=lambda: choose_file(alapZene_var))
alap_browse.pack(side="right", padx=(6,0))

mentes_button = tk.Button(header, text="Mentés", font=button_font, command=mentes)
mentes_button.grid(row=0, column=2, sticky="e", padx=6, pady=6)

csengRend_label = tk.Label(header, text="Csengetési rend:", font=label_font)
csengRend_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=6, pady=6)

add_button = tk.Button(header, text="Hozzáadás", command=insert_new_row, font=button_font)
add_button.grid(row=1, column=2, sticky="e", padx=6, pady=6)

# Layout weights so header and content expand properly
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
header.grid_columnconfigure(1, weight=1)

for idopont in konfiguracio.idopontok:
    insert_new_row()
    ido_vars[-1].set(idopont.idopont)
    zene_vars[-1].set(idopont.zene if idopont.zene else "")

root.mainloop()