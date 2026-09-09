from __future__ import annotations

import csv
import hashlib
import queue
import re
import threading
import sys
from datetime import datetime
from pathlib import Path
from tkinter import BOTH, DISABLED, END, LEFT, NORMAL, RIGHT, X, filedialog, messagebox, ttk
import tkinter as tk
import os
import shutil

from markitdown import MarkItDown
from PIL import Image
import pytesseract


APP_PATH = Path(__file__).resolve()
if getattr(sys, "frozen", False):
    WORKSPACE_ROOT = Path(sys.executable).resolve().parent
else:
    WORKSPACE_ROOT = APP_PATH.parents[2]
APP_DATA_DIR = WORKSPACE_ROOT / "work" / "desktop_app"
UPLOAD_DIR = APP_DATA_DIR / "inputs"
OUTPUT_DIR = APP_DATA_DIR / "markdown"
MANIFEST_PATH = APP_DATA_DIR / "manifest.csv"
DEFAULT_TESSERACT_PATHS = [
    Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
    Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
]

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".doc",
    ".pptx",
    ".xlsx",
    ".xls",
    ".html",
    ".htm",
    ".txt",
    ".csv",
    ".json",
    ".xml",
    ".zip",
    ".epub",
    ".msg",
    ".wav",
    ".mp3",
    ".jpg",
    ".jpeg",
    ".jfif",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".jfif", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def ensure_dirs() -> None:
    for path in (APP_DATA_DIR, UPLOAD_DIR, OUTPUT_DIR):
        path.mkdir(parents=True, exist_ok=True)

    if not MANIFEST_PATH.exists():
        MANIFEST_PATH.write_text(
            "source_path,source_hash,output_path,status,converted_at,error\n",
            encoding="utf-8",
        )


def safe_stem(name: str) -> str:
    stem = Path(name).stem
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._")
    return cleaned or "documento"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def append_manifest(row: dict[str, str]) -> None:
    with MANIFEST_PATH.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "source_path",
                "source_hash",
                "output_path",
                "status",
                "converted_at",
                "error",
            ],
        )
        writer.writerow(row)


class MarkItDownDesktopApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        ensure_dirs()
        self.title("LocalDoc Markdown")
        self.geometry("980x680")
        self.minsize(840, 560)

        self.converter = MarkItDown()
        self.selected_files: list[Path] = []
        self.event_queue: queue.Queue[tuple[str, str]] = queue.Queue()
        self.is_busy = False

        self.output_dir_var = tk.StringVar(value=str(OUTPUT_DIR))
        self.tesseract_path_var = tk.StringVar(value=self._detect_tesseract())
        self.ocr_language_var = tk.StringVar(value="spa+eng")
        self.status_var = tk.StringVar(value="Listo")

        self._configure_style()
        self._build_ui()
        self.after(100, self._drain_queue)

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", padding=(12, 8))
        style.configure("Primary.TButton", padding=(14, 9))
        style.configure("TLabel", padding=(0, 2))
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Small.TLabel", foreground="#4b5563")

    def _build_ui(self) -> None:
        main = ttk.Frame(self, padding=18)
        main.pack(fill=BOTH, expand=True)

        header = ttk.Frame(main)
        header.pack(fill=X)
        ttk.Label(header, text="LocalDoc Markdown", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Convierte documentos locales a Markdown y guarda un historial de conversiones.",
            style="Small.TLabel",
        ).pack(anchor="w", pady=(2, 12))

        controls = ttk.Frame(main)
        controls.pack(fill=X, pady=(0, 12))

        ttk.Button(controls, text="Agregar archivos", command=self.select_files).pack(side=LEFT, padx=(0, 8))
        ttk.Button(controls, text="Agregar imagenes", command=self.select_images).pack(side=LEFT, padx=(0, 8))
        ttk.Button(controls, text="Agregar carpeta", command=self.select_folder).pack(side=LEFT, padx=(0, 8))
        ttk.Button(controls, text="Limpiar lista", command=self.clear_files).pack(side=LEFT, padx=(0, 8))
        self.convert_button = ttk.Button(
            controls,
            text="Convertir",
            style="Primary.TButton",
            command=self.convert_selected,
        )
        self.convert_button.pack(side=RIGHT)

        output_frame = ttk.LabelFrame(main, text="Salida", padding=10)
        output_frame.pack(fill=X, pady=(0, 12))
        ttk.Entry(output_frame, textvariable=self.output_dir_var).pack(side=LEFT, fill=X, expand=True, padx=(0, 8))
        ttk.Button(output_frame, text="Cambiar", command=self.choose_output_dir).pack(side=LEFT, padx=(0, 8))
        ttk.Button(output_frame, text="Abrir", command=self.open_output_dir).pack(side=LEFT)

        ocr_frame = ttk.LabelFrame(main, text="OCR para imagenes", padding=10)
        ocr_frame.pack(fill=X, pady=(0, 12))
        ttk.Label(ocr_frame, text="Ruta tesseract.exe").pack(side=LEFT, padx=(0, 8))
        ttk.Entry(ocr_frame, textvariable=self.tesseract_path_var).pack(side=LEFT, fill=X, expand=True, padx=(0, 8))
        ttk.Button(ocr_frame, text="Detectar", command=self.detect_tesseract_button).pack(side=LEFT, padx=(0, 8))
        ttk.Button(ocr_frame, text="Elegir EXE", command=self.choose_tesseract).pack(side=LEFT, padx=(0, 8))
        ttk.Label(ocr_frame, text="Idioma").pack(side=LEFT, padx=(0, 8))
        ttk.Entry(ocr_frame, textvariable=self.ocr_language_var, width=12).pack(side=LEFT)

        body = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        body.pack(fill=BOTH, expand=True)

        file_frame = ttk.LabelFrame(body, text="Archivos", padding=8)
        log_frame = ttk.LabelFrame(body, text="Registro", padding=8)
        body.add(file_frame, weight=1)
        body.add(log_frame, weight=1)

        self.file_list = tk.Listbox(file_frame, height=18, activestyle="none")
        self.file_list.pack(fill=BOTH, expand=True)

        self.log_text = tk.Text(log_frame, height=18, wrap="word", state=DISABLED)
        self.log_text.pack(fill=BOTH, expand=True)

        footer = ttk.Frame(main)
        footer.pack(fill=X, pady=(12, 0))
        ttk.Label(footer, textvariable=self.status_var, style="Small.TLabel").pack(side=LEFT)
        ttk.Button(footer, text="Abrir historial CSV", command=self.open_manifest).pack(side=RIGHT)

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state=NORMAL)
        self.log_text.insert(END, f"[{timestamp}] {message}\n")
        self.log_text.see(END)
        self.log_text.configure(state=DISABLED)

    def _detect_tesseract(self) -> str:
        path_from_env = shutil.which("tesseract")
        if path_from_env:
            return path_from_env
        for path in DEFAULT_TESSERACT_PATHS:
            if path.exists():
                return str(path)
        return ""

    def select_files(self) -> None:
        filenames = filedialog.askopenfilenames(
            title="Selecciona documentos",
            filetypes=[
                ("Archivos compatibles", "*.pdf *.docx *.doc *.pptx *.xlsx *.xls *.html *.htm *.txt *.csv *.json *.xml *.zip *.epub *.msg *.wav *.mp3 *.jpg *.jpeg *.jfif *.png *.bmp *.tif *.tiff *.webp"),
                ("Imagenes OCR", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.webp"),
                ("Documentos", "*.pdf *.docx *.doc *.pptx *.xlsx *.xls *.html *.htm *.txt *.csv *.json *.xml *.zip *.epub *.msg *.wav *.mp3"),
                ("Todos los archivos", "*.*"),
            ],
        )
        self.add_files([Path(name) for name in filenames])

    def select_images(self) -> None:
        filenames = filedialog.askopenfilenames(
            title="Selecciona imagenes para OCR",
            filetypes=[
                ("Imagenes OCR", "*.jpg *.jpeg *.jfif *.png *.bmp *.tif *.tiff *.webp"),
                ("Todos los archivos", "*.*"),
            ],
        )
        self.add_files([Path(name) for name in filenames])

    def select_folder(self) -> None:
        folder = filedialog.askdirectory(title="Selecciona carpeta de entrada")
        if not folder:
            return
        files = [
            path
            for path in Path(folder).rglob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
        self.add_files(files)

    def add_files(self, files: list[Path]) -> None:
        existing = {path.resolve() for path in self.selected_files}
        added = 0
        for path in files:
            resolved = path.resolve()
            if resolved in existing or not path.is_file():
                continue
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            self.selected_files.append(path)
            self.file_list.insert(END, str(path))
            existing.add(resolved)
            added += 1
        self.status_var.set(f"{len(self.selected_files)} archivo(s) en cola")
        if added:
            self.log(f"Agregados {added} archivo(s)")

    def clear_files(self) -> None:
        self.selected_files.clear()
        self.file_list.delete(0, END)
        self.status_var.set("Lista limpia")

    def choose_output_dir(self) -> None:
        folder = filedialog.askdirectory(title="Selecciona carpeta de salida")
        if folder:
            self.output_dir_var.set(folder)

    def choose_tesseract(self) -> None:
        filename = filedialog.askopenfilename(
            title="Selecciona tesseract.exe",
            initialdir=r"C:\Program Files\Tesseract-OCR",
            filetypes=[("Tesseract", "tesseract.exe"), ("Ejecutables", "*.exe"), ("Todos los archivos", "*.*")],
        )
        if filename and Path(filename).name.lower() == "tesseract.exe":
            self.tesseract_path_var.set(filename)
        elif filename:
            messagebox.showwarning(
                "Archivo incorrecto",
                "Ese campo debe apuntar a tesseract.exe. Para convertir imagenes usa Agregar imagenes.",
            )

    def detect_tesseract_button(self) -> None:
        detected = self._detect_tesseract()
        if detected:
            self.tesseract_path_var.set(detected)
            self.log(f"Tesseract detectado: {detected}")
        else:
            messagebox.showwarning(
                "Tesseract no detectado",
                "No encontre tesseract.exe automaticamente. Usa Elegir EXE y selecciona el ejecutable de Tesseract.",
            )

    def open_output_dir(self) -> None:
        output_dir = Path(self.output_dir_var.get())
        output_dir.mkdir(parents=True, exist_ok=True)
        os.startfile(str(output_dir))

    def open_manifest(self) -> None:
        os.startfile(str(MANIFEST_PATH))

    def convert_selected(self) -> None:
        if self.is_busy:
            return
        if not self.selected_files:
            messagebox.showinfo("Sin archivos", "Agrega uno o mas documentos antes de convertir.")
            return

        output_dir = Path(self.output_dir_var.get())
        output_dir.mkdir(parents=True, exist_ok=True)
        self.is_busy = True
        self.convert_button.configure(state=DISABLED)
        self.status_var.set("Convirtiendo...")
        thread = threading.Thread(target=self._convert_worker, args=(list(self.selected_files), output_dir), daemon=True)
        thread.start()

    def _convert_worker(self, files: list[Path], output_dir: Path) -> None:
        tesseract_path = self.tesseract_path_var.get().strip()
        ocr_language = self.ocr_language_var.get().strip() or "spa+eng"
        converted = 0
        errors = 0
        for source in files:
            try:
                digest = sha256_file(source)
                output_path = output_dir / f"{safe_stem(source.name)}-{digest[:10]}.md"
                if source.suffix.lower() in IMAGE_EXTENSIONS:
                    self.event_queue.put(("log", f"OCR {source.name}"))
                    markdown = self._ocr_image(source, tesseract_path, ocr_language)
                else:
                    self.event_queue.put(("log", f"Convirtiendo {source.name}"))
                    result = self.converter.convert(str(source))
                    markdown = result.text_content

                output_path.write_text(markdown, encoding="utf-8")
                append_manifest(
                    {
                        "source_path": str(source),
                        "source_hash": digest,
                        "output_path": str(output_path),
                        "status": "converted",
                        "converted_at": datetime.now().isoformat(timespec="seconds"),
                        "error": "",
                    }
                )
                converted += 1
                self.event_queue.put(("log", f"OK {output_path.name}"))
            except Exception as exc:
                errors += 1
                append_manifest(
                    {
                        "source_path": str(source),
                        "source_hash": "",
                        "output_path": "",
                        "status": "error",
                        "converted_at": datetime.now().isoformat(timespec="seconds"),
                        "error": str(exc),
                    }
                )
                self.event_queue.put(("log", f"ERROR {source.name}: {exc}"))

        self.event_queue.put(("done", f"Finalizado: {converted} convertido(s), {errors} error(es)"))

    def _ocr_image(self, source: Path, tesseract_path: str, language: str) -> str:
        if not tesseract_path or Path(tesseract_path).suffix.lower() != ".exe":
            tesseract_path = self._detect_tesseract()

        if not tesseract_path:
            raise RuntimeError("No se encontro tesseract.exe. Instala Tesseract OCR o selecciona la ruta.")

        executable = Path(tesseract_path)
        if not executable.exists() or executable.name.lower() != "tesseract.exe":
            raise RuntimeError(f"No existe tesseract.exe en: {tesseract_path}")

        pytesseract.pytesseract.tesseract_cmd = str(executable)
        with Image.open(source) as image:
            text = pytesseract.image_to_string(image, lang=language)

        text = text.strip()
        if not text:
            text = "_OCR no encontro texto legible en la imagen._"

        return f"# {source.name}\n\n{text}\n"

    def _drain_queue(self) -> None:
        try:
            while True:
                event, payload = self.event_queue.get_nowait()
                if event == "log":
                    self.log(payload)
                elif event == "done":
                    self.is_busy = False
                    self.convert_button.configure(state=NORMAL)
                    self.status_var.set(payload)
                    self.log(payload)
        except queue.Empty:
            pass
        self.after(100, self._drain_queue)


def main() -> None:
    app = MarkItDownDesktopApp()
    app.mainloop()


if __name__ == "__main__":
    main()
