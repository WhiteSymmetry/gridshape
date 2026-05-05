# gridshape.py
"""
gridshape - A Python module for drawing geometric shapes on a cell matrix
with high‑resolution subgrid support, statistical analysis and visualisation.

Main class: GridShape
"""

import matplotlib.pyplot as plt
import numpy as np
import math
import csv
import sys
from datetime import datetime
from matplotlib.colors import ListedColormap

class GridShape:
    def __init__(self, outer_size=10, sub_res=48):
        self.outer_size = outer_size
        self.sub_res = sub_res
        self.res_size = outer_size * sub_res
        self.cumulative_mode = False          # Varsayılan: TEK ŞEKİL
        self.subgrid_active = False
        self.shapes_history = []
        self.shape_id_map = {'square': 1, 'rectangle': 1, 'circle': 2, 'triangle': 3, 'diamond': 4, 'polygon': 5}
        self.default_colors = ['#f8f9fa', '#e63946', '#457b9d', '#2a9d8f', '#e9c46a', '#9b5de5']
        self.bg_color_map = {'1': '#ffffff', '2': '#f1f2f6', '3': '#dfe4ea', '4': '#2f3542', '5': '#ced6e0'}
        self.selected_bg = '#ffffff'
        self.reset_all()

    def reset_all(self):
        self.bg_matrix = np.zeros((self.outer_size, self.outer_size), dtype=int)
        for i in range(self.outer_size):
            for j in range(self.outer_size):
                self.bg_matrix[i, j] = (i + 1) * 10 + (j + 1)
        self._rebuild_layer()

    def _rebuild_layer(self):
        res = self.res_size if self.subgrid_active else self.outer_size
        self.layer_matrix = np.zeros((res, res), dtype=int)
        for mask in self.shapes_history:
            if mask.shape == self.layer_matrix.shape:
                self.layer_matrix[mask > 0] = mask[mask > 0]

    # ---- Klasik mod için basit algoritmalar (kullanıcının orijinali) ----
    def _generate_shape_classic(self, shape_type, params):
        mask = np.zeros((self.outer_size, self.outer_size), dtype=int)
        r = int(params.get('row', 1)) - 1
        c = int(params.get('col', 1)) - 1
        sid = self.shape_id_map.get(shape_type, 1)

        if shape_type in ['square', 'rectangle']:
            h = int(params.get('h', 3))
            w = int(params.get('w', 3))
            for i in range(r, min(r + h, self.outer_size)):
                for j in range(c, min(c + w, self.outer_size)):
                    mask[i, j] = sid
        elif shape_type == 'circle':
            rad = params.get('radius', 2.5)
            for i in range(self.outer_size):
                for j in range(self.outer_size):
                    if math.sqrt((i - r)**2 + (j - c)**2) <= rad:
                        mask[i, j] = sid
        elif shape_type == 'triangle':
            sz = int(params.get('size', 4))
            # İkizkenar dik üçgen (tepe yukarı, taban aşağı)
            for i in range(self.outer_size):
                for j in range(self.outer_size):
                    di = i - r
                    dj = j - c
                    if 0 <= di < sz and abs(dj) <= di:
                        mask[i, j] = sid
        elif shape_type == 'diamond':
            sz = int(params.get('size', 2))
            for i in range(self.outer_size):
                for j in range(self.outer_size):
                    if abs(i - r) + abs(j - c) <= sz:
                        mask[i, j] = sid
        elif shape_type == 'polygon':
            for pr, pc in params.get('coords', []):
                if 0 <= pr-1 < self.outer_size and 0 <= pc-1 < self.outer_size:
                    mask[pr-1, pc-1] = sid
        return mask

    # ---- Subgrid modu için yüksek çözünürlüklü testler (alt hücre merkezleri) ----
    def _generate_shape_subgrid(self, shape_type, params):
        mask = np.zeros((self.res_size, self.res_size), dtype=int)
        sid = self.shape_id_map.get(shape_type, 1)
        scale = self.sub_res
    
        if shape_type in ['square', 'rectangle']:
            r0 = (params.get('row', 1) - 1) * scale
            c0 = (params.get('col', 1) - 1) * scale
            h = params.get('h', 3) * scale
            w = params.get('w', 3) * scale
            for i in range(self.res_size):
                for j in range(self.res_size):
                    if r0 <= i < r0 + h and c0 <= j < c0 + w:
                        mask[i, j] = sid
    
        elif shape_type == 'circle':
            # Daire merkezi: ana hücrenin merkezi
            cy = (params.get('row', 1) - 1) * scale + scale / 2.0
            cx = (params.get('col', 1) - 1) * scale + scale / 2.0
            rad = params.get('radius', 2.5) * scale
            for i in range(self.res_size):
                for j in range(self.res_size):
                    if (i - cy) ** 2 + (j - cx) ** 2 <= rad ** 2:
                        mask[i, j] = sid
    
        elif shape_type == 'triangle':
            # Üçgen tepe noktası: ana hücrenin SOL ÜST KÖŞESİ (tam kenardan başlasın)
            r0 = (params.get('row', 1) - 1) * scale
            c0 = (params.get('col', 1) - 1) * scale
            sz = params.get('size', 4) * scale
            for i in range(self.res_size):
                for j in range(self.res_size):
                    di = i - r0
                    dj = j - c0
                    # 0 <= di < sz  ve  |dj| <= di  (piksel tabanlı, eğim 45°)
                    if 0 <= di < sz and abs(dj) <= di:
                        mask[i, j] = sid
    
        elif shape_type == 'diamond':
            # Elmas merkezi: ana hücrenin merkezi (klasik moddaki gibi)
            cy = (params.get('row', 1) - 1) * scale + scale / 2.0
            cx = (params.get('col', 1) - 1) * scale + scale / 2.0
            rad = params.get('size', 2) * scale
            for i in range(self.res_size):
                for j in range(self.res_size):
                    if abs(i - cy) + abs(j - cx) <= rad:
                        mask[i, j] = sid
    
        elif shape_type == 'polygon':
            coords = params.get('coords', [])
            if coords:
                # Çokgen köşelerini piksel koordinatlarına çevir (sol üst köşeler)
                scaled_verts = []
                for r, c in coords:
                    x = (c - 1) * scale
                    y = (r - 1) * scale
                    scaled_verts.append((x, y))
                # Ray casting ile hücre merkezlerini test et
                for i in range(self.res_size):
                    for j in range(self.res_size):
                        x = j + 0.5
                        y = i + 0.5
                        inside = False
                        n = len(scaled_verts)
                        for k in range(n):
                            x1, y1 = scaled_verts[k]
                            x2, y2 = scaled_verts[(k + 1) % n]
                            if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
                                inside = not inside
                        if inside:
                            mask[i, j] = sid
        return mask

    def generate_shape(self, shape_type, params):
        if self.subgrid_active:
            mask = self._generate_shape_subgrid(shape_type, params)
        else:
            mask = self._generate_shape_classic(shape_type, params)

        if not self.cumulative_mode:
            self.shapes_history = []
        self.shapes_history.append(mask)
        self._rebuild_layer()

    def _get_cell_level_mask(self):
        if not self.subgrid_active:
            return self.layer_matrix > 0
        cell_mask = np.zeros((self.outer_size, self.outer_size), dtype=bool)
        for i in range(self.outer_size):
            for j in range(self.outer_size):
                r0, r1 = i * self.sub_res, (i+1) * self.sub_res
                c0, c1 = j * self.sub_res, (j+1) * self.sub_res
                if np.any(self.layer_matrix[r0:r1, c0:c1] > 0):
                    cell_mask[i, j] = True
        return cell_mask

    def get_advanced_stats(self):
        shape_cell_mask = self._get_cell_level_mask()
        bg = self.bg_matrix
        shape_vals = bg[shape_cell_mask]
        bg_vals = bg[~shape_cell_mask]

        count_shape_cells = np.sum(shape_cell_mask)
        total_cells = self.outer_size ** 2
        percent = (count_shape_cells / total_cells) * 100.0

        if self.subgrid_active:
            subgrid_shape_pixels = np.sum(self.layer_matrix > 0)
            subgrid_total_pixels = self.res_size ** 2
            pixel_percent = (subgrid_shape_pixels / subgrid_total_pixels) * 100.0
        else:
            pixel_percent = percent

        stats = {
            'shape_cell_count': count_shape_cells,
            'shape_percent_cells': round(percent, 2),
            'shape_pixel_percent': round(pixel_percent, 2),
            'shape_sum': int(np.sum(shape_vals)) if shape_vals.size else 0,
            'shape_mean': round(np.mean(shape_vals), 2) if shape_vals.size else 0,
            'shape_std': round(np.std(shape_vals), 2) if shape_vals.size else 0,
            'shape_min': int(np.min(shape_vals)) if shape_vals.size else 0,
            'shape_max': int(np.max(shape_vals)) if shape_vals.size else 0,
            'shape_median': round(np.median(shape_vals), 2) if shape_vals.size else 0,
            'bg_sum': int(np.sum(bg_vals)) if bg_vals.size else 0,
            'bg_mean': round(np.mean(bg_vals), 2) if bg_vals.size else 0,
            'bg_std': round(np.std(bg_vals), 2) if bg_vals.size else 0,
            'bg_min': int(np.min(bg_vals)) if bg_vals.size else 0,
            'bg_max': int(np.max(bg_vals)) if bg_vals.size else 0,
            'bg_median': round(np.median(bg_vals), 2) if bg_vals.size else 0,
            'total_sum': int(np.sum(bg)),
            'total_mean': round(np.mean(bg), 2),
            'total_std': round(np.std(bg), 2),
        }
        return stats

    def export_data(self, stats):
        with open('matris_data.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Satır', 'Sütun', 'Değer', 'Şekil_İçinde'])
            for i in range(self.outer_size):
                for j in range(self.outer_size):
                    val = self.bg_matrix[i, j]
                    in_shape = self._get_cell_level_mask()[i, j]
                    writer.writerow([i+1, j+1, val, 'Evet' if in_shape else 'Hayır'])

        with open('matris_raporu.txt', 'w', encoding='utf-8') as f:
            f.write(f"RAPOR TARİHİ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"PYTHON SÜRÜMÜ: {sys.version.split()[0]}\n")
            f.write("--- MATRİS ANALİZ RAPORU ---\n\n")
            f.write(f"Toplam Hücre: {self.outer_size**2}\n")
            f.write(f"Şekil Hücre Sayısı: {stats['shape_cell_count']} (%{stats['shape_percent_cells']})\n")
            if self.subgrid_active:
                f.write(f"Alt piksel kaplama: %{stats['shape_pixel_percent']} (1/{self.sub_res**2} hassasiyet)\n")
            f.write("\n--- ŞEKİL İÇİ ---\n")
            f.write(f"Toplam: {stats['shape_sum']}  Ort: {stats['shape_mean']}  Std: {stats['shape_std']}\n")
            f.write(f"Min: {stats['shape_min']}  Max: {stats['shape_max']}  Medyan: {stats['shape_median']}\n")
            f.write("\n--- ARKA PLAN ---\n")
            f.write(f"Toplam: {stats['bg_sum']}  Ort: {stats['bg_mean']}  Std: {stats['bg_std']}\n")
            f.write(f"Min: {stats['bg_min']}  Max: {stats['bg_max']}  Medyan: {stats['bg_median']}\n")
            f.write("\n--- MATRİS GÖRÜNÜMÜ ---\n")
            for i in range(self.outer_size):
                row = []
                for j in range(self.outer_size):
                    val = self.bg_matrix[i, j]
                    if self._get_cell_level_mask()[i, j]:
                        row.append(f"[{val}]")
                    else:
                        row.append(f"{val:3}")
                f.write(" ".join(row) + "\n")

    def visualize(self, show_nums=True, show_grid=True, show_ticks=True):
        fig, ax = plt.subplots(figsize=(10, 10))
        colors = [self.selected_bg] + self.default_colors[1:]
        cmap = ListedColormap(colors)
        ax.imshow(self.layer_matrix, cmap=cmap, vmin=0, vmax=5,
                  extent=[0, self.outer_size, self.outer_size, 0], aspect='equal')

        # Hücre numaraları (merkezde)
        if show_nums:
            for i in range(self.outer_size):
                for j in range(self.outer_size):
                    val = (i+1)*10 + (j+1)
                    ax.text(j+0.5, i+0.5, str(val), va='center', ha='center',
                            alpha=0.3, fontweight='bold', fontsize=12, color='black')

        # Grid çizgileri: sadece iç çizgiler (1..N-1), dış çerçeve spine ile
        if show_grid:
            for k in range(1, self.outer_size):
                ax.axhline(k, color='black', lw=1.2, alpha=0.5)
                ax.axvline(k, color='black', lw=1.2, alpha=0.5)

        # Eksen düzenlemesi
        if show_ticks:
            ax.set_xticks(np.arange(0.5, self.outer_size, 1))
            ax.set_yticks(np.arange(0.5, self.outer_size, 1))
            ax.set_xticklabels(np.arange(1, self.outer_size+1))
            ax.set_yticklabels(np.arange(1, self.outer_size+1))
            ax.tick_params(axis='both', which='both', length=4)
        else:
            ax.set_xticks([])
            ax.set_yticks([])

        # Dış çerçeve (spines)
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(1.5)
            spine.set_color('black')

        stats = self.get_advanced_stats()
        now_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        py_ver = sys.version.split()[0]
        title = (f"Subgrid: {self.subgrid_active} (1/{self.sub_res**2}) | {now_str} | Python {py_ver}\n"
                 f"Şekil: {stats['shape_cell_count']} hücre (%{stats['shape_percent_cells']}) | "
                 f"Ort: {stats['shape_mean']} | Med: {stats['shape_median']}")
        ax.set_title(title, fontweight='bold')
        plt.tight_layout()
        return fig, ax

    # GridShapePro sınıfına eklenecek döndürme metodu (subgrid modunda çalışır)
    def rotate_last_shape(self, angle_deg, center_row, center_col):
        if not self.subgrid_active or not self.shapes_history:
            return False
        last_mask = self.shapes_history[-1].copy()
        h, w = last_mask.shape
        cx = (center_col - 1) * self.sub_res + self.sub_res / 2.0
        cy = (center_row - 1) * self.sub_res + self.sub_res / 2.0
        rad = np.radians(angle_deg)
        cos_t, sin_t = np.cos(rad), np.sin(rad)
        new_mask = np.zeros_like(last_mask)
    
        for i_src in range(h):
            for j_src in range(w):
                if last_mask[i_src, j_src] > 0:
                    x_src = j_src + 0.5 - cx
                    y_src = i_src + 0.5 - cy
                    x_dst = x_src * cos_t - y_src * sin_t + cx
                    y_dst = x_src * sin_t + y_src * cos_t + cy
                    j_dst = int(round(x_dst - 0.5))
                    i_dst = int(round(y_dst - 0.5))
                    if 0 <= i_dst < h and 0 <= j_dst < w:
                        new_mask[i_dst, j_dst] = last_mask[i_src, j_src]
    
        if np.count_nonzero(new_mask) == 0:
            return False
        self.shapes_history[-1] = new_mask
        self._rebuild_layer()
        return True

    @classmethod
    def run_interactive(cls):
        """İnteraktif menüyü başlatır (classmethod)."""
        def get_input(prompt, default):
            val = input(f"{prompt} (Varsayılan {default}): ").strip()
            if val == '':
                return default
            try:
                return float(val) if '.' in val else int(val)
            except ValueError:
                return default

        size = get_input("Matris Boyutu (ana hücre sayısı)", 10)
        gen = cls(outer_size=int(size), sub_res=48)

        print("\nArka Plan Renkleri: 1:Beyaz, 2:Bulut, 3:Gümüş, 4:Kömür, 5:Açık Gri")
        bg_choice = input("Seçim (1-5): ").strip() or '1'
        gen.selected_bg = gen.bg_color_map.get(bg_choice, '#ffffff')

        show_nums = input("Hücre numaraları gösterilsin mi? (E/h): ").lower() != 'h'
        show_grid = input("Izgara çizgileri gösterilsin mi? (E/h): ").lower() != 'h'
        show_ticks = input("Eksen değerleri gösterilsin mi? (E/h): ").lower() != 'h'

        while True:
            stats = gen.get_advanced_stats()
            mode_str = "ÇOKLU ŞEKİL" if gen.cumulative_mode else "TEK ŞEKİL"
            res_str = f"SUBGRID (1/{gen.sub_res**2})" if gen.subgrid_active else "KLASİK"
            print(f"\n--- MOD: {mode_str} | {res_str} ---")
            print(f"Kaplama: {stats['shape_cell_count']}/{size**2} hücre (%{stats['shape_percent_cells']})")
            print("[1:Kare/Dikdörtgen] [2:Daire] [3:Üçgen] [4:Elmas] [5:Çokgen] [7:Döndür (subgrid)]")
            print("[6:Çoklu/Tekli] [S:Subgrid Aç/Kapa] [8:Geri Al] [9:Temizle] [0:Çıkış]")
            ch = input("Seçim: ").upper()

            if ch == '0':
                break
            elif ch == '6':
                gen.cumulative_mode = not gen.cumulative_mode
                continue
            elif ch == 'S':
                gen.subgrid_active = not gen.subgrid_active
                gen.shapes_history = []
                gen.reset_all()
                continue
            elif ch == '8':
                if gen.shapes_history:
                    gen.shapes_history.pop()
                    gen._rebuild_layer()
                continue
            elif ch == '9':
                gen.shapes_history = []
                gen.reset_all()
                continue
            elif ch == '7':
                if not gen.subgrid_active:
                    print("Döndürme sadece SUBGRID modunda çalışır. Önce S ile subgrid'i açın.")
                elif not gen.shapes_history:
                    print("Döndürülecek şekil yok. Önce bir şekil çizin (1-5).")
                else:
                    row = get_input("Döndürme merkezi satırı", 5)
                    col = get_input("Döndürme merkezi sütunu", 5)
                    angle = get_input("Döndürme açısı (derece)", 45)
                    if gen.rotate_last_shape(angle, row, col):
                        print(f"Şekil {angle}° döndürüldü.")
                        stats = gen.get_advanced_stats()
                        gen.export_data(stats)
                        print("\n--- MATRİS (ana hücreler) ---")
                        for i in range(gen.outer_size):
                            row_vals = []
                            for j in range(gen.outer_size):
                                val = gen.bg_matrix[i, j]
                                if gen._get_cell_level_mask()[i, j]:
                                    row_vals.append(f"[{val}]")
                                else:
                                    row_vals.append(f"{val:3}")
                            print(" ".join(row_vals))
                        print("\n--- İSTATİSTİKLER ---")
                        print(f"Şekil içi hücre sayısı: {stats['shape_cell_count']} (%{stats['shape_percent_cells']})")
                        fig, ax = gen.visualize(show_nums, show_grid, show_ticks)
                        save = input("\nGörseli kaydet? (png/jpg/pdf/svg/h): ").lower()
                        if save in ['png','jpg','pdf','svg']:
                            fname = f"grid_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{save}"
                            plt.savefig(fname, dpi=300, bbox_inches='tight')
                            print(f"Kaydedildi: {fname}")
                        plt.show()
                    else:
                        print("Döndürme başarısız oldu.")
                continue

            params = {}
            shape_type = 'square'
            try:
                if ch == '1':
                    params = {'row': get_input("Başlangıç satırı", 2), 'col': get_input("Başlangıç sütunu", 2),
                              'h': get_input("Yükseklik", 4), 'w': get_input("Genişlik", 4)}
                    shape_type = 'rectangle'
                elif ch == '2':
                    params = {'row': get_input("Merkez satır", 5), 'col': get_input("Merkez sütun", 5),
                              'radius': get_input("Yarıçap", 2.5)}
                    shape_type = 'circle'
                elif ch == '3':
                    params = {'row': get_input("Tepe satırı", 2), 'col': get_input("Tepe sütunu", 5),
                              'size': get_input("Kenar uzunluğu", 5)}
                    shape_type = 'triangle'
                elif ch == '4':
                    params = {'row': get_input("Merkez satır", 5), 'col': get_input("Merkez sütun", 5),
                              'size': get_input("Yarıçap", 2)}
                    shape_type = 'diamond'
                elif ch == '5':
                    pts = input("Köşeler (satır,sütun) örn: 2,2 5,2 5,5 : ").strip()
                    if pts == '':
                        pts = "2,2 5,2 5,5"
                    coords = []
                    for pt in pts.split():
                        try:
                            r, c = map(int, pt.split(','))
                            coords.append((r, c))
                        except:
                            pass
                    if len(coords) < 3:
                        print("En az 3 nokta girin. Varsayılan kullanılıyor.")
                        coords = [(2,2), (5,2), (5,5)]
                    params = {'coords': coords}
                    shape_type = 'polygon'
                else:
                    print("Geçersiz seçim.")
                    continue

                gen.generate_shape(shape_type, params)
                stats = gen.get_advanced_stats()
                gen.export_data(stats)

                print("\n--- MATRİS (ana hücreler) ---")
                for i in range(size):
                    row_vals = []
                    for j in range(size):
                        val = gen.bg_matrix[i, j]
                        if gen._get_cell_level_mask()[i, j]:
                            row_vals.append(f"[{val}]")
                        else:
                            row_vals.append(f"{val:3}")
                    print(" ".join(row_vals))

                print("\n--- İSTATİSTİKLER ---")
                print(f"Şekil içi hücre sayısı: {stats['shape_cell_count']} (%{stats['shape_percent_cells']})")
                print(f"Toplam: {stats['shape_sum']}  Ort: {stats['shape_mean']}  Std: {stats['shape_std']}")
                print(f"Min: {stats['shape_min']}  Max: {stats['shape_max']}  Medyan: {stats['shape_median']}")
                print(f"Arka plan toplam: {stats['bg_sum']}  Ort: {stats['bg_mean']}")
                print(f"Genel toplam: {stats['total_sum']}  Ort: {stats['total_mean']}")

                fig, ax = gen.visualize(show_nums, show_grid, show_ticks)
                save = input("\nGörseli kaydet? (png/jpg/pdf/svg/h): ").lower()
                if save in ['png','jpg','pdf','svg']:
                    fname = f"grid_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{save}"
                    plt.savefig(fname, dpi=300, bbox_inches='tight')
                    print(f"Kaydedildi: {fname}")
                plt.show()
            except Exception as e:
                print(f"Hata: {e}. Lütfen parametreleri kontrol edin.")

# ---- Kullanıcı arayüzü ----
def get_input(prompt, default):
    val = input(f"{prompt} (Varsayılan {default}): ").strip()
    if val == '':
        return default
    try:
        return float(val) if '.' in val else int(val)
    except ValueError:
        return default

def main():
    size = get_input("Matris Boyutu (ana hücre sayısı)", 10)
    gen = GridShape(outer_size=int(size), sub_res=48)

    print("\nArka Plan Renkleri: 1:Beyaz, 2:Bulut, 3:Gümüş, 4:Kömür, 5:Açık Gri")
    bg_choice = input("Seçim (1-5): ").strip() or '1'
    gen.selected_bg = gen.bg_color_map.get(bg_choice, '#ffffff')

    show_nums = input("Hücre numaraları gösterilsin mi? (E/h): ").lower() != 'h'
    show_grid = input("Izgara çizgileri gösterilsin mi? (E/h): ").lower() != 'h'
    show_ticks = input("Eksen değerleri gösterilsin mi? (E/h): ").lower() != 'h'

    while True:
        stats = gen.get_advanced_stats()
        mode_str = "ÇOKLU ŞEKİL" if gen.cumulative_mode else "TEK ŞEKİL"
        res_str = f"SUBGRID (1/{gen.sub_res**2})" if gen.subgrid_active else "KLASİK"
        print(f"\n--- MOD: {mode_str} | {res_str} ---")
        print(f"Kaplama: {stats['shape_cell_count']}/{size**2} hücre (%{stats['shape_percent_cells']})")
        print("[1:Kare/Dikdörtgen] [2:Daire] [3:Üçgen] [4:Elmas] [5:Çokgen] [7:Döndür (subgrid)")
        print("[6:Çoklu/Tekli] [S:Subgrid Aç/Kapa] [8:Geri Al] [9:Temizle] [0:Çıkış]")
        ch = input("Seçim: ").upper()

        if ch == '0':
            break
        elif ch == '6':
            gen.cumulative_mode = not gen.cumulative_mode
            continue
        elif ch == 'S':
            gen.subgrid_active = not gen.subgrid_active
            gen.shapes_history = []
            gen.reset_all()
            continue
        elif ch == '8':
            if gen.shapes_history:
                gen.shapes_history.pop()
                gen._rebuild_layer()
            continue
        elif ch == '9':
            gen.shapes_history = []
            gen.reset_all()
            continue

        params = {}
        shape_type = 'square'
        try:
            if ch == '1':
                params = {'row': get_input("Başlangıç satırı", 2), 'col': get_input("Başlangıç sütunu", 2),
                          'h': get_input("Yükseklik", 4), 'w': get_input("Genişlik", 4)}
                shape_type = 'rectangle'
            elif ch == '2':
                params = {'row': get_input("Merkez satır", 5), 'col': get_input("Merkez sütun", 5),
                          'radius': get_input("Yarıçap", 2.5)}
                shape_type = 'circle'
            elif ch == '3':
                params = {'row': get_input("Tepe satırı", 2), 'col': get_input("Tepe sütunu", 5),
                          'size': get_input("Kenar uzunluğu", 4)}
                shape_type = 'triangle'
            elif ch == '4':
                params = {'row': get_input("Merkez satır", 5), 'col': get_input("Merkez sütun", 5),
                          'size': get_input("Yarıçap", 2)}
                shape_type = 'diamond'
            elif ch == '5':
                pts = input("Köşeler (satır,sütun) örn: 2,2 5,2 5,5 : ").strip()
                if pts == '':
                    pts = "2,2 5,2 5,5"
                coords = []
                for pt in pts.split():
                    try:
                        r, c = map(int, pt.split(','))
                        coords.append((r, c))
                    except:
                        pass
                if len(coords) < 3:
                    print("En az 3 nokta girin. Varsayılan kullanılıyor.")
                    coords = [(2,2), (5,2), (5,5)]
                params = {'coords': coords}
                shape_type = 'polygon'

            elif ch == '7':
                if not gen.subgrid_active:
                    print("Döndürme sadece SUBGRID modunda çalışır. Önce S ile subgrid'i açın.")
                elif not gen.shapes_history:
                    print("Döndürülecek şekil yok. Önce bir şekil çizin (1-5).")
                else:
                    # Merkez ve açıyı al
                    row = get_input("Döndürme merkezi satırı", 5)
                    col = get_input("Döndürme merkezi sütunu", 5)
                    angle = get_input("Döndürme açısı (derece)", 45)
                    if gen.rotate_last_shape(angle, row, col):
                        print(f"Şekil {angle}° döndürüldü.")
                        # İstatistikleri güncelle ve göster
                        stats = gen.get_advanced_stats()
                        gen.export_data(stats)
                        # Terminal tablosunu göster
                        print("\n--- MATRİS (ana hücreler) ---")
                        for i in range(gen.outer_size):
                            row_vals = []
                            for j in range(gen.outer_size):
                                val = gen.bg_matrix[i, j]
                                if gen._get_cell_level_mask()[i, j]:
                                    row_vals.append(f"[{val}]")
                                else:
                                    row_vals.append(f"{val:3}")
                            print(" ".join(row_vals))
                        print("\n--- İSTATİSTİKLER ---")
                        print(f"Şekil içi hücre sayısı: {stats['shape_cell_count']} (%{stats['shape_percent_cells']})")
                        # Görselleştir
                        fig, ax = gen.visualize(show_nums, show_grid, show_ticks)
                        save = input("\nGörseli kaydet? (png/jpg/pdf/svg/h): ").lower()
                        if save in ['png','jpg','pdf','svg']:
                            fname = f"grid_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{save}"
                            plt.savefig(fname, dpi=300, bbox_inches='tight')
                            print(f"Kaydedildi: {fname}")
                        plt.show()
                    else:
                        print("Döndürme başarısız oldu.")
                continue
            
            else:
                print("Geçersiz seçim.")
                continue

            gen.generate_shape(shape_type, params)
            stats = gen.get_advanced_stats()
            gen.export_data(stats)

            # Terminal tablosu
            print("\n--- MATRİS (ana hücreler) ---")
            for i in range(size):
                row = []
                for j in range(size):
                    val = gen.bg_matrix[i, j]
                    if gen._get_cell_level_mask()[i, j]:
                        row.append(f"[{val}]")
                    else:
                        row.append(f"{val:3}")
                print(" ".join(row))

            # Detaylı istatistikler
            print("\n--- İSTATİSTİKLER ---")
            print(f"Şekil içi hücre sayısı: {stats['shape_cell_count']} (%{stats['shape_percent_cells']})")
            print(f"Toplam: {stats['shape_sum']}  Ort: {stats['shape_mean']}  Std: {stats['shape_std']}")
            print(f"Min: {stats['shape_min']}  Max: {stats['shape_max']}  Medyan: {stats['shape_median']}")
            print(f"Arka plan toplam: {stats['bg_sum']}  Ort: {stats['bg_mean']}")
            print(f"Genel toplam: {stats['total_sum']}  Ort: {stats['total_mean']}")

            fig, ax = gen.visualize(show_nums, show_grid, show_ticks)
            save = input("\nGörseli kaydet? (png/jpg/pdf/svg/h): ").lower()
            if save in ['png','jpg','pdf','svg']:
                fname = f"grid_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{save}"
                plt.savefig(fname, dpi=300, bbox_inches='tight')
                print(f"Kaydedildi: {fname}")
            plt.show()
        except Exception as e:
            print(f"Hata: {e}. Lütfen parametreleri kontrol edin.")

if __name__ == "__main__":
    GridShape.run_interactive()
