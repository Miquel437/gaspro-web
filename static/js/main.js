// GasPro Web - JavaScript principal

// Calculador de bateria (des de la pàgina d'inici)
function calcularBateria() {
    const gas = document.getElementById('bat-gas').value;
    const potencia = parseFloat(document.getElementById('bat-potencia').value);
    const hores = parseFloat(document.getElementById('bat-hores').value);
    const temp = parseFloat(document.getElementById('bat-temp').value);

    fetch('/api/calcular-bateria', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({gas, potencia_kw: potencia, hores_dia: hores, temperatura: temp})
    })
    .then(r => r.json())
    .then(data => {
        const div = document.getElementById('bat-resultat');
        div.style.display = 'block';
        let html = `<div class="alert alert-info">
            <strong>Consum:</strong> ${data.consum_diari} m³/dia
        </div>`;
        html += '<table class="table table-sm table-bordered">';
        html += '<thead><tr><th>Bombona</th><th>kg</th><th>m³/bombona</th><th>Durada</th><th>Bateria</th></tr></thead><tbody>';
        data.bombones.forEach(b => {
            html += `<tr>
                <td>${b.bombona}</td>
                <td>${b.kg}</td>
                <td>${b.m3_bombona}</td>
                <td>${b.dies_durada} dies</td>
                <td><strong>${b.bateria_recomanada} unitats</strong></td>
            </tr>`;
        });
        html += '</tbody></table>';
        div.innerHTML = html;
    })
    .catch(err => {
        document.getElementById('bat-resultat').style.display = 'block';
        document.getElementById('bat-resultat').innerHTML =
            `<div class="alert alert-danger">Error: ${err.message}</div>`;
    });
}
