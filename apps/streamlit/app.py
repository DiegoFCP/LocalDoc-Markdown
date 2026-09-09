from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
from markitdown import MarkItDown

from localdoc_markdown.core import (
    SUPPORTED_TYPE_NAMES,
    FileLimits,
    append_manifest,
    ensure_manifest,
    read_manifest,
    safe_filename,
    sha256_bytes,
    validate_named_sizes,
)

APP_PATH = Path(__file__).resolve()
if getattr(sys, "frozen", False):
    WORKSPACE_ROOT = Path(sys.executable).resolve().parent
else:
    WORKSPACE_ROOT = APP_PATH.parents[2]
APP_DATA_DIR = WORKSPACE_ROOT / "work" / "streamlit_app"
UPLOAD_DIR = APP_DATA_DIR / "uploads"
CONVERTED_DIR = APP_DATA_DIR / "converted"
APP_MANIFEST = APP_DATA_DIR / "manifest.csv"
PIPELINE_SCRIPT = WORKSPACE_ROOT / "scripts" / "Process-MarkitdownInbox.ps1"
DEFAULT_PIPELINE_INPUT = WORKSPACE_ROOT / "work" / "pipeline" / "input"
DEFAULT_PIPELINE_OUTPUT = WORKSPACE_ROOT / "work" / "pipeline" / "output"
DEFAULT_PIPELINE_LOGS = WORKSPACE_ROOT / "work" / "pipeline" / "logs"

MANIFEST_FIELDS = [
    "source_name",
    "source_hash",
    "input_path",
    "output_path",
    "status",
    "converted_at",
    "error",
]
FILE_LIMITS = FileLimits()


def ensure_dirs() -> None:
    for path in (APP_DATA_DIR, UPLOAD_DIR, CONVERTED_DIR):
        path.mkdir(parents=True, exist_ok=True)

    ensure_manifest(APP_MANIFEST, MANIFEST_FIELDS)


@st.cache_resource(show_spinner=False)
def get_converter() -> MarkItDown:
    return MarkItDown()


def convert_upload(filename: str, content: bytes) -> tuple[Path, str]:
    digest = sha256_bytes(content)
    clean_name = safe_filename(filename)
    stem = Path(clean_name).stem
    suffix = Path(clean_name).suffix
    saved_input = UPLOAD_DIR / f"{stem}-{digest[:10]}{suffix}"
    output_path = CONVERTED_DIR / f"{stem}-{digest[:10]}.md"

    saved_input.write_bytes(content)

    result = get_converter().convert(str(saved_input))
    markdown = result.text_content
    output_path.write_text(markdown, encoding="utf-8")

    append_manifest(
        APP_MANIFEST,
        MANIFEST_FIELDS,
        {
            "source_name": filename,
            "source_hash": digest,
            "input_path": str(saved_input),
            "output_path": str(output_path),
            "status": "converted",
            "converted_at": datetime.now().isoformat(timespec="seconds"),
            "error": "",
        }
    )
    return output_path, markdown


