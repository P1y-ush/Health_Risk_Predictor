// ── Health Risk Predictor — Client-Side Logic ────────────
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('healthForm');
    const resultSection = document.getElementById('result-section');
    const formSection = document.getElementById('form-section');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await submitPrediction();
    });
});

async function submitPrediction() {
    const btn = document.getElementById('predict-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoader = btn.querySelector('.btn-loader');

    // Show loading
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-flex';
    btn.disabled = true;

    const payload = {
        age: parseFloat(document.getElementById('age').value),
        bp: parseFloat(document.getElementById('bp').value),
        sugar: parseFloat(document.getElementById('sugar').value),
        cholesterol: parseFloat(document.getElementById('cholesterol').value),
        heart_rate: parseFloat(document.getElementById('heart_rate').value),
        bmi: parseFloat(document.getElementById('bmi').value)
    };

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        displayResults(data);
    } catch (error) {
        alert('Error: Could not connect to the prediction service. ' + error.message);
    } finally {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        btn.disabled = false;
    }
}

function displayResults(data) {
    const resultSection = document.getElementById('result-section');
    resultSection.classList.remove('hidden');
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Risk level & color
    const riskLevel = data.risk_level;
    const riskEl = document.getElementById('risk-level');
    riskEl.textContent = riskLevel;

    const riskDisplay = document.getElementById('risk-display');
    riskDisplay.className = 'risk-display';

    let riskColor, gauseOffset;
    if (riskLevel === 'Low') {
        riskColor = '#06d6a0';
        gauseOffset = 534 * 0.67; // 33% filled
        riskDisplay.classList.add('risk-low');
    } else if (riskLevel === 'Normal') {
        riskColor = '#f59e0b';
        gauseOffset = 534 * 0.33; // 67% filled
        riskDisplay.classList.add('risk-normal-risk');
    } else {
        riskColor = '#ef4444';
        gauseOffset = 534 * 0.05; // 95% filled
        riskDisplay.classList.add('risk-high-risk');
    }

    riskEl.style.color = riskColor;

    // Animate gauge
    const gaugeProgress = document.getElementById('gauge-progress');
    gaugeProgress.style.stroke = riskColor;
    setTimeout(() => {
        gaugeProgress.style.strokeDashoffset = gauseOffset;
    }, 100);

    // Confidence
    document.getElementById('confidence-value').textContent = data.confidence;

    // Probability bars
    const probLow = parseFloat(data.probabilities.Low);
    const probNormal = parseFloat(data.probabilities.Normal);
    const probHigh = parseFloat(data.probabilities.High);

    setTimeout(() => {
        document.getElementById('prob-low').style.width = probLow + '%';
        document.getElementById('prob-normal').style.width = probNormal + '%';
        document.getElementById('prob-high').style.width = probHigh + '%';
    }, 200);

    document.getElementById('prob-low-val').textContent = data.probabilities.Low;
    document.getElementById('prob-normal-val').textContent = data.probabilities.Normal;
    document.getElementById('prob-high-val').textContent = data.probabilities.High;

    // Recommendations
    const recList = document.getElementById('recommendations-list');
    recList.innerHTML = '';
    data.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.textContent = rec;
        recList.appendChild(li);
    });

    // Preventive measures
    const prevList = document.getElementById('preventive-list');
    prevList.innerHTML = '';
    data.preventive_measures.forEach(measure => {
        const li = document.createElement('li');
        li.textContent = measure;
        prevList.appendChild(li);
    });
}

function resetForm() {
    document.getElementById('healthForm').reset();
    document.getElementById('result-section').classList.add('hidden');

    // Reset gauge
    document.getElementById('gauge-progress').style.strokeDashoffset = 534;
    document.getElementById('prob-low').style.width = '0%';
    document.getElementById('prob-normal').style.width = '0%';
    document.getElementById('prob-high').style.width = '0%';

    document.getElementById('form-section').scrollIntoView({ behavior: 'smooth' });
}
