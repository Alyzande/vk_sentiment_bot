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

        // Debug info
        debugDiv.textContent = `Posts fetched: ${data.steps.posts_fetched}\n` +
                               `Posts matching keywords: ${data.steps.analyzed_posts ? data.steps.analyzed_posts.length : 0}\n\n` +
                               (data.steps.posts_fetched_preview || []).join("\n---\n");

        // Clear results container
        resultsDiv.innerHTML = "";

        if (data.steps && data.steps.analyzed_posts) {
            data.steps.analyzed_posts.forEach(post => {
                const box = document.createElement("div");
                box.classList.add("post-box");
                box.style.borderRadius = "8px";
                box.style.padding = "10px";
                box.style.margin = "10px 0";
                box.style.whiteSpace = "pre-wrap";

                // Color by sentiment of the fragment
                if (post.sentiment === "Positive") box.style.backgroundColor = "#cce5ff"; // light blue
                else if (post.sentiment === "Negative") box.style.backgroundColor = "#f8d7da"; // light red
                else box.style.backgroundColor = "#e2e3e5"; // grey

                // Display full post, but indicate analyzed fragment
                box.innerHTML = `<strong>[${post.sentiment}]</strong> ${post.text_full}<br><em>Analyzed fragment: "${post.text_fragment}"</em>`;
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
