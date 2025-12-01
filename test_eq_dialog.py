import tkinter as tk
from tkinter import ttk

# Simple test of the equalizer dialog
root = tk.Tk()
root.withdraw()

dialog = tk.Toplevel(root)
dialog.title("Test Dialog")
dialog.geometry("700x450")
dialog.configure(bg="#1e1e1e")

# Main container
main_container = tk.Frame(dialog, bg="#1e1e1e")
main_container.pack(fill="both", expand=True, padx=20, pady=20)

# Title
title = tk.Label(main_container, text="10-Band Graphic Equalizer", 
                font=("Segoe UI", 14, "bold"), bg="#1e1e1e", fg="#ffffff")
title.pack(pady=(0, 15))

# Sliders container
sliders_outer = tk.Frame(main_container, bg="#333333", bd=1, relief="solid")
sliders_outer.pack(pady=(0, 20), fill="both", expand=True)

sliders_frame = tk.Frame(sliders_outer, bg="#1e1e1e")
sliders_frame.pack(padx=10, pady=10, fill="both", expand=True)

# Create 10 test sliders
BANDS = [31, 62, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]

for i, freq in enumerate(BANDS):
    container = tk.Frame(sliders_frame, bg="#1e1e1e")
    container.grid(row=0, column=i, padx=8, pady=5, sticky="n")
    
    # Value label
    val_label = tk.Label(container, text="+0.0", 
                        font=("Segoe UI", 9, "bold"), bg="#1e1e1e", fg="#4cc2ff",
                        width=5)
    val_label.pack(pady=(0, 2))
    
    # Slider
    slider = tk.Scale(container, from_=12, to=-12, resolution=0.5,
                    orient="vertical", length=200, width=25,
                    bg="#1e1e1e", fg="#4cc2ff", 
                    troughcolor="#333333",
                    activebackground="#4cc2ff",
                    highlightthickness=0, bd=0, 
                    showvalue=0)
    slider.set(0)
    slider.pack(pady=2)
    
    # Frequency label
    freq_text = f"{freq}Hz" if freq < 1000 else f"{freq//1000}k"
    tk.Label(container, text=freq_text, font=("Segoe UI", 8), 
            bg="#1e1e1e", fg="#ffffff").pack(pady=(2, 0))

# Buttons
button_frame = tk.Frame(main_container, bg="#1e1e1e")
button_frame.pack(pady=(0, 0))

tk.Button(button_frame, text="Close", command=dialog.destroy,
         bg="#4cc2ff", fg="#000000", relief="flat", padx=20, pady=8,
         font=("Segoe UI", 10, "bold")).pack()

# Center dialog
dialog.update_idletasks()
x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
dialog.geometry(f"+{x}+{y}")

dialog.mainloop()
