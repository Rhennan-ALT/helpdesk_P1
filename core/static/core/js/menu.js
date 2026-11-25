(function () {
    const sidebar = document.getElementById('sidebar');
    const fundo = document.querySelector('.sidebar-fundo');
    if (!sidebar) return;

    function alternar(aberto) {
        sidebar.classList.toggle('aberta', aberto);
        fundo.classList.toggle('visivel', aberto);
    }

    document.querySelectorAll('[data-menu-abrir]').forEach(el => el.addEventListener('click', () => alternar(true)));
    document.querySelectorAll('[data-menu-fechar]').forEach(el => el.addEventListener('click', () => alternar(false)));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') alternar(false); });
})();
