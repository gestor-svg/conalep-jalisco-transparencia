# Sueldos CONALEP Jalisco — Transparencia

Página pública (estática, sin backend) para buscar, agrupar por municipio,
ordenar por ingreso y exportar a CSV las remuneraciones de personas servidoras
públicas de **CONALEP Jalisco** (Colegio de Educación Profesional Técnica del
Estado de Jalisco), con base en su obligación de transparencia "SUELDOS",
formato 46307 ("Remuneraciones brutas y netas...").

## Qué cubre y qué no

- **Solo CONALEP Jalisco.** El archivo fuente que se usó para esta página es
  exclusivamente de esa institución — no de todas las dependencias del
  estado de Jalisco. Si se quiere ampliar a otras dependencias, hay que
  descargar su propio formato 46307 desde la Plataforma Nacional de
  Transparencia y agregarlo (ver "Cómo actualizar los datos" abajo).
- **Periodo:** agosto 2026 (único periodo presente en el archivo fuente).
- **El archivo original llegó incompleto.** La descarga se cortó antes de
  cerrarse el JSON. Se recuperaron **550 registros íntegros**; es probable
  que falten algunos más al final del archivo. El script de build (
  `scripts/build_data.py`) descarta de forma silenciosa cualquier fila
  truncada, así que nunca rompe por esto — pero los 550 no son
  necesariamente el 100% de la plantilla.

## Municipio: de dónde sale

El formato oficial **no incluye municipio**, solo "Área de adscripción"
(el plantel/oficina). Para 18 de los 20 planteles el nombre del plantel ya es
inequívocamente un municipio real de Jalisco (ej. "TLAQUEPAQUE", "ARANDAS",
"LAGOS DE MORENO"). Dos quedaron sin una fuente oficial y vigente:

| Plantel (tal cual en el archivo) | Municipio asignado | Fuente |
|---|---|---|
| CENTRO MEXICANO ITALIANO | Zapopan | Tesis UNAM que lo referencia como "Centro Mexicano-Italiano del Conalep en Zapopan, Jalisco" — no un directorio oficial vigente. |
| JOSE MARIA MARTINEZ | Mazamitla | Listado de datos escolares de terceros ("CONALEP JOSE MA. MARTINEZ R.", municipio Mazamitla) — fuente secundaria, no un directorio oficial. |

Estos dos se marcan en la página con la etiqueta **"municipio estimado"**.
Si tienes el directorio oficial vigente de CONALEP Jalisco, avisa para
corregir `PLANTEL_A_MUNICIPIO` en `scripts/build_data.py`.

## Dirección / geolocalización

El formato oficial de sueldos **nunca incluye domicilio ni coordenadas** —
no es parte de la obligación de transparencia "SUELDOS". Se buscaron
direcciones públicas por fuera y solo se encontraron para 4 de los 20
planteles, con fuentes de fechas distintas:

| Plantel | Dirección | Fuente / año |
|---|---|---|
| Dirección General | Av. Salvador Vargas 3035, Paseos del Sol 1a Sección, Zapopan, Jalisco, C.P. 45079 | Documento de planeación estatal, 2024 |
| Acatlán de Juárez | Av. CONALEP No. 5, Col. El Plan, Acatlán de Juárez, Jalisco, C.P. 45700 | Manual de servicios CONALEP Jalisco, 2017 (puede estar desactualizada) |
| Arandas | Presidente Gustavo Díaz Ordaz No. 40, Col. Linda Vista, Arandas, Jalisco, C.P. 47180 | Mismo manual, 2017 |
| Jalostotitlán | Prolongación a Tierras Blancas s/n, La Manzanilla, Jalostotitlán, Jalisco, C.P. 47120 | Mismo manual, 2017 |

No se generaron coordenadas GPS para ningún plantel — no había ninguna
dirección confiable que geocodificar para el resto, y adivinar coordenadas
en un sitio público habría sido peor que no mostrar nada.

## Cómo actualizar los datos

1. Descarga el/los archivo(s) completos de la Plataforma Nacional de
   Transparencia (formato 46307) y colócalos en `data/raw/` (puedes dejar
   varios archivos `.json` ahí, el script los junta todos).
2. Corre:
   ```bash
   python scripts/build_data.py
   ```
3. Esto regenera `data/data.json` y `data/data.csv`. Commitea y publica
   (push a `main` si usas GitHub Pages desde esa rama).

## Desarrollo local

Es un sitio 100% estático (HTML/CSS/JS, sin build step ni dependencias).
Para verlo localmente basta un servidor estático simple, por ejemplo:

```bash
python -m http.server 8000
```

y abrir `http://localhost:8000`.

## Aviso

Esta página no es un sitio oficial de CONALEP ni del Gobierno de Jalisco.
Reempaqueta datos públicos de transparencia gubernamental para facilitar su
consulta ciudadana.
