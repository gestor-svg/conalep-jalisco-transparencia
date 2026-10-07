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

## Municipio y dirección: de dónde salen

El formato oficial de sueldos **no incluye ni municipio ni domicilio**, solo
"Área de adscripción" (el nombre del plantel). **El nombre del plantel no
siempre coincide con su municipio real** — por ejemplo "Guadalajara 1" está
físicamente en Tlaquepaque, y "José María Martínez" (nombre oficial completo
"Tamazula José Ma. Martínez R.") está en Tamazula de Gordiano, no en
Guadalajara ni en Mazamitla.

Por eso el municipio y la dirección de cada uno de los 20 planteles se
verificaron el **7 de octubre de 2026** visitando una por una las páginas del
[directorio oficial de planteles de CONALEP Jalisco](https://www.conalepjalisco.edu.mx/web/index.php/conocenos/planteles-jalisco)
(sitio oficial y vigente de la institución, sección "Ubicación" de cada
plantel). Es la misma fuente para los 20, con una sola excepción:

| Plantel | Municipio | Dirección | Fuente |
|---|---|---|---|
| Guadalajara 1 | Tlaquepaque | Calle Bajío No. 115, Col. Las Juntas, C.P. 45590 | conalepjalisco.edu.mx, 2026 |
| Guadalajara 2 | Guadalajara | Calle Isla Salomón No. 2553, Col. Jardines del Sur, C.P. 44950 | conalepjalisco.edu.mx, 2026 |
| Guadalajara 3 | Guadalajara | Prolongación Av. Patria S/N, Col. Rancho Nuevo, C.P. 44240 | conalepjalisco.edu.mx, 2026 |
| Tlaquepaque | Tlaquepaque | Esteban Ramírez No. 220, Col. Residencial La Soledad, C.P. 45525 | conalepjalisco.edu.mx, 2026 |
| Tonalá | Tonalá | Dunas Norte No. 180, Col. Lomas del Camichín, C.P. 45417 | conalepjalisco.edu.mx, 2026 |
| Zapopan | Zapopan | Francisco Villa S/N, Esq. Av. Patria, Col. Loma Bonita Ejidal, C.P. 45085 | conalepjalisco.edu.mx, 2026 |
| Centro Mexicano Italiano | Zapopan | Felipe Ruvalcaba S/N, Col. Paseos del Sol, C.P. 45070 | conalepjalisco.edu.mx, 2026 |
| CAST Zapopan | Zapopan | (sin domicilio publicado; oficina confirmada en Zapopan por el directorio oficial y su lada local) | conalepjalisco.edu.mx, 2026 |
| Acatlán de Juárez | Acatlán de Juárez | Avenida Conalep No. 5, Col. El Plan, C.P. 45700 | conalepjalisco.edu.mx, 2026 |
| Arandas | Arandas | Gustavo Díaz Ordaz No. 40, Col. Lindavista, C.P. 47180 | conalepjalisco.edu.mx, 2026 |
| Chapala | Chapala | Carretera Libramiento Chapala-Ajijic No. 202, C.P. 45900 | conalepjalisco.edu.mx, 2026 |
| Jalostotitlán | Jalostotitlán | Calle Loma del Realengo S/N, Col. La Manzanilla, C.P. 47120 | conalepjalisco.edu.mx, 2026 |
| Juanacatlán | Juanacatlán | Km 1 Carr. Ex Hacienda de Zapotlanejo S/N, Col. Tateposco, C.P. 45880 | conalepjalisco.edu.mx, 2026 |
| La Barca | La Barca | Avenida Conalep No. 90, Col. San Antonio, C.P. 47910 | conalepjalisco.edu.mx, 2026 |
| Lagos de Moreno | Lagos de Moreno | Avenida Conalep S/N, Carr. Lagos-La Unión, C.P. 47480 | conalepjalisco.edu.mx, 2026 |
| Puerto Vallarta | Puerto Vallarta | Calle Viena No. 111, Fracc. Las Gaviotas, C.P. 48310 | conalepjalisco.edu.mx, 2026 |
| Puerto Vallarta II | Puerto Vallarta | Calle Federación No. 412, Col. Colinas Universitarias, C.P. 48280 | conalepjalisco.edu.mx, 2026 |
| Tapalpa | Tapalpa | Calle Durazno No. 288, Localidad Atacco, C.P. 49340 | conalepjalisco.edu.mx, 2026 |
| José María Martínez | Tamazula de Gordiano | Salvador Esquer Apodaca No. 36, Col. Obrera Benito Juárez 2da Etapa, C.P. 49653 | conalepjalisco.edu.mx, 2026 |
| Dirección General | Zapopan | Av. Salvador Vargas 3035, Paseos del Sol 1a Sección, C.P. 45079 | Documento de planeación estatal, 2024 (no está en la sección de planteles del sitio de CONALEP) |

No se generaron coordenadas GPS para ningún plantel — el sitio oficial
muestra cada ubicación en un mapa embebido en vez de publicar lat/long, y
geocodificar por fuera habría sido una capa extra de incertidumbre que no
hacía falta para resolver "¿en qué municipio está esto?".

**Nota sobre una corrección:** una primera versión de este archivo ubicaba
"José María Martínez" en Mazamitla, tomado de una fuente secundaria (un
listado de datos escolares de terceros). Al verificar contra el sitio oficial
de CONALEP Jalisco se confirmó que es incorrecto — el plantel real es
Tamazula de Gordiano. Mazamitla sí es un módulo real de CONALEP Jalisco, pero
no aparece como "Área de adscripción" en el archivo de sueldos usado aquí.

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
