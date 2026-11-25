function lerDados(id) {
    const elemento = document.getElementById(id);
    return elemento ? JSON.parse(elemento.textContent) : null;
}

const CORES = ['#4B2A63', '#8E6BAA', '#C9B8D8'];

Chart.defaults.font.family = "'IBM Plex Sans', system-ui, sans-serif";
Chart.defaults.color = '#6E6577';
Chart.defaults.borderColor = '#E2DFEA';

function graficoDeBarras(canvasId, dados, rotulo, campoRotulo) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !dados) return;
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: dados.map(d => d[campoRotulo]),
            datasets: [{ label: rotulo, data: dados.map(d => d.total), backgroundColor: CORES, borderRadius: 6, maxBarThickness: 56 }],
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
