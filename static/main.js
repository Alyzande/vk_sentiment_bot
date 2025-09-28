document.getElementById('analyze-btn').addEventListener('click', async () => {
    const newsService = document.getElementById('news-service').value;
    const keyword = document.getElementById('keyword').value;
    const count = parseInt(document.getElementById('count').value) || 100;

    const resultsDiv = document.getElementById('results');
    const debugDiv = document.getElementById('raw-posts-preview');
    resultsDiv.innerHTML = "Analyzing...";
    debugDiv.textContent = "";

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                news_service: newsService,
                count: count,
                keywords: [keyword]
            })
        });

        if (!response.ok) {
            throw new Error("Backend error: " + (await response.text()));
        }

        const data = await response.json();

        // Debug: show fetched posts
        debugDiv.textContent = `Posts fetched: ${data.steps.posts_fetched}\n` +
                               `Posts matching keywords: ${data.steps.analyzed_posts ? data.steps.analyzed_posts.length : 0}\n\n` +
                               (data.steps.posts_fetched_preview || []).join("\n---\n");

        // Clear results container
        resultsDiv.innerHTML = "";

        // Display analyzed posts
        if (data.steps && data.steps.analyzed_posts) {
            data.steps.analyzed_posts.forEach(post => {
                const box = document.createElement("div");
                box.classList.add("post-box");
                box.style.borderRadius = "8px";
                box.style.padding = "10px";
                box.style.margin = "10px 0";
                box.style.whiteSpace = "pre-wrap";

                // Display full post text first
                const fullTextEl = document.createElement("div");
                fullTextEl.innerHTML = `<strong>Full post:</strong> ${post.text_full}`;
                fullTextEl.style.marginBottom = "8px";
                box.appendChild(fullTextEl);

                // Display overall sentiment
                const overallEl = document.createElement("div");
                overallEl.innerHTML = `<strong>Overall sentiment:</strong> ${post.sentiment}`;
                overallEl.style.marginBottom = "8px";
                // Color code overall sentiment
                if (post.sentiment === "Positive") overallEl.style.color = "#004085"; // blue
                else if (post.sentiment === "Negative") overallEl.style.color = "#721c24"; // red
                else overallEl.style.color = "#383d41"; // grey
                box.appendChild(overallEl);

                // Display per-clause sentiments
                const clausesEl = document.createElement("div");
                clausesEl.innerHTML = "<strong>Clause-level sentiments:</strong><br>";
                post.clauses.forEach(([clauseText, clauseSentiment]) => {
                    const clauseDiv = document.createElement("div");
                    clauseDiv.textContent = `[${clauseSentiment}] ${clauseText}`;
                    clauseDiv.style.paddingLeft = "10px";
                    clauseDiv.style.marginBottom = "2px";
                    // Color code clause
                    if (clauseSentiment === "Positive") clauseDiv.style.backgroundColor = "#cce5ff";
                    else if (clauseSentiment === "Negative") clauseDiv.style.backgroundColor = "#f8d7da";
                    else clauseDiv.style.backgroundColor = "#e2e3e5";
                    clauseDiv.style.borderRadius = "4px";
                    clausesEl.appendChild(clauseDiv);
                });
                box.appendChild(clausesEl);

                resultsDiv.appendChild(box);
            });
        } else {
            resultsDiv.textContent = "No posts found matching keywords.";
        }
    } catch (err) {
        console.error("analyzeText error", err);
        resultsDiv.textContent = "Error: " + err.message;
    }
});
