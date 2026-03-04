let anomalies = [];

// Chart.js setup
const severityDonut = new Chart(document.getElementById('severityDonut').getContext('2d'), {
    type: 'doughnut',
    data: { labels: ['Low', 'Medium', 'High'], datasets: [{ data: [0,0,0], backgroundColor: ['#28a745','#fd7e14','#dc3545'] }] },
    options: { plugins: { legend: { position: 'bottom' } } }
});

const anomalyTrend = new Chart(document.getElementById('anomalyTrend').getContext('2d'), {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'Anomaly Score', data: [], borderColor: '#0dcaf0', backgroundColor:'rgba(13,202,240,0.2)', fill:true }] },
    options: { responsive:true }
});

const heartRateChart = new Chart(document.getElementById('heartRateChart').getContext('2d'), {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'Heart Rate', data: [], borderColor:'#dc3545', fill:false }] }
});

const spo2Chart = new Chart(document.getElementById('spo2Chart').getContext('2d'), {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'SpO₂', data: [], borderColor:'#20c997', fill:false }] }
});

const tempChart = new Chart(document.getElementById('tempChart').getContext('2d'), {
    type: 'bar',
    data: { labels: [], datasets: [{ label: 'Temperature', data: [], backgroundColor:'#fd7e14' }] }
});

const bpChart = new Chart(document.getElementById('bpChart').getContext('2d'), {
    type: 'line',
    data: { labels: [], datasets: [
        { label: 'Systolic', data: [], borderColor:'#7b2ff7', fill:false },
        { label: 'Diastolic', data: [], borderColor:'#f2709c', fill:false }
    ]}
});

function renderTable() {
    const tbody = document.querySelector('#anomalyTable tbody');
    tbody.innerHTML = '';
    anomalies.slice().reverse().forEach(a => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${a.timestamp}</td>
            <td>${a.patient_id}</td>
            <td class="text-info">${a.score.toFixed(2)}</td>
            <td><span class="badge ${a.severity==='High'?'bg-danger':a.severity==='Medium'?'bg-warning text-dark':'bg-success'}">${a.severity}</span></td>
            <td>${a.heart_rate}</td>
            <td>${a.spo2}</td>
            <td>${a.temperature}</td>
            <td>${a.bp}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function fetchData(){
    try {
        const response = await fetch('/anomalies');
        const data = await response.json();
        anomalies = data.map(a => ({
            timestamp: new Date(a.timestamp*1000).toLocaleTimeString(),
            patient_id: 'P' + String(a.patient_id).padStart(3,'0'),
            score: a.anomaly_score,
            severity: a.explanations.length===0?'Low':a.explanations.includes('High Heart Rate')||a.explanations.includes('High Body Temperature')||a.explanations.includes('High Blood Pressure')?'High':'Medium',
            heart_rate: a.heart_rate,
            spo2: Math.floor(Math.random()*5 + 95), // placeholder
            temperature: a.temperature,
            bp: `${a.blood_pressure}/85` // placeholder diastolic
        }));
        updateKPIs();
        renderTable();
        updateCharts();
    } catch(e){ console.error(e); }
}

function updateCharts(){
    const counts={Low:0,Medium:0,High:0}; anomalies.forEach(a=>counts[a.severity]++);
    severityDonut.data.datasets[0].data = [counts.Low,counts.Medium,counts.High]; severityDonut.update();
    const last10 = anomalies.slice(-10); const labels=last10.map(a=>a.timestamp);
    anomalyTrend.data.labels = labels; anomalyTrend.data.datasets[0].data=last10.map(a=>a.score); anomalyTrend.update();
    heartRateChart.data.labels = labels; heartRateChart.data.datasets[0].data = last10.map(a=>a.heart_rate); heartRateChart.update();
    spo2Chart.data.labels = labels; spo2Chart.data.datasets[0].data = last10.map(a=>a.spo2); spo2Chart.update();
    tempChart.data.labels = labels; tempChart.data.datasets[0].data = last10.map(a=>a.temperature); tempChart.update();
    bpChart.data.labels = labels; bpChart.data.datasets[0].data = last10.map(a=>parseInt(a.bp.split('/')[0]));
    bpChart.data.datasets[1].data = last10.map(a=>parseInt(a.bp.split('/')[1])); bpChart.update();
}

function updateKPIs(){
    document.getElementById('activePatients').innerHTML = `<span class="text-success">●</span> ${[...new Set(anomalies.map(a=>a.patient_id))].length} Active`;
    const highRisk = anomalies.filter(a=>a.severity==='High').length;
    const percent = anomalies.length>0?((highRisk/anomalies.length)*100).toFixed(1):0;
    document.getElementById('highRiskAlerts').innerHTML = `${highRisk} <small>${percent}% of total</small>`;
    const avgScore = anomalies.length>0? (anomalies.reduce((acc,a)=>acc+a.score,0)/anomalies.length).toFixed(2):0;
    document.getElementById('avgAnomalyScore').innerText = `${avgScore} ✓ Normal range`;
    document.getElementById('lastAlert').innerText = anomalies.length>0?anomalies.slice(-1)[0].timestamp:'--:--:--';
}

document.getElementById('refreshBtn').addEventListener('click', fetchData);

setInterval(()=>{
    if(document.getElementById('autoRefresh').checked){
        fetchData();
    }
},10000);

fetchData();