import os
import sys
import threading
import shutil
import subprocess
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox
import ffmpeg

# --- Konfiguracja Wyglądu ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class AudioNormalizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Audio Normalizer Ultra 🔊")
        self.geometry("750x700")
        self.resizable(False, False)

        # Zmienne
        self.ffmpeg_path = ctk.StringVar()
        self.input_path = ctk.StringVar()
        self.output_path = ctk.StringVar()
        
        # Target LUFS (zakres od -25 do -5)
        # -23 LUFS to standard TV (cicho)
        # -14 LUFS to standard YouTube/Spotify (optymalnie)
        # -9 LUFS to bardzo głośno (CD)
        self.target_lufs = ctk.DoubleVar(value=-14.0) 
        self.is_running = False

        # Auto-detekcja ffmpeg
        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            self.ffmpeg_path.set(system_ffmpeg)

        self.create_widgets()

    def create_widgets(self):
        # --- Kontener Główny ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Tytuł
        ctk.CTkLabel(self.main_frame, text="NORMALIZATOR DŹWIĘKU", 
                     font=("Roboto Medium", 22)).pack(pady=(20, 10))
        ctk.CTkLabel(self.main_frame, text="Wyrównuje głośność audio • Nie rusza jakości wideo", 
                     font=("Roboto", 12), text_color="gray60").pack(pady=(0, 15))

        # --- Sekcja Ścieżek ---
        self.create_path_entry("Ścieżka FFmpeg:", self.ffmpeg_path, self.select_ffmpeg)
        self.create_path_entry("Folder Źródłowy:", self.input_path, self.select_input)
        self.create_path_entry("Folder Docelowy:", self.output_path, self.select_output)

        # Separator
        ctk.CTkFrame(self.main_frame, height=2, fg_color="gray30").pack(fill="x", padx=20, pady=15)

        # --- Sekcja Analizy i Ustawień ---
        settings_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        settings_frame.pack(fill="x", padx=20, pady=5)

        # Lewa strona: Przycisk Analizy
        left_col = ctk.CTkFrame(settings_frame, fg_color="transparent")
        left_col.pack(side="left", fill="y")
        
        self.btn_analyze = ctk.CTkButton(left_col, text="🔍 Skanuj pliki (Sprawdź głośność)", 
                                         fg_color="#3B8ED0", hover_color="#36719F",
                                         command=self.start_analysis_thread)
        self.btn_analyze.pack(anchor="w", pady=5)
        
        self.lbl_analysis_result = ctk.CTkLabel(left_col, text="Brak danych o głośności", 
                                                text_color="gray", font=("Roboto", 11))
        self.lbl_analysis_result.pack(anchor="w")

        # Prawa strona: Suwak
        right_col = ctk.CTkFrame(settings_frame, fg_color="transparent")
        right_col.pack(side="right", fill="x", expand=True, padx=(20, 0))

        ctk.CTkLabel(right_col, text="Docelowa Głośność (LUFS)", font=("Roboto", 14)).pack(anchor="w")
        
        slider_box = ctk.CTkFrame(right_col, fg_color="transparent")
        slider_box.pack(fill="x", pady=5)

        self.lbl_lufs_val = ctk.CTkLabel(slider_box, text="-14.0", font=("Roboto", 24, "bold"), text_color="#3B8ED0")
        self.lbl_lufs_val.pack(side="right", padx=10)

        self.slider = ctk.CTkSlider(slider_box, from_=-25, to=-5, number_of_steps=40, 
                                    variable=self.target_lufs, command=self.update_lufs_label)
        self.slider.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(right_col, text="(-23 = TV/Cicho  |  -14 = YouTube/Standard  |  -9 = Głośno)", 
                     text_color="gray60", font=("Roboto", 10)).pack()

        # --- Progress Bar ---
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(20, 5))
        self.progress_bar.set(0)
        
        self.lbl_status = ctk.CTkLabel(self.main_frame, text="Gotowy", text_color="gray70")
        self.lbl_status.pack(pady=(0, 10))

        # --- Przycisk Start ---
        self.btn_start = ctk.CTkButton(self.main_frame, text="ROZPOCZNIJ NORMALIZACJĘ", 
                                       font=("Roboto", 14, "bold"), height=45,
                                       fg_color="#2CC985", hover_color="#25A66E",
                                       command=self.start_processing_thread)
        self.btn_start.pack(fill="x", padx=20, pady=10)

        # --- Konsola Logów ---
        self.log_area = ctk.CTkTextbox(self.main_frame, height=120, font=("Consolas", 11))
        self.log_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.log_area.configure(state="disabled")

    def create_path_entry(self, label_text, variable, cmd):
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame, text=label_text, width=110, anchor="w").pack(side="left")
        ctk.CTkEntry(frame, textvariable=variable).pack(side="left", fill="x", expand=True, padx=10)
        ctk.CTkButton(frame, text="📂", width=40, command=cmd).pack(side="right")

    # --- Logika UI ---
    def select_ffmpeg(self):
        path = filedialog.askopenfilename(filetypes=[("Pliki wykonywalne", "*.exe")])
        if path: self.ffmpeg_path.set(path)

    def select_input(self):
        path = filedialog.askdirectory()
        if path: 
            self.input_path.set(path)
            self.lbl_analysis_result.configure(text="Folder wybrany. Kliknij Skanuj.", text_color="gray")

    def select_output(self):
        path = filedialog.askdirectory()
        if path: self.output_path.set(path)

    def update_lufs_label(self, val):
        self.lbl_lufs_val.configure(text=f"{val:.1f}")

    def log(self, message, level="INFO"):
        self.log_area.configure(state="normal")
        prefix = "✅" if level == "SUCCESS" else "❌" if level == "ERROR" else "ℹ️"
        self.log_area.insert("end", f"{prefix} {message}\n")
        self.log_area.see("end")
        self.log_area.configure(state="disabled")

    def get_creation_flags(self):
        """Pomocnik do ukrywania okna konsoli na Windows"""
        if os.name == 'nt':
            return 0x08000000 # CREATE_NO_WINDOW
        return 0

    # --- Wątek Analizy ---
    def start_analysis_thread(self):
        if not self.input_path.get() or not self.ffmpeg_path.get():
            messagebox.showwarning("Błąd", "Wybierz folder źródłowy i ścieżkę FFmpeg!")
            return
        threading.Thread(target=self.run_analysis, daemon=True).start()

    def run_analysis(self):
        input_dir = self.input_path.get()
        ffmpeg_exe = self.ffmpeg_path.get()
        files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.mp4', '.mov', '.mkv', '.avi'))]
        
        if not files:
            self.log("Brak plików wideo do analizy.", "ERROR")
            return

        self.btn_analyze.configure(state="disabled", text="Skanowanie...")
        self.log("Rozpoczynam analizę głośności (może to chwilę potrwać)...")

        total_lufs = 0
        count = 0
        
        # Analizujemy max 3 pierwsze pliki żeby nie tracić czasu
        files_to_scan = files[:3] 

        for filename in files_to_scan:
            filepath = os.path.join(input_dir, filename)
            try:
                # Uruchamiamy filtr loudnorm w trybie print_format=json aby odczytać głośność
                # -vn oznacza brak wideo (szybciej), -f null - oznacza brak pliku wyjściowego
                cmd = [
                    ffmpeg_exe, '-i', filepath, 
                    '-vn', 
                    '-af', 'loudnorm=print_format=json', 
                    '-f', 'null', '-'
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    encoding='utf-8', 
                    creationflags=self.get_creation_flags()
                )
                
                # FFmpeg wypisuje JSON z loudnorm na stderr (nie stdout!)
                stderr_output = result.stderr
                
                # Szukamy JSONa w wyjściu
                start_idx = stderr_output.rfind('{')
                end_idx = stderr_output.rfind('}')
                
                if start_idx != -1 and end_idx != -1:
                    json_str = stderr_output[start_idx:end_idx+1]
                    data = json.loads(json_str)
                    input_i = float(data.get('input_i', -99))
                    total_lufs += input_i
                    count += 1
                    self.log(f"Plik {filename}: {input_i} LUFS")
            except Exception as e:
                self.log(f"Błąd analizy {filename}: {str(e)}", "ERROR")

        self.btn_analyze.configure(state="normal", text="🔍 Skanuj ponownie")

        if count > 0:
            avg_lufs = total_lufs / count
            self.lbl_analysis_result.configure(text=f"Średnia wykryta: {avg_lufs:.1f} LUFS", text_color="#2CC985")
            self.log(f"Zakończono analizę. Średnia głośność źródłowa: {avg_lufs:.1f} LUFS", "SUCCESS")
            
            # Logika sugestii:
            # Nie zmieniamy suwaka automatycznie, bo -14 LUFS to standard internetowy.
            # Użytkownik widzi teraz, że np. ma -25 LUFS i wie, że podgłośnieni do -14.
        else:
            self.lbl_analysis_result.configure(text="Nie udało się zmierzyć głośności", text_color="red")

    # --- Wątek Przetwarzania ---
    def start_processing_thread(self):
        if not all([self.input_path.get(), self.output_path.get(), self.ffmpeg_path.get()]):
            messagebox.showwarning("Braki", "Uzupełnij wszystkie ścieżki!")
            return
        
        if self.is_running: return

        self.is_running = True
        self.btn_start.configure(state="disabled", text="PRZETWARZANIE...", fg_color="gray")
        threading.Thread(target=self.run_normalization, daemon=True).start()

    def run_normalization(self):
        input_dir = self.input_path.get()
        output_dir = self.output_path.get()
        target_lufs = self.target_lufs.get()
        ffmpeg_exe = self.ffmpeg_path.get()

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.mp4', '.mov', '.mkv', '.avi'))]
        total = len(files)
        
        if total == 0:
            self.log("Brak plików wideo!", "ERROR")
            self.reset_ui()
            return

        self.log(f"Start: {total} plików. Cel: {target_lufs:.1f} LUFS", "INFO")

        for i, filename in enumerate(files):
            in_f = os.path.join(input_dir, filename)
            out_f = os.path.join(output_dir, filename)
            
            self.lbl_status.configure(text=f"Normalizacja: {filename} ({i+1}/{total})")
            self.progress_bar.set((i) / total)
            
            try:
                # --- KLUCZOWE KOMENDY FFmpeg ---
                # -c:v copy         -> Kopiuje obraz bez zmian (szybko, bez utraty jakości)
                # -af loudnorm=...  -> Normalizuje dźwięk do zadanego I (Integrated loudness)
                # -c:a aac          -> Musimy przekodować audio, żeby zmienić głośność
                # -b:a 192k         -> Dobry bitrate audio
                
                cmd = [
                    ffmpeg_exe, '-y',
                    '-i', in_f,
                    '-c:v', 'copy',
                    '-af', f'loudnorm=I={target_lufs}:TP=-1.5:LRA=11',
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    out_f
                ]

                # Uruchomienie bez okna konsoli
                subprocess.run(
                    cmd,
                    check=True,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    creationflags=self.get_creation_flags()
                )

                self.log(f"Gotowe: {filename}", "SUCCESS")
            
            except subprocess.CalledProcessError as e:
                self.log(f"Błąd FFmpeg przy {filename}", "ERROR")
            except Exception as e:
                self.log(f"Błąd: {str(e)}", "ERROR")

            self.progress_bar.set((i + 1) / total)

        messagebox.showinfo("Sukces", "Zakończono normalizację!")
        self.reset_ui()

    def reset_ui(self):
        self.is_running = False
        self.btn_start.configure(state="normal", text="ROZPOCZNIJ NORMALIZACJĘ", fg_color="#2CC985")
        self.lbl_status.configure(text="Gotowy")
        self.progress_bar.set(0)

if __name__ == "__main__":
    app = AudioNormalizerApp()
    app.mainloop()