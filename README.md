# Audio Normalizer 🔊

Profesjonalna aplikacja desktopowa do wsadowej (batch) normalizacji głośności w plikach wideo. Program wyrównuje poziom dźwięku do nowoczesnych standardów (LUFS), **nie ingerując w jakość obrazu** (kopiowanie strumienia wideo).

![Image](preview.png)

Idealne rozwiązanie dla twórców wideo, których nagrania mają różny poziom głośności i wymagają ujednolicenia przed publikacją na YouTube, Spotify czy w TV.

## ✨ Główne funkcje

*   **Bezstratne Wideo:** Program używa trybu `copy` dla ścieżki wideo – obraz nie jest rekompresowany, więc jakość pozostaje 1:1, a proces jest błyskawiczny.
*   **Inteligentna Normalizacja (EBU R128):** Wykorzystuje zaawansowany filtr `loudnorm` w FFmpeg, który dba nie tylko o średnią głośność, ale też o "True Peak" (zapobiega przesterowaniu/trzeszczeniu).
*   **Analiza Plików:** Funkcja "Skanuj" pozwala sprawdzić aktualną głośność plików przed podjęciem decyzji.
*   **Nowoczesne GUI:** Ciemny, estetyczny interfejs oparty na `customtkinter`.
*   **Pełna Kontrola:** Suwak pozwalający wybrać docelowy poziom LUFS (od standardów kinowych po głośne standardy internetowe).

## 🛠️ Wymagania

### Dla użytkownika (gotowa aplikacja .exe)
1.  **System Windows** (10/11).
2.  **FFmpeg**: Wymagany do działania silnika.
    *   Możesz wskazać plik `ffmpeg.exe` ręcznie w aplikacji.
    *   LUB mieć go w zmiennej systemowej `PATH` (aplikacja wykryje go automatycznie).

### Dla programisty (uruchamianie z kodu)
*   Python 3.x
*   Zależności z pliku `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 Jak używać

1.  Uruchom `AudioNormalizerUltra.exe`.
2.  **Konfiguracja:** Wskaż ścieżkę do `ffmpeg.exe` (jeśli nie wykryto automatycznie) oraz foldery Źródłowy i Docelowy.
3.  **Analiza (Opcjonalnie):** Kliknij **🔍 Skanuj pliki**. Program sprawdzi próbkę Twoich filmów i powie Ci, jaką mają średnią głośność.
4.  **Ustaw Cel (LUFS):** Przesuń suwak, aby wybrać docelową głośność:
    *   **-23 LUFS:** Standard telewizyjny (EBU R128), dość cicho.
    *   **-14 LUFS:** **Zalecane dla Internetu** (YouTube, Spotify, Podcasty).
    *   **-9 LUFS:** Bardzo głośno (standard płyt CD / głośnych reklam).
5.  Kliknij **ROZPOCZNIJ NORMALIZACJĘ**.

## 🏗️ Budowanie pliku .exe

Aby zbudować plik wykonywalny samodzielnie:

1.  Upewnij się, że zainstalowałeś wymagane biblioteki.
2.  Uruchom skrypt:
    ```cmd
    build.bat
    ```
3.  Gotowy program znajdziesz w folderze `dist/`.

> **Info:** Skrypt budujący automatycznie dołącza style `customtkinter` i ukrywa okno konsoli dla procesów w tle.

## ⚙️ Szczegóły techniczne

Program wykonuje następujące operacje FFmpeg na każdym pliku:

*   **Wideo:** `-c:v copy` (Kopiowanie strumienia bit-po-bicie. Zero utraty jakości, bardzo szybkie działanie).
*   **Audio:** `-c:a aac -b:a 192k` (Konwersja audio do formatu AAC z wysokim bitratem).
*   **Filtr:** `loudnorm` z parametrami:
    *   `I` (Integrated Loudness): Wartość wybrana suwakiem (domyślnie -14.0).
    *   `TP` (True Peak): -1.5 dBTP (Zabezpieczenie przed przesterami).
    *   `LRA` (Loudness Range): 11 LU (Zachowanie naturalnej dynamiki).