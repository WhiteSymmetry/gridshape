```markdown
# gridshape

**GridShape** – A Python module for drawing geometric shapes on a cell‑matrix with high‑resolution subgrid support, statistical analysis, and rich visualisation.

**GridShape** – Bir hücre matrisi üzerine geometrik şekiller çizmek için yüksek çözünürlüklü alt‑ızgara desteği, istatistiksel analiz ve zengin görselleştirme sunan Python modülü.

---

## Features / Özellikler

- Draw shapes: **rectangle, circle, triangle, diamond, polygon**  
  Şekil çizimi: **dikdörtgen, daire, üçgen, elmas, çokgen**
- **Cumulative / single shape mode** – add multiple shapes or replace  
  **Birikimli / tek şekil modu** – çoklu şekil ekle veya değiştir
- **Subgrid mode** – up to 1/2304 cell resolution (48×48 pixels per cell)  
  **Altızgara modu** – hücre başına 48×48 piksel ile 1/2304 çözünürlüğe kadar
- **Rotation** – rotate the last shape in subgrid mode  
  **Döndürme** – altızgara modunda son şekli döndür
- **Advanced statistics** – sum, mean, standard deviation, min, max, median for shape cells, background, and whole matrix  
  **Gelişmiş istatistikler** – şekil, arka plan ve tüm matris için toplam, ortalama, standart sapma, min, max, medyan
- **Export** – CSV data and formatted text report  
  **Dışa aktarma** – CSV verisi ve biçimlendirilmiş metin raporu
- **Visualisation** – custom colour map, grid lines, cell numbers, axis ticks  
  **Görselleştirme** – özel renk haritası, ızgara çizgileri, hücre numaraları, eksen işaretleri
- **Interactive console menu** – easy to use without coding  
  **Etkileşimli konsol menüsü** – kod yazmadan kolay kullanım

---

## Installation / Kurulum

The module is a single Python file. No external dependencies except **matplotlib** and **numpy**.

Modül tek bir Python dosyasıdır. **matplotlib** ve **numpy** dışında harici bağımlılığı yoktur.

```bash
pip install gridshape
```

Place `gridshape.py` in your project folder or Python path.

`gridshape.py` dosyasını proje klasörünüze veya Python yoluna koyun.

---

## Usage / Kullanım

```bash

from gridshape import GridShape
import matplotlib.pyplot as plt

g = GridShape(outer_size=10)
g.generate_shape('square', {'row': 5, 'col': 5, 'h': 3, 'w': 3})
g.visualize()
plt.show()

```

Run the interactive menu:

Etkileşimli menüyü başlatın:

```bash

from gridshape import GridShape

# Interaktif menüyü başlatmak için:
GridShape.run_interactive()

```

### Basic workflow / Temel iş akışı

1. Set matrix size (e.g. 10×10)  
   Matris boyutunu ayarlayın (ör. 10×10)

2. Choose background colour  
   Arka plan rengini seçin

3. Select shape type (1‑5) and enter parameters  
   Şekil tipini (1‑5) seçin ve parametreleri girin

4. View the cell matrix, statistics, and plot  
   Hücre matrisini, istatistikleri ve çizimi görüntüleyin

5. Switch to **subgrid mode** (`S`) for higher precision  
   Daha yüksek hassasiyet için **altızgara moduna** (`S`) geçin

6. Rotate the last shape (`7`) – subgrid only  
   Son şekli döndürün (`7`) – sadece altızgara modunda

7. Export data automatically (CSV + TXT report)  
   Veriler otomatik dışa aktarılır (CSV + TXT rapor)

---

## Class Reference / Sınıf Referansı

### `GridShape(outer_size=10, sub_res=48)`

- **outer_size** – number of cells per row/column (default 10)  
  satır/sütun başına hücre sayısı
- **sub_res** – sub‑divisions per cell (default 48 → 2304 sub‑cells)  
  hücre başına alt bölüm sayısı

### Main methods / Ana metotlar

| Method | Description / Açıklama |
|--------|------------------------|
| `create_shape(shape_type, params)` | adds a shape to the history / şekli geçmişe ekler |
| `rotate_last_shape(angle, center_row, center_col)` | rotates last shape (subgrid only) / son şekli döndürür (sadece altızgara) |
| `get_advanced_stats()` | returns detailed statistics / detaylı istatistik döndürür |
| `export_data(stats)` | saves CSV and report files / CSV ve rapor dosyalarını kaydeder |
| `visualize(show_nums, show_grid, show_ticks)` | displays the plot / grafiği gösterir |

### Shape parameters / Şekil parametreleri

| Shape | Required parameters / Gerekli parametreler |
|-------|--------------------------------------------|
| Rectangle | `row, col, h, w` |
| Circle | `row, col, radius` |
| Triangle | `row, col, size` |
| Diamond | `row, col, size` |
| Polygon | `coords` (list of `(row, col)` tuples) |

All positions are **1‑indexed** (row 1..N, column 1..N).

Tüm konumlar **1‑tabanlıdır** (satır 1..N, sütun 1..N).

---

## Output Files / Çıktı Dosyaları

- `matris_data.csv` – each matrix cell (row, column, value, inside_shape)  
  her matris hücresi (satır, sütun, değer, şekil içinde mi)
- `matris_raporu.txt` – full statistical report with a visual matrix  
  tam istatistik raporu ve görsel matris
- `grid_YYYYMMDD_HHMMSS.png` – saved plot (user requested)  
  kaydedilmiş grafik (kullanıcı istediğinde)

---

## Example / Örnek

Draw a 4×4 square at position (4,4) and rotate it 45° around cell (5,5):

(4,4) konumunda 4×4 bir kare çizin ve (5,5) hücresi etrafında 45° döndürün:

```bash
Matris Boyutu: 10
Arka Plan: 1
Subgrid aç (S)
Şekil 1 (Kare) → row=4, col=4, h=4, w=4
Şekil 7 (Döndür) → center row=5, col=5, angle=45
```

The resulting shape will be a diamond covering about 31 cells.

Sonuç şekil yaklaşık 31 hücre kaplayan bir elmas olacaktır.

---

## License / Lisans

AGPL3.0-or-later License

---

## Author / Yazar

Developed for educational and simulation purposes.  
Eğitim ve simülasyon amaçlı geliştirilmiştir.

```
