import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector

# -------- CONFIG --------
RAW_PATH = "/home/roberto/Documents/juan/temp2/imagen/test1.raw"   # salida de: dji_irp -a measure --measurefmt 1
W, H = 640, 512              # según tu log: 640x512
ENDIAN = "little"            # casi siempre little-endian en x86

# Rango físico esperado (ajusta a tu escena)
VALID_MIN, VALID_MAX = 0.0, 120.0

# Rango de visualización (solo para ver bonito; no altera datos)
VMIN, VMAX = 20.0, 80.0

# -------- LOAD RAW FLOAT32 TEMP MAP (°C) --------
dtype = np.dtype("<f4") if ENDIAN == "little" else np.dtype(">f4")
data = np.fromfile(RAW_PATH, dtype=dtype)

expected = W * H
if data.size != expected:
    raise ValueError(
        f"El raw no tiene el tamaño esperado. "
        f"Leí {data.size} floats, esperaba {expected} ({W}x{H}). "
        f"Revisa que realmente sea --measurefmt 1 y la resolución."
    )

temp_map = data.reshape((H, W))  # temp_map[y, x] en °C

temp_clean = temp_map.copy()
temp_clean[~np.isfinite(temp_clean)] = np.nan
temp_clean[(temp_clean < VALID_MIN) | (temp_clean > VALID_MAX)] = np.nan

# Min/Max "reales" (sobre valores válidos)
tmin = float(np.nanmin(temp_clean))
tmax = float(np.nanmax(temp_clean))
print(f"Temp válida: min={tmin:.2f}°C max={tmax:.2f}°C")

# Rango de visualización robusto (percentiles)
p1, p99 = np.nanpercentile(temp_clean, [1, 99])
VMIN, VMAX = float(p1), float(p99)

# Opcional: añade un margen pequeño para que no quede tan "apretado"
margin = 0.5
VMIN -= margin
VMAX += margin

# -------- ROI callback --------
defined_roi = {}

def clean_roi(roi: np.ndarray) -> np.ndarray:
    """Filtra NaN/Inf y valores fuera del rango físico."""
    roi = roi.astype(np.float32, copy=True)
    roi[~np.isfinite(roi)] = np.nan
    roi[(roi < VALID_MIN) | (roi > VALID_MAX)] = np.nan
    return roi

def onselect(eclick, erelease):
    if eclick.xdata is None or erelease.xdata is None:
        return

    x1, y1 = int(eclick.xdata), int(eclick.ydata)
    x2, y2 = int(erelease.xdata), int(erelease.ydata)

    x0, x1 = sorted([x1, x2])
    y0, y1 = sorted([y1, y2])

    # Asegurar límites
    x0 = max(0, min(W - 1, x0))
    x1 = max(0, min(W, x1))
    y0 = max(0, min(H - 1, y0))
    y1 = max(0, min(H, y1))

    roi = temp_map[y0:y1, x0:x1]
    roi_clean = clean_roi(roi)

    defined_roi["data"] = roi_clean

    n_valid = np.isfinite(roi_clean).sum()
    if n_valid == 0:
        mean_temp = np.nan
        min_temp = np.nan
        max_temp = np.nan
        min_pos = max_pos = None
    else:
        mean_temp = float(np.nanmean(roi_clean))
        min_temp = float(np.nanmin(roi_clean))
        max_temp = float(np.nanmax(roi_clean))

        # ---- posiciones locales dentro del ROI ----
        min_idx = np.nanargmin(roi_clean)
        max_idx = np.nanargmax(roi_clean)

        min_ry, min_rx = np.unravel_index(min_idx, roi_clean.shape)
        max_ry, max_rx = np.unravel_index(max_idx, roi_clean.shape)

        # ---- convertir a coordenadas globales ----
        min_pos = (x0 + min_rx, y0 + min_ry)
        max_pos = (x0 + max_rx, y0 + max_ry)

    # ---- Visualización ----
    fig, ax = plt.subplots()
    im = ax.imshow(temp_map, cmap="plasma", vmin=VMIN, vmax=VMAX)
    plt.colorbar(im, ax=ax, label="Temperature (°C)")

    # ROI rectangle
    ax.add_patch(
        plt.Rectangle(
            (x0, y0), x1 - x0, y1 - y0,
            edgecolor="cyan", facecolor="none", linewidth=2
        )
    )

    # Puntos min / max
    if min_pos is not None:
        ax.plot(min_pos[0], min_pos[1], 'bo', markersize=8, label="Min")

    if max_pos is not None:
        ax.plot(max_pos[0], max_pos[1], 'ro', markersize=8, label="Max")

    ax.set_title(
        f"ROI | mean={mean_temp:.2f}°C  "
        f"min={min_temp:.2f}°C  max={max_temp:.2f}°C  "
        f"valid={n_valid}/{roi_clean.size}"
    )

    ax.legend(loc="upper right")
    ax.axis("off")
    plt.show()

# -------- Interactive ROI selection --------
fig, ax = plt.subplots()
ax.imshow(temp_map, cmap="plasma", vmin=VMIN, vmax=VMAX)
plt.title("Draw ROI to Analyze Temperature (raw float32)")
plt.axis("off")

selector = RectangleSelector(
    ax, onselect,
    useblit=True,
    button=[1],
    minspanx=5, minspany=5,
    spancoords="pixels",
    interactive=True
)

plt.show()