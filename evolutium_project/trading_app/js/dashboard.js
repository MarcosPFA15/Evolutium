// static/trading_app/js/dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('start-analysis-btn');
    const loaderContainer = document.getElementById('loader-container');
    const analysisResultContainer = document.getElementById('analysis-result');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    let pollingInterval;

    function pollJobStatus(jobId) {
        pollingInterval = setInterval(() => {
            fetch(`/check_analysis_result/${jobId}/`)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'finished') {
                        clearInterval(pollingInterval);
                        loaderContainer.style.display = 'none';
                        analyzeBtn.disabled = false;
                        analyzeBtn.innerText = 'Analisar e Otimizar Novamente';
                        displayResults(data.result);
                    } else if (data.status === 'failed') {
                        clearInterval(pollingInterval);
                        loaderContainer.style.display = 'none';
                        analyzeBtn.disabled = false;
                        analyzeBtn.innerText = 'Tentar Análise Novamente';
                        displayError('A análise falhou. Por favor, tente novamente.');
                    }
                    // If 'queued' or 'started', do nothing and wait for the next poll
                })
                .catch(error => {
                    console.error('Error polling job status:', error);
                    clearInterval(pollingInterval);
                    loaderContainer.style.display = 'none';
                    analyzeBtn.disabled = false;
                    displayError('Ocorreu um erro ao verificar o resultado da análise.');
                });
        }, 5000); // Poll every 5 seconds
    }

    function displayError(message) {
        analysisResultContainer.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    }

    function displayResults(recommendation) {
        if (!recommendation) {
            displayError("Não foi possível obter uma recomendação da IA.");
            return;
        }

        let cardHeaderClass = 'bg-secondary';
        if (recommendation.action === 'BUY') cardHeaderClass = 'bg-success';
        if (recommendation.action === 'SELL') cardHeaderClass = 'bg-danger';
        
        let tradeForm = '';
        if (recommendation.action !== 'HOLD') {
            const formUrl = analyzeBtn.dataset.tradeUrl;
            let suggestionHtml = '';

            if(recommendation.action === 'BUY') {
                 suggestionHtml = `
                    <div class="alert alert-info">
                        <strong>Sugestão:</strong> Comprar <strong>${recommendation.suggested_quantity} ações</strong>.
                    </div>`;
            } else if (recommendation.action === 'SELL') {
                 suggestionHtml = `
                    <div class="alert alert-warning">
                        <strong>Sugestão:</strong> Vender <strong>${recommendation.quantity} ações</strong>.
                    </div>`;
            }

            tradeForm = `
                <form action="${formUrl}" method="post">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                    <input type="hidden" name="action" value="${recommendation.action}">
                    <input type="hidden" name="ticker" value="${recommendation.ticker}">
                    <input type="hidden" name="quantity" value="${recommendation.action === 'BUY' ? recommendation.suggested_quantity : recommendation.quantity}">
                    <input type="hidden" name="price" value="${recommendation.current_price}">
                    
                    ${suggestionHtml}

                    <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-3">
                        <button type="submit" class="btn btn-success">Aprovar</button>
                        <button type="button" class="btn btn-outline-secondary" onclick="document.getElementById('analysis-result').innerHTML = ''">Ignorar</button>
                    </div>
                </form>
            `;
        }

        const resultHtml = `
            <div class="card mt-4">
                <div class="card-header fw-bold text-white ${cardHeaderClass}">
                    Plano de Ação Recomendado
                </div>
                <div class="card-body">
                    <h5 class="card-title">
                        Ação: <span class="text-primary">${recommendation.action} ${recommendation.ticker || ''}</span>
                    </h5>
                    <p><strong>Justificativa da IA:</strong> ${recommendation.rationale}</p>
                    ${tradeForm}
                </div>
            </div>
        `;
        analysisResultContainer.innerHTML = resultHtml;
    }

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', function() {
            // Start analysis
            loaderContainer.style.display = 'block';
            analysisResultContainer.innerHTML = '';
            analyzeBtn.disabled = true;

            fetch(analyzeBtn.dataset.analysisUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.job_id) {
                    pollJobStatus(data.job_id);
                } else {
                    throw new Error(data.error || 'Failed to start analysis job.');
                }
            })
            .catch(error => {
                console.error('Error starting analysis:', error);
                loaderContainer.style.display = 'none';
                analyzeBtn.disabled = false;
                displayError(error.message);
            });
        });
    }
});
