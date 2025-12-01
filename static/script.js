const input = document.getElementById("reviewInput");
const btn = document.getElementById("predictBtn");
const clearBtn = document.getElementById("clearBtn");
const card = document.getElementById("resultCard");
const sentimentBadge = document.getElementById("sentimentBadge");
const sentimentText = document.getElementById("sentimentText");
const aspectsGrid = document.getElementById("aspects");

btn.addEventListener("click", async () => {
    const text = input.value.trim();
    if (!text) {
        alert("✨ Please enter a review to analyze!");
        return;
    }

    btn.disabled = true;
    btn.textContent = "⏳ Analyzing...";

    try {
        const res = await fetch("/predict", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({text})
        });

        const data = await res.json();
        if (data.error) {
            alert("⚠️ Error: " + data.message);
            return;
        }

        // Update sentiment
        const isSentimentPositive = data.prediction === 1;
        const sentiment = isSentimentPositive ? "Positive" : "Negative";
        
        sentimentText.textContent = sentiment;
        sentimentBadge.classList.remove("positive", "negative");
        sentimentBadge.classList.add(isSentimentPositive ? "positive" : "negative");

        // Display aspects
        aspectsGrid.innerHTML = "";
        const aspects = data.aspects || {};

        if (Object.keys(aspects).length === 0) {
            const empty = document.createElement("p");
            empty.textContent = "No specific aspects detected.";
            empty.style.color = "var(--text-tertiary)";
            empty.style.gridColumn = "1 / -1";
            empty.style.textAlign = "center";
            empty.style.padding = "20px";
            aspectsGrid.appendChild(empty);
        } else {
            Object.keys(aspects).forEach((aspect, index) => {
                aspects[aspect].forEach((item, itemIndex) => {
                    const card = document.createElement("div");
                    card.className = "aspect-item";
                    card.style.animation = `slideUp ${0.6 + (index * 0.1 + itemIndex * 0.05)}s cubic-bezier(0.34, 1.56, 0.64, 1)`;

                    const nameEl = document.createElement("div");
                    nameEl.className = "aspect-name";
                    nameEl.textContent = aspect.charAt(0).toUpperCase() + aspect.slice(1);
                    card.appendChild(nameEl);

                    const commentEl = document.createElement("div");
                    commentEl.className = "aspect-comment";
                    commentEl.textContent = `"${item.sentence}"`;
                    card.appendChild(commentEl);

                    const sentimentEl = document.createElement("span");
                    sentimentEl.className = `aspect-sentiment ${item.pred === 1 ? "positive" : "negative"}`;
                    sentimentEl.textContent = item.pred === 1 ? "✓ Positive" : "✗ Negative";
                    card.appendChild(sentimentEl);

                    if (item.probability !== null) {
                        const confEl = document.createElement("div");
                        confEl.className = "aspect-confidence";
                        confEl.textContent = `Confidence: ${Math.round(item.probability * 100)}%`;
                        card.appendChild(confEl);
                    }

                    aspectsGrid.appendChild(card);
                });
            });
        }

        card.classList.remove("hidden");
        card.scrollIntoView({ behavior: "smooth", block: "nearest" });

    } catch (error) {
        alert("⚠️ Error: " + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">⚡</span><span class="btn-label">Analyze Now</span>';
    }
});

clearBtn.addEventListener("click", () => {
    input.value = "";
    card.classList.add("hidden");
    input.focus();
});