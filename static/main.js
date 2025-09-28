document.addEventListener("DOMContentLoaded", () => {
    console.log("main.js loaded!");

    document.getElementById('analyze-btn').addEventListener('click', async () => {
        const newsService = document.getElementById('news-service').value;
        const keyword = document.getElementById('keyword').value;

        let endpoint = '';
        if (newsService === 'tass') endpoint = '/analyze_tass';
        else if (newsService === 'ria') endpoint = '/analyze_ria';
        else if (newsService === 'rt') endpoint = '/analyze_user';

        console.log("Sending request to", endpoint, "with keyword", keyword);

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ count: 100, keywords: [keyword] })
        });

        const data = await response.json();
        document.getElementById('results').textContent = JSON.stringify(data, null, 2);
        console.log("Received response", data);
    });
});
