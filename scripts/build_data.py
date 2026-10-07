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
# Verificado el 2026-10-07 visitando una por una las 20 páginas de plantel en
# conalepjalisco.edu.mx (sitio oficial, vigente), que publica domicilio físico
# por plantel. "alta" = tomado directo de esa fuente oficial. La excepción es
# DIRECCION GENERAL, cuyo domicilio no está en esa sección del sitio y se tomó
# de un documento de planeación estatal 2024 (ver PLANTEL_DIRECCION).
#
# OJO: el nombre del plantel NO siempre coincide con su municipio real -
# "Guadalajara 1" está físicamente en Tlaquepaque, y "Jose Maria Martinez"
# (nombre completo oficial "Tamazula José Ma. Martínez R.") está en Tamazula
# de Gordiano, no en Mazamitla como se había estimado en una primera pasada
# con fuentes secundarias - corregido tras verificar contra el sitio oficial.
PLANTEL_A_MUNICIPIO = {
    "CENTRO MEXICANO ITALIANO": ("Zapopan", "alta"),
    "TLAQUEPAQUE": ("Tlaquepaque", "alta"),
    "DIRECCION GENERAL": ("Zapopan", "alta"),
    "PUERTO VALLARTA": ("Puerto Vallarta", "alta"),
    "GUADALAJARA 2": ("Guadalajara", "alta"),
    "LAGOS DE MORENO": ("Lagos de Moreno", "alta"),
    "JOSE MARIA MARTINEZ": ("Tamazula de Gordiano", "alta"),
    "TONALA": ("Tonalá", "alta"),
    "ZAPOPAN": ("Zapopan", "alta"),
    "GUADALAJARA 3": ("Guadalajara", "alta"),
    "GUADALAJARA 1": ("Tlaquepaque", "alta"),
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

# Direcciones oficiales por plantel, tomadas el 2026-10-07 de la sección
# "Ubicación" de cada página de plantel en conalepjalisco.edu.mx (sitio oficial
# y vigente de CONALEP Jalisco), salvo donde se indica otra fuente. El formato
# de sueldos nunca trae domicilio - esto es un enriquecimiento con datos
# públicos de otra obligación/fuente del mismo sujeto obligado. Sin coordenadas
# GPS: no se geocodificó nada.
PLANTEL_DIRECCION = {
    "GUADALAJARA 1": ("Calle Bajío No. 115, Col. Las Juntas, Tlaquepaque, Jalisco, C.P. 45590", 2026),
    "GUADALAJARA 2": ("Calle Isla Salomón No. 2553, Col. Jardines del Sur, Guadalajara, Jalisco, C.P. 44950", 2026),
    "GUADALAJARA 3": ("Prolongación Av. Patria S/N, Col. Rancho Nuevo, Guadalajara, Jalisco, C.P. 44240", 2026),
    "TLAQUEPAQUE": ("Esteban Ramírez No. 220, Esq. J. Álvarez del Castillo, Col. Residencial La Soledad, Tlaquepaque, Jalisco, C.P. 45525", 2026),
    "TONALA": ("Dunas Norte No. 180, Col. Lomas del Camichín, Tonalá, Jalisco, C.P. 45417", 2026),
    "ZAPOPAN": ("Francisco Villa S/N, Esq. Av. Patria, Col. Loma Bonita Ejidal, Zapopan, Jalisco, C.P. 45085", 2026),
    "CENTRO MEXICANO ITALIANO": ("Felipe Ruvalcaba S/N, Col. Paseos del Sol, Zapopan, Jalisco, C.P. 45070", 2026),
    "ACATLAN DE JUAREZ": ("Avenida Conalep No. 5, Col. El Plan, Acatlán de Juárez, Jalisco, C.P. 45700", 2026),
    "ARANDAS": ("Gustavo Díaz Ordaz No. 40, Col. Lindavista, Arandas, Jalisco, C.P. 47180", 2026),
    "CHAPALA": ("Carretera Libramiento Chapala-Ajijic No. 202, Chapala, Jalisco, C.P. 45900", 2026),
    "JALOSTOTITLAN": ("Calle Loma del Realengo S/N, Col. La Manzanilla, Jalostotitlán, Jalisco, C.P. 47120", 2026),
    "JUANACATLAN": ("Km 1 Carretera Ex Hacienda de Zapotlanejo S/N, Col. Tateposco, Juanacatlán, Jalisco, C.P. 45880", 2026),
    "LA BARCA": ("Avenida Conalep No. 90, Col. San Antonio, La Barca, Jalisco, C.P. 47910", 2026),
    "LAGOS DE MORENO": ("Avenida Conalep S/N, Carr. Lagos-La Unión, Lagos de Moreno, Jalisco, C.P. 47480", 2026),
    "PUERTO VALLARTA": ("Calle Viena No. 111, Esq. Av. Fco. Villa, Fracc. Las Gaviotas, Puerto Vallarta, Jalisco, C.P. 48310", 2026),
    "PUERTO VALLARTA II": ("Calle Federación No. 412, Col. Colinas Universitarias, Puerto Vallarta, Jalisco, C.P. 48280", 2026),
    "TAPALPA": ("Calle Durazno No. 288, Localidad Atacco, Tapalpa, Jalisco, C.P. 49340", 2026),
    "JOSE MARIA MARTINEZ": ("Salvador Esquer Apodaca No. 36, Col. Obrera Benito Juárez 2da Etapa, Tamazula de Gordiano, Jalisco, C.P. 49653", 2026),
    "DIRECCION GENERAL": ("Av. Salvador Vargas 3035, Paseos del Sol 1a Sección, Zapopan, Jalisco, C.P. 45079", 2024),
    # CAST Zapopan: el directorio oficial confirma oficina activa en Zapopan
    # (directorio-dg del sitio), pero su página de plantel no publica domicilio.
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
