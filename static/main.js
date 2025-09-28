document.getElementById('analyze-btn').addEventListener('click', async () => {
    const newsService = document.getElementById('news-service').value;
    const keyword = document.getElementById('keyword').value;
    const count = parseInt(document.getElementById('count').value) || 100;

    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = "Analyzing...";

    // const debugDiv = document.getElementById('raw-posts-preview'); // commented out
    // debugDiv.textContent = "";

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

        // debugDiv.textContent = `Posts fetched: ${data.steps.posts_fetched}\n` +
        //                        `Posts matching keywords: ${data.steps.analyzed_posts ? data.steps.analyzed_posts.length : 0}\n\n` +
        //                        (data.steps.raw_posts_preview || []).join("\n---\n");

        resultsDiv.innerHTML = "";

        if (data.steps && data.steps.analyzed_posts) {
            data.steps.analyzed_posts.forEach(post => {
                const box = document.createElement("div");
                box.classList.add("post-box");
                box.style.borderRadius = "8px";
                box.style.padding = "10px";
                box.style.margin = "10px 0";
                box.style.whiteSpace = "pre-wrap";

                // Color by sentiment
                if (post.sentiment === "Positive") box.style.backgroundColor = "#cce5ff";
                else if (post.sentiment === "Negative") box.style.backgroundColor = "#f8d7da";
                else box.style.backgroundColor = "#e2e3e5";

                let html = `<strong>[${post.sentiment}]</strong> ${post.text_full}\n`;

                if (post.clauses && post.clauses.length > 0) {
                    const uniqueId = 'clauses-' + Math.random().toString(36).substring(2, 10);
                    html += `<details style="margin-top:5px;"><summary>Why [${post.sentiment}]?</summary><pre style="white-space: pre-wrap; margin:5px 0;">`;
                    post.clauses.forEach(clause => {
                        html += `[${clause.sentiment}] ${clause.text}\n`;
                    });
                    html += `</pre></details>`;
                }

                box.innerHTML = html;
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
