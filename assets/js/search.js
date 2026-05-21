document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const resultsBox = document.getElementById('search-results');
    let timeout = null;

    searchInput.addEventListener('input', function() {
        clearTimeout(timeout);
        const query = this.value.trim();

        if (query.length < 2) {
            resultsBox.style.display = 'none';
            return;
        }

        timeout = setTimeout(() => {
            fetch(`/ajax/search/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    resultsBox.innerHTML = '';

                    if (data.results && data.results.length > 0) {
                        data.results.forEach(item => {
                            resultsBox.innerHTML += `<a href="/question/${item.id}/" class="dropdown-item text-wrap border-bottom py-2">${item.title}</a>`;
                        });
                        resultsBox.style.display = 'block';
                    } else {
                        resultsBox.innerHTML = '<span class="dropdown-item text-muted py-2">No results found</span>';
                        resultsBox.style.display = 'block';
                    }
                })
                .catch(error => console.error('Search error:', error));
        }, 300);
    });

    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !resultsBox.contains(e.target)) {
            resultsBox.style.display = 'none';
        }
    });
});
