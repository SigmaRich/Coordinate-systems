import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from transforms6 import convert6, propagate_uncertainty


# Системы координат и подписи
systems = ["МПСК", "ССК", "ССССК", "БСК"]
labels6 = {
    "МПСК":  ["x (м)",    "y (м)",    "z (м)",    "vx (м/с)",   "vy (м/с)",   "vz (м/с)"],
    "ССК":   ["R (м)",    "α (°)",    "β (°)",    "vR (м/с)",    "vα (°/с)",    "vβ (°/с)"],
    "ССССК": ["R (м)",    "αC (°)",   "β (°)",    "vR (м/с)",    "vα (°/с)",    "vβ (°/с)"],
    "БСК":   ["R (м)",    "ε (°)",    "θ (°)",    "vR (м/с)",    "vε (°/с)",    "vθ (°/с)"],
}

# Параметры станций: геодезические φ, λ (°) и высота h (м)
stations = {
    "Печора":     {'geo': (68.3075, 54.416667, 0.0), 'A': np.deg2rad(10), 'beta0': np.deg2rad(5)},
    "Оленегорск": {'geo': (68.114167,33.910278, 0.0), 'A': np.deg2rad(20), 'beta0': np.deg2rad(4)},
    "Лехтуси":    {'geo': (60.286667,30.561389, 0.0), 'A': np.deg2rad(30), 'beta0': np.deg2rad(6)},
    "Армавир":    {'geo': (44.925278,40.983889, 0.0), 'A': np.deg2rad(40), 'beta0': np.deg2rad(7)},
    "Барнаул":    {'geo': (53.347222,83.778333, 0.0), 'A': np.deg2rad(50), 'beta0': np.deg2rad(8)},
}

class CoordConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("6D конвертер + необязательные погрешности")
        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # Исходная и целевая системы
        ttk.Label(frm, text="Из:").grid(row=0, column=0, sticky="e")
        self.src_cb = ttk.Combobox(frm, values=systems, state="readonly")
        self.src_cb.current(0); self.src_cb.grid(row=0, column=1, sticky="ew")

        ttk.Label(frm, text="В:").grid(row=1, column=0, sticky="e")
        self.dst_cb = ttk.Combobox(frm, values=systems, state="readonly")
        self.dst_cb.current(1); self.dst_cb.grid(row=1, column=1, sticky="ew")

        # Станция наблюдения
        ttk.Label(frm, text="Станция:").grid(row=2, column=0, sticky="e")
        self.st_cb = ttk.Combobox(frm, values=list(stations), state="readonly")
        self.st_cb.current(0); self.st_cb.grid(row=2, column=1, sticky="ew", pady=(0,5))

        # Поля ввода значений и необязательных погрешностей
        self.val_entries = []
        self.err_entries = []
        for i in range(6):
            ttk.Label(frm, text=labels6[systems[0]][i] + ":").grid(row=3+i, column=0, sticky="e", padx=5)
            ve = ttk.Entry(frm); ve.grid(row=3+i, column=1, sticky="ew"); self.val_entries.append(ve)
            ttk.Label(frm, text="σ (опц.):").grid(row=3+i, column=2, sticky="e")
            ee = ttk.Entry(frm); ee.grid(row=3+i, column=3, sticky="ew"); self.err_entries.append(ee)

        # Кнопка и область результата
        btn = ttk.Button(frm, text="Конвертировать", command=self.on_convert)
        btn.grid(row=9, column=0, columnspan=4, pady=10)
        self.res = tk.StringVar()
        ttk.Label(frm, textvariable=self.res, foreground="blue").grid(row=10, column=0, columnspan=4)

        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(3, weight=1)
        self.src_cb.bind("<<ComboboxSelected>>", self._update_labels)

    def _update_labels(self, *_):
        sys = self.src_cb.get()
        for i, lab in enumerate(labels6[sys]):
            frm = self.val_entries[i].master
            frm.grid_slaves(row=3+i, column=0)[0].config(text=lab + ":")

    def on_convert(self):
        try:
            # Считываем значения; пустые поля ошибок считаем σ=0
            vals = []
            errs = []
            for ve, ee in zip(self.val_entries, self.err_entries):
                v = ve.get().strip()
                if not v:
                    raise ValueError("Все 6 значений обязательны")
                vals.append(float(v))
                e = ee.get().strip()
                errs.append(float(e) if e else 0.0)
            params = stations[self.st_cb.get()]
        except Exception as ex:
            messagebox.showerror("Ошибка ввода", str(ex))
            return

        src, dst = self.src_cb.get(), self.dst_cb.get()
        out = convert6(vals, src, dst, station_params=params)

        # Если хотя бы одна σ_in > 0, считаем σ_out, иначе просто выводим значения
        if any(errs):
            sigma_out = propagate_uncertainty(vals, src, dst, params, errs)
            parts = [f"{n}={v:.3f}±{s:.3f}"
                     for n, v, s in zip(labels6[dst], out, sigma_out)]
        else:
            parts = [f"{n}={v:.3f}"
                     for n, v in zip(labels6[dst], out)]

        self.res.set("; ".join(parts))

if __name__ == "__main__":
    CoordConverterApp().mainloop()
