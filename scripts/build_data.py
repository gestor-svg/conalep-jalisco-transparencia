"""
Convierte el export oficial (formato 46307, Plataforma Nacional de Transparencia)
de remuneraciones de CONALEP Jalisco en un data/data.json + data/data.csv planos,
listos para la pagina web.

El archivo fuente (data/raw/detalle_formato_46307_parte1.json) llego truncado
(se corto la descarga antes de cerrar el JSON), asi que este script lee fila
por fila en vez de usar json.load() sobre el archivo completo: cada fila de
"filas" esta en su propia linea en el pretty-print original, así que una fila
incompleta al final simplemente se descarta sin tronar el resto.

Vuelve a correr este script cuando tengas una descarga completa del archivo
(o partes adicionales) para regenerar los datos de la pagina.
"""
import csv
import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
OUT_JSON = ROOT / "data" / "data.json"
OUT_CSV = ROOT / "data" / "data.csv"

# Columnas reales del formato (0-indexed), confirmadas contra el archivo fuente.
COL_PUESTO = 5
COL_AREA = 7
COL_NOMBRE = 8
COL_AP1 = 9
COL_AP2 = 10
COL_SEXO = 11
COL_BRUTO = 12
COL_NETO = 14
COL_TIPO_INTEGRANTE = 3
COL_FECHA_ACT = 30

# Plantel/área de adscripción (tal cual en el archivo) -> municipio real.
# "alta" = el nombre del plantel ya es el municipio, sin ambigüedad.
# "estimada" = municipio inferido de una fuente secundaria, no un directorio
#   oficial de CONALEP Jalisco con domicilios vigentes - puede estar desactualizado
#   o ser incorrecto. Ver README.md para el detalle y las fuentes.
PLANTEL_A_MUNICIPIO = {
    "CENTRO MEXICANO ITALIANO": ("Zapopan", "estimada"),
    "TLAQUEPAQUE": ("Tlaquepaque", "alta"),
    "DIRECCION GENERAL": ("Zapopan", "alta"),
    "PUERTO VALLARTA": ("Puerto Vallarta", "alta"),
    "GUADALAJARA 2": ("Guadalajara", "alta"),
    "LAGOS DE MORENO": ("Lagos de Moreno", "alta"),
    "JOSE MARIA MARTINEZ": ("Mazamitla", "estimada"),
    "TONALA": ("Tonalá", "alta"),
    "ZAPOPAN": ("Zapopan", "alta"),
    "GUADALAJARA 3": ("Guadalajara", "alta"),
    "GUADALAJARA 1": ("Guadalajara", "alta"),
    "JUANACATLAN": ("Juanacatlán", "alta"),
    "ACATLAN DE JUAREZ": ("Acatlán de Juárez", "alta"),
    "ARANDAS": ("Arandas", "alta"),
    "CHAPALA": ("Chapala", "alta"),
    "PUERTO VALLARTA II": ("Puerto Vallarta", "alta"),
    "JALOSTOTITLAN": ("Jalostotitlán", "alta"),
    "LA BARCA": ("La Barca", "alta"),
    "CAST ZAPOPAN": ("Zapopan", "alta"),
    "TAPALPA": ("Tapalpa", "alta"),
}

# Direcciones publicas encontradas para algunos planteles (ver README para fuentes
# y fecha). No se intento geocodificar / no hay coordenadas GPS: el formato
# oficial de sueldos nunca trae domicilio, estas son de fuentes externas sueltas.
PLANTEL_DIRECCION = {
    "ACATLAN DE JUAREZ": ("Av. CONALEP No. 5, Col. El Plan, Acatlán de Juárez, Jalisco, C.P. 45700", 2017),
    "ARANDAS": ("Presidente Gustavo Díaz Ordaz No. 40, Col. Linda Vista, Arandas, Jalisco, C.P. 47180", 2017),
    "JALOSTOTITLAN": ("Prolongación a Tierras Blancas s/n, La Manzanilla, Jalostotitlán, Jalisco, C.P. 47120", 2017),
    "DIRECCION GENERAL": ("Av. Salvador Vargas 3035, Paseos del Sol 1a Sección, Zapopan, Jalisco, C.P. 45079", 2024),
}


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def parse_rows_tolerant(path: Path):
    """Lee 'filas' línea por línea; una fila truncada al final se descarta sola."""
    with path.open(encoding="utf-8") as f:
        lines = f.readlines()

    start = None
    for i, line in enumerate(lines):
        if line.strip() == '"filas": [':
            start = i + 1
            break
    if start is None:
        raise ValueError(f"No se encontró el inicio de 'filas' en {path}")

    rows = []
    skipped = 0
    for line in lines[start:]:
        s = line.strip()
        if not s or s in ("]", "}", "],", "]}"):
            continue
        if s.endswith(","):
            s = s[:-1]
        try:
            rows.append(json.loads(s))
        except json.JSONDecodeError:
            skipped += 1
    return rows, skipped


def build():
    raw_files = sorted(RAW_DIR.glob("*.json"))
    if not raw_files:
        print(f"No hay archivos fuente en {RAW_DIR}", file=sys.stderr)
        sys.exit(1)

    records = []
    seen_names = set()
    total_skipped = 0

    for rf in raw_files:
        rows, skipped = parse_rows_tolerant(rf)
        total_skipped += skipped
        print(f"{rf.name}: {len(rows)} filas completas, {skipped} descartadas por corte/truncado")

        for r in rows:
            plantel_raw = r[COL_AREA]
            municipio, confianza = PLANTEL_A_MUNICIPIO.get(plantel_raw, (plantel_raw.title(), "desconocida"))
            direccion, direccion_anio = PLANTEL_DIRECCION.get(plantel_raw, (None, None))

            # El archivo fuente trae algunos "0" literales como placeholder de
            # segundo apellido vacío (error de captura de CONALEP, no de este script).
            PLACEHOLDERS = {"", "0", "NO DATO", "N/A", "S/N"}
            nombre_completo = " ".join(
                p.strip() for p in (r[COL_NOMBRE], r[COL_AP1], r[COL_AP2])
                if p and p.strip().upper() not in PLACEHOLDERS
            )
            key = (nombre_completo, plantel_raw)
            if key in seen_names:
                continue  # evita duplicar si dos partes del archivo se traslaparan
            seen_names.add(key)

            records.append({
                "nombre": nombre_completo,
                "puesto": r[COL_PUESTO],
                "plantel": plantel_raw.title(),
                "municipio": municipio,
                "municipio_confianza": confianza,
                "direccion": direccion,
                "direccion_anio": direccion_anio,
                "sexo": r[COL_SEXO],
                "sueldo_bruto": float(r[COL_BRUTO]) if r[COL_BRUTO] not in (None, "") else None,
                "sueldo_neto": float(r[COL_NETO]) if r[COL_NETO] not in (None, "") else None,
                "fecha_actualizacion": r[COL_FECHA_ACT],
            })

    records.sort(key=lambda x: (x["sueldo_bruto"] is None, -(x["sueldo_bruto"] or 0)))

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = [
        "nombre", "puesto", "plantel", "municipio", "municipio_confianza",
        "direccion", "direccion_anio", "sexo", "sueldo_bruto", "sueldo_neto",
        "fecha_actualizacion",
    ]
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"\nTotal registros únicos: {len(records)}")
    print(f"Total filas descartadas por truncado/corte: {total_skipped}")
    print(f"Escrito: {OUT_JSON}")
    print(f"Escrito: {OUT_CSV}")


if __name__ == "__main__":
    build()
