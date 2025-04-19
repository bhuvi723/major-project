// Main JavaScript file for FinDash

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Format currency values
    document.querySelectorAll('.currency-value').forEach(function(element) {
        const value = parseFloat(element.textContent);
        if (!isNaN(value)) {
            element.textContent = formatCurrency(value);
        }
    });
    
    // Format percentage values
    document.querySelectorAll('.percentage-value').forEach(function(element) {
        const value = parseFloat(element.textContent);
        if (!isNaN(value)) {
            element.textContent = formatPercentage(value);
            
            // Add color class based on value
            if (value > 0) {
                element.classList.add('positive-return');
            } else if (value < 0) {
                element.classList.add('negative-return');
            }
        }
    });
    
    // Add animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
});

// Format currency function
function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

// Format percentage function
function formatPercentage(value) {
    return value.toFixed(2) + '%';
}

// Format large numbers with abbreviations
function formatLargeNumber(num) {
    if (num >= 10000000) {
        return (num / 10000000).toFixed(2) + ' Cr';
    } else if (num >= 100000) {
        return (num / 100000).toFixed(2) + ' L';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(2) + ' K';
    }
    return num.toString();
}

// Create a line chart
function createLineChart(elementId, labels, data, label, color = '#2563eb') {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                borderColor: color,
                backgroundColor: color + '20',
                borderWidth: 2,
                pointBackgroundColor: color,
                pointRadius: 3,
                pointHoverRadius: 5,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: false,
                    grid: {
                        color: '#e2e8f0'
                    }
                }
            }
        }
    });
}

// Create a pie chart
function createPieChart(elementId, labels, data, colors) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 1,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${percentage}% (${formatCurrency(value)})`;
                        }
                    }
                }
            }
        }
    });
}

// Create a bar chart
function createBarChart(elementId, labels, data, label, color = '#2563eb') {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: color + '80',
                borderColor: color,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#e2e8f0'
                    }
                }
            }
        }
    });
}

// Create a heatmap using Plotly
function createHeatmap(elementId, data, xLabels, yLabels, title) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const heatmapData = [{
        z: data,
        x: xLabels,
        y: yLabels,
        type: 'heatmap',
        colorscale: 'Viridis',
        showscale: true
    }];
    
    const layout = {
        title: title,
        xaxis: {
            title: 'Stocks'
        },
        yaxis: {
            title: 'Stocks'
        },
        margin: {
            l: 100,
            r: 50,
            b: 100,
            t: 50,
            pad: 4
        }
    };
    
    Plotly.newPlot(elementId, heatmapData, layout, {responsive: true});
}

// Search stocks function
function searchStocks(query, callback) {
    fetch(`/stocks/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            callback(data);
        })
        .catch(error => {
            console.error('Error searching stocks:', error);
            callback([]);
        });
}
