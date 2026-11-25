function lerDados(id) {
    const elemento = document.getElementById(id);
    return elemento ? JSON.parse(elemento.textContent) : null;
}

const CORES = ['#4B2A63', '#BBAAB8', '#292643', '#7A5A9A', '#D9D9D9'];

function graficoDeBarras(canvasId, dados, rotulo, campoRotulo) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !dados) return;
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: dados.map(d => d[campoRotulo]),
            datasets: [{ label: rotulo, data: dados.map(d => d.total), backgroundColor: CORES }],
        },
        options: {
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
        },
    });
}

function graficoDeLinha(canvasId, dados) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !dados) return;
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: dados.map(d => d.mes),
            datasets: [{
                label: 'Chamados',
                data: dados.map(d => d.total),
                borderColor: CORES[0],
                backgroundColor: CORES[0],
                tension: 0.2,
            }],
        },
        options: {
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
        },
    });
}

graficoDeBarras('grafico-status', lerDados('dados-status'), 'Chamados', 'rotulo');
graficoDeBarras('grafico-tipo', lerDados('dados-tipo'), 'Chamados', 'rotulo');
graficoDeLinha('grafico-mes', lerDados('dados-mes'));
