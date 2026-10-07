(function () {
  "use strict";

  const money = (n) =>
    n == null ? "—" : n.toLocaleString("es-MX", { style: "currency", currency: "MXN", maximumFractionDigits: 0 });

  const state = {
    data: [],
    municipioActivo: "",
    busqueda: "",
    orden: "bruto_desc",
  };

  const els = {
    stats: document.getElementById("stats"),
    chips: document.getElementById("chips"),
    buscar: document.getElementById("buscar"),
    municipio: document.getElementById("municipio"),
    orden: document.getElementById("orden"),
    tbody: document.getElementById("tbody"),
    conteo: document.getElementById("conteo"),
    vacio: document.getElementById("vacio"),
    exportar: document.getElementById("exportar"),
  };

  function normaliza(s) {
    return (s || "")
      .toString()
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "");
  }

  function municipiosOrdenados(data) {
    const conteo = new Map();
    for (const r of data) conteo.set(r.municipio, (conteo.get(r.municipio) || 0) + 1);
    return [...conteo.entries()].sort((a, b) => b[1] - a[1]);
  }

  function construirControles() {
    const municipios = municipiosOrdenados(state.data);

    for (const [m] of [...municipios].sort((a, b) => a[0].localeCompare(b[0], "es"))) {
      const opt = document.createElement("option");
      opt.value = m;
      opt.textContent = m;
      els.municipio.appendChild(opt);
    }

    els.chips.innerHTML = "";
    for (const [m, n] of municipios) {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "chip";
      chip.textContent = `${m} (${n})`;
      chip.dataset.municipio = m;
      chip.addEventListener("click", () => {
        state.municipioActivo = state.municipioActivo === m ? "" : m;
        els.municipio.value = state.municipioActivo;
        render();
      });
      els.chips.appendChild(chip);
    }
  }

  function filtrar() {
    const q = normaliza(state.busqueda);
    return state.data.filter((r) => {
      if (state.municipioActivo && r.municipio !== state.municipioActivo) return false;
      if (!q) return true;
      return normaliza(r.nombre).includes(q) || normaliza(r.puesto).includes(q) || normaliza(r.plantel).includes(q);
    });
  }

  function ordenar(lista) {
    const by = {
      bruto_desc: (a, b) => (b.sueldo_bruto ?? -1) - (a.sueldo_bruto ?? -1),
      bruto_asc: (a, b) => (a.sueldo_bruto ?? 1e15) - (b.sueldo_bruto ?? 1e15),
      neto_desc: (a, b) => (b.sueldo_neto ?? -1) - (a.sueldo_neto ?? -1),
      nombre_asc: (a, b) => a.nombre.localeCompare(b.nombre, "es"),
      municipio_asc: (a, b) => a.municipio.localeCompare(b.municipio, "es") || (b.sueldo_bruto ?? -1) - (a.sueldo_bruto ?? -1),
    };
    return [...lista].sort(by[state.orden] || by.bruto_desc);
  }

  function renderStats(lista) {
    const brutos = lista.map((r) => r.sueldo_bruto).filter((n) => n != null);
    const promedio = brutos.length ? brutos.reduce((a, b) => a + b, 0) / brutos.length : 0;
    const total = brutos.reduce((a, b) => a + b, 0);
    const municipiosCount = new Set(lista.map((r) => r.municipio)).size;

    els.stats.innerHTML = `
      <div class="stat"><div class="n">${lista.length}</div><div class="label">Personas en este filtro</div></div>
      <div class="stat"><div class="n">${municipiosCount}</div><div class="label">Municipios representados</div></div>
      <div class="stat"><div class="n">${money(promedio)}</div><div class="label">Sueldo bruto promedio</div></div>
      <div class="stat"><div class="n">${money(total)}</div><div class="label">Suma de sueldos brutos (nómina mensual)</div></div>
    `;
  }

  function renderTabla(lista) {
    els.tbody.innerHTML = "";
    els.conteo.textContent = lista.length;
    els.vacio.hidden = lista.length !== 0;

    const frag = document.createDocumentFragment();
    for (const r of lista) {
      const tr = document.createElement("tr");
      const confianza =
        r.municipio_confianza === "estimada"
          ? '<span class="badge-confianza" title="Municipio inferido de una fuente secundaria, no de un directorio oficial vigente">municipio estimado</span>'
          : "";
      tr.innerHTML = `
        <td>${escapeHtml(r.nombre)}</td>
        <td>${escapeHtml(r.puesto)}</td>
        <td>${escapeHtml(r.plantel)}</td>
        <td>${escapeHtml(r.municipio)}${confianza}</td>
        <td>${escapeHtml(r.direccion)}</td>
        <td>${escapeHtml(r.sexo)}</td>
        <td class="money">${money(r.sueldo_bruto)}</td>
        <td class="money">${money(r.sueldo_neto)}</td>
      `;
      frag.appendChild(tr);
    }
    els.tbody.appendChild(frag);
  }

  function escapeHtml(s) {
    return (s ?? "").toString().replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  function render() {
    const filtrada = ordenar(filtrar());
    renderStats(filtrada);
    renderTabla(filtrada);

    for (const chip of els.chips.querySelectorAll(".chip")) {
      chip.classList.toggle("active", chip.dataset.municipio === state.municipioActivo);
    }
  }

  function exportarCSV() {
    const lista = ordenar(filtrar());
    const headers = ["Nombre", "Puesto", "Plantel", "Municipio", "Municipio (confianza)", "Direccion", "Sexo", "Sueldo bruto mensual", "Sueldo neto mensual"];
    const filas = lista.map((r) => [
      r.nombre, r.puesto, r.plantel, r.municipio, r.municipio_confianza,
      r.direccion || "", r.sexo, r.sueldo_bruto ?? "", r.sueldo_neto ?? "",
    ]);

    const csvEscape = (v) => {
      const s = String(v ?? "");
      return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    };

    const csv = [headers, ...filas].map((row) => row.map(csvEscape).join(",")).join("\r\n");
    const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    const etiqueta = state.municipioActivo ? `_${state.municipioActivo.replace(/\s+/g, "-")}` : "";
    a.href = url;
    a.download = `sueldos_conalep_jalisco${etiqueta}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  els.buscar.addEventListener("input", (e) => {
    state.busqueda = e.target.value;
    render();
  });
  els.municipio.addEventListener("change", (e) => {
    state.municipioActivo = e.target.value;
    render();
  });
  els.orden.addEventListener("change", (e) => {
    state.orden = e.target.value;
    render();
  });
  els.exportar.addEventListener("click", exportarCSV);

  fetch("data/data.json")
    .then((r) => r.json())
    .then((data) => {
      state.data = data;
      construirControles();
      render();
    })
    .catch((err) => {
      els.tbody.innerHTML = `<tr><td colspan="8">No se pudieron cargar los datos: ${escapeHtml(err.message)}</td></tr>`;
    });
})();