def render_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            max-width: 1180px;
        }
        [data-testid="stMetric"] {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 0.8rem 1rem;
            background: #ffffff;
        }
        textarea {
            font-family: Consolas, ui-monospace, monospace;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_converter_tab() -> None:
    st.subheader("Convertir archivos")
    uploads = st.file_uploader(
        "Selecciona uno o mas documentos",
        type=SUPPORTED_TYPE_NAMES,
        accept_multiple_files=True,
    )

    col_a, col_b = st.columns([1, 2])
    with col_a:
        convert_clicked = st.button("Convertir", type="primary", use_container_width=True)
    with col_b:
        st.caption("Los resultados se guardan en work\\streamlit_app\\converted.")

    if not uploads:
        st.info(
            "Carga PDFs, Office, HTML, texto, datos o archivos comprimidos para generar "
            "Markdown."
        )
        return

    if convert_clicked:
        try:
            validate_named_sizes(
                [(upload.name, len(upload.getvalue())) for upload in uploads],
                FILE_LIMITS,
            )
        except ValueError as exc:
            st.error(str(exc))
            return

        for upload in uploads:
            try:
                output_path, markdown = convert_upload(upload.name, upload.getvalue())
                st.success(f"{upload.name} convertido")
                st.download_button(
                    "Descargar Markdown",
                    data=markdown,
                    file_name=output_path.name,
                    mime="text/markdown",
                    key=f"download-{output_path.name}",
                )
                st.text_area(
                    f"Vista previa: {output_path.name}",
                    markdown[:12000],
                    height=320,
                    key=f"preview-{output_path.name}",
                )
            except Exception as exc:
                append_manifest(
                    APP_MANIFEST,
                    MANIFEST_FIELDS,
                    {
                        "source_name": upload.name,
                        "source_hash": sha256_bytes(upload.getvalue()),
                        "input_path": "",
                        "output_path": "",
                        "status": "error",
                        "converted_at": datetime.now().isoformat(timespec="seconds"),
                        "error": str(exc),
                    }
                )
                st.error(f"No se pudo convertir {upload.name}: {exc}")


def render_pipeline_tab() -> None:
    st.subheader("Pipeline por carpetas")
    input_dir = st.text_input("Carpeta de entrada", value=str(DEFAULT_PIPELINE_INPUT))
    output_dir = st.text_input("Carpeta de salida", value=str(DEFAULT_PIPELINE_OUTPUT))
    log_dir = st.text_input("Carpeta de logs", value=str(DEFAULT_PIPELINE_LOGS))
    force = st.checkbox("Forzar reconversion", value=False)

    if st.button("Ejecutar pipeline", type="primary"):
        command = [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(PIPELINE_SCRIPT),
            "-InputDir",
            input_dir,
            "-OutputDir",
            output_dir,
            "-LogDir",
            log_dir,
        ]
        if force:
            command.append("-Force")

        completed = subprocess.run(
            command,
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            timeout=900,
        )

        if completed.returncode == 0:
            st.success("Pipeline ejecutado")
        else:
            st.error("El pipeline finalizo con errores")

        output = "\n".join(part for part in [completed.stdout, completed.stderr] if part)
        st.code(output or "Sin salida de consola", language="powershell")


def render_history_tab() -> None:
    st.subheader("Historial")
    app_rows = read_manifest(APP_MANIFEST)
    pipeline_manifest = DEFAULT_PIPELINE_LOGS / "manifest.csv"
    pipeline_rows = read_manifest(pipeline_manifest)

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Conversiones UI", len(app_rows))
    col_b.metric("Registros pipeline", len(pipeline_rows))
    col_c.metric("Errores UI", sum(1 for row in app_rows if row.get("status") == "error"))

    if app_rows:
        st.markdown("Conversiones desde la interfaz")
        st.dataframe(list(reversed(app_rows)), use_container_width=True, hide_index=True)

    if pipeline_rows:
        st.markdown("Manifest del pipeline")
        st.dataframe(list(reversed(pipeline_rows)), use_container_width=True, hide_index=True)

    if not app_rows and not pipeline_rows:
        st.info("Todavia no hay conversiones registradas.")


def main() -> None:
    ensure_dirs()
    st.set_page_config(
        page_title="MarkItDown Workbench",
        page_icon=None,
        layout="wide",
    )
    render_css()

    st.title("MarkItDown Workbench")
    st.caption(
        "Conversion de documentos a Markdown para analisis, busqueda y pipelines "
        "documentales."
    )

    tab_convert, tab_pipeline, tab_history = st.tabs(["Convertir", "Pipeline", "Historial"])
    with tab_convert:
        render_converter_tab()
    with tab_pipeline:
        render_pipeline_tab()
    with tab_history:
        render_history_tab()


if __name__ == "__main__":
    main()
