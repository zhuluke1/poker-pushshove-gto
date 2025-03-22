// range-chart.js
// Show loading indicator while form is submitting
document.getElementById('calculator-form').addEventListener('submit', function() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('calculate-btn').disabled = true;
});

// Hand mapping for range chart
const ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'];
const handMap = {};
ranks.forEach((rank1, i) => {
    ranks.forEach((rank2, j) => {
        if (i === j) {
            handMap[`${rank1}${rank2}`] = { row: i, col: j, type: 'pair' };
        } else if (i < j) {
            handMap[`${rank1}${rank2}s`] = { row: i, col: j, type: 'suited' };
        } else {
            handMap[`${rank1}${rank2}o`] = { row: i, col: j, type: 'offsuit' };
        }
    });
});

// Function to create range chart
function createRangeChart(containerId, strategy, evData) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Create labels for rows and columns
    const rowLabels = document.createElement('div');
    rowLabels.className = 'row-labels';
    const colLabels = document.createElement('div');
    colLabels.className = 'col-labels';
    const labelsContainer = document.createElement('div');
    labelsContainer.className = 'range-labels';
    labelsContainer.appendChild(rowLabels);
    labelsContainer.appendChild(colLabels);
    container.parentElement.insertBefore(labelsContainer, container);

    ranks.forEach(rank => {
        const rowLabel = document.createElement('div');
        rowLabel.className = 'label';
        rowLabel.textContent = rank;
        rowLabels.appendChild(rowLabel);

        const colLabel = document.createElement('div');
        colLabel.className = 'label';
        colLabel.textContent = rank;
        colLabels.appendChild(colLabel);
    });

    // Create grid cells
    for (let i = 0; i < 13; i++) {
        for (let j = 0; j < 13; j++) {
            const cell = document.createElement('div');
            cell.className = 'range-cell';

            let hand, handType;
            if (i === j) {
                hand = `${ranks[i]}${ranks[j]}`;
                handType = 'pair';
            } else if (i < j) {
                hand = `${ranks[i]}${ranks[j]}s`;
                handType = 'suited';
            } else {
                hand = `${ranks[i]}${ranks[j]}o`;
                handType = 'offsuit';
            }

            cell.classList.add(handType);
            cell.textContent = hand;

            const freq = strategy[hand] || 0;
            const ev = evData[hand] || 0;

            const intensity = Math.min(1, freq);
            const r = Math.round(255 * (1 - intensity));
            const g = Math.round(255 * intensity);
            cell.style.backgroundColor = `rgb(${r}, ${g}, 0)`;

            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = `Freq: ${(freq * 100).toFixed(1)}%, EV: ${ev.toFixed(2)}`;
            cell.appendChild(tooltip);

            container.appendChild(cell);
        }
    }
}

// Render range charts using data from global variables
document.addEventListener('DOMContentLoaded', function() {
    if (window.sbStrategy) {
        createRangeChart('sb-range-chart', window.sbStrategy, window.sbPushEv);
    }
    if (window.bbStrategy) {
        createRangeChart('bb-range-chart', window.bbStrategy, window.bbCallEv);
    }
});