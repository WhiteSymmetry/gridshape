# gridshape (GridShape: Grid Shape)

## gridshape (GridShape: Grid Shape) <img src="https://github.com/WhiteSymmetry/WhiteSymmetry/blob/main/docs/logo.jpg" alt="gridshape (Grid Shape)" align="right" height="140"/>

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

---

Usage/Kullanım:

Matris Boyutu (ana hücre sayısı) (Varsayılan 10):  

Arka Plan Renkleri: 1:Beyaz, 2:Bulut, 3:Gümüş, 4:Kömür, 5:Açık Gri

Seçim (1-5):  4
Hücre numaraları gösterilsin mi? (E/h):  h
Izgara çizgileri gösterilsin mi? (E/h):  h
Eksen değerleri gösterilsin mi? (E/h):  h

--- MOD: TEK ŞEKİL | KLASİK ---
Kaplama: 0/100 hücre (%0.0)
[1:Kare/Dikdörtgen] [2:Daire] [3:Üçgen] [4:Elmas] [5:Çokgen] [7:Döndür (subgrid)]
[6:Çoklu/Tekli] [S:Subgrid Aç/Kapa] [8:Geri Al] [9:Temizle] [0:Çıkış]

Seçim:  S

--- MOD: TEK ŞEKİL | SUBGRID (1/2304) ---
Kaplama: 0/100 hücre (%0.0)
[1:Kare/Dikdörtgen] [2:Daire] [3:Üçgen] [4:Elmas] [5:Çokgen] [7:Döndür (subgrid)]
[6:Çoklu/Tekli] [S:Subgrid Aç/Kapa] [8:Geri Al] [9:Temizle] [0:Çıkış]

Seçim:  4
Merkez satır (Varsayılan 5):  
Merkez sütun (Varsayılan 5):  
Yarıçap (Varsayılan 2):  


--- MATRİS (ana hücreler) ---
 11  12  13  14  15  16  17  18  19  20
 21  22  23  24  25  26  27  28  29  30
 31  32  33  34 [35]  36  37  38  39  40
 41  42  43 [44] [45] [46]  47  48  49  50
 51  52 [53] [54] [55] [56] [57]  58  59  60
 61  62  63 [64] [65] [66] [67]  68  69  70
 71  72  73  74 [75] [76]  77  78  79  80
 81  82  83  84  85  86  87  88  89  90
 91  92  93  94  95  96  97  98  99 100
101 102 103 104 105 106 107 108 109 110

--- İSTATİSTİKLER ---
Şekil içi hücre sayısı: 15 (%15.0)
Toplam: 858  Ort: 57.2  Std: 11.33
Min: 35  Max: 76  Medyan: 56.0
Arka plan toplam: 5192  Ort: 61.08
Genel toplam: 6050  Ort: 60.5

Görseli kaydet? (png/jpg/pdf/svg/h):  jpg

Kaydedildi: *.jpg
<img src="[https://github.com/WhiteSymmetry/kececicurve/blob/main/docs/logo.jpg](https://github.com/WhiteSymmetry/gridshape/blob/main/example/2.jpg)" alt="gridshape" align="right" height="640"/>

--- MOD: TEK ŞEKİL | SUBGRID (1/2304) ---
Kaplama: 15/100 hücre (%15.0)
[1:Kare/Dikdörtgen] [2:Daire] [3:Üçgen] [4:Elmas] [5:Çokgen] [7:Döndür (subgrid)]
[6:Çoklu/Tekli] [S:Subgrid Aç/Kapa] [8:Geri Al] [9:Temizle] [0:Çıkış]

Seçim:  7
Döndürme merkezi satırı (Varsayılan 5):  
Döndürme merkezi sütunu (Varsayılan 5):  
Döndürme açısı (derece) (Varsayılan 45):  

Şekil 45° döndürüldü.

--- MATRİS (ana hücreler) ---
 11  12  13  14  15  16  17  18  19  20
 21  22  23  24  25  26  27  28  29  30
 31  32  33  34  35  36  37  38  39  40
 41  42  43 [44] [45] [46]  47  48  49  50
 51  52  53 [54] [55] [56]  57  58  59  60
 61  62  63 [64] [65] [66]  67  68  69  70
 71  72  73  74  75  76  77  78  79  80
 81  82  83  84  85  86  87  88  89  90
 91  92  93  94  95  96  97  98  99 100
101 102 103 104 105 106 107 108 109 110

--- İSTATİSTİKLER ---
Şekil içi hücre sayısı: 9 (%9.0)

Görseli kaydet? (png/jpg/pdf/svg/h):  jpg

Kaydedildi: *.jpg
<img src="[https://github.com/WhiteSymmetry/kececicurve/blob/main/docs/logo.jpg](https://github.com/WhiteSymmetry/gridshape/blob/main/example/1.jpg)" alt="gridshape" align="right" height="640"/>

--- MOD: TEK ŞEKİL | SUBGRID (1/2304) ---
Kaplama: 9/100 hücre (%9.0)

---
