/**
 * OSINT Microagent - Results JavaScript
 * Handles displaying and interacting with search results
 */

document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const resultsTabs = document.querySelectorAll('.results-tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    resultsTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs and contents
            resultsTabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Get target content and activate it
            const target = this.getAttribute('data-target');
            document.getElementById(target).classList.add('active');
        });
    });
    
    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.copy-btn');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            
            navigator.clipboard.writeText(textToCopy)
                .then(() => {
                    // Visual feedback
                    const originalText = this.textContent;
                    this.textContent = 'Copied!';
                    this.classList.add('copied');
                    
                    setTimeout(() => {
                        this.textContent = originalText;
                        this.classList.remove('copied');
                    }, 2000);
                })
                .catch(err => {
                    console.error('Could not copy text: ', err);
                });
        });
    });
    
    // Export results functionality
    const exportButton = document.getElementById('export-results');
    if (exportButton) {
        exportButton.addEventListener('click', function() {
            const resultsData = JSON.parse(document.getElementById('results-data').textContent);
            const dataStr = JSON.stringify(resultsData, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
            
            const exportFileDefaultName = 'osint-results.json';
            
            const linkElement = document.createElement('a');
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', exportFileDefaultName);
            linkElement.click();
        });
    }
    
    // Terminal output functionality
    function addTerminalOutput(message, type = 'output') {
        const terminal = document.getElementById('results-terminal');
        if (!terminal) return;
        
        const line = document.createElement('div');
        line.className = 'terminal-line';
        
        switch (type) {
            case 'command':
                line.innerHTML = `<span class="terminal-prompt">$</span><span class="terminal-command"> ${message}</span>`;
                break;
            case 'output':
                line.innerHTML = `<span class="terminal-output">${message}</span>`;
                break;
            case 'warning':
                line.innerHTML = `<span class="terminal-warning">${message}</span>`;
                break;
            case 'error':
                line.innerHTML = `<span class="terminal-error">${message}</span>`;
                break;
            default:
                line.textContent = message;
        }
        
        terminal.appendChild(line);
        terminal.scrollTop = terminal.scrollHeight;
    }
    
    // Function to animate the results appearance
    function animateResultsAppearance() {
        const resultCards = document.querySelectorAll('.result-card');
        resultCards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100 * index);
        });
    }
    
    // Initialize animations
    animateResultsAppearance();
    
    // Add terminal simulator for OSINT operations visualization
    const terminal = document.getElementById('results-terminal');
    if (terminal) {
        // Get query from page data
        const query = document.getElementById('query-data')?.textContent || 'unknown query';
        
        // Simulate terminal activity for the search
        setTimeout(() => addTerminalOutput(`osint-search "${query}"`, 'command'), 500);
        setTimeout(() => addTerminalOutput('Initializing search modules...'), 1000);
        setTimeout(() => addTerminalOutput('Searching public sources...'), 1500);
        setTimeout(() => addTerminalOutput('Querying APIs...'), 2000);
        setTimeout(() => addTerminalOutput('Performing WHOIS lookups...'), 2500);
        setTimeout(() => addTerminalOutput('Processing and categorizing results...'), 3000);
        setTimeout(() => addTerminalOutput('Search complete! Results available in tabs above.'), 3500);
        setTimeout(() => addTerminalOutput('$ ', 'command'), 4000);
    }
    
    // Toggle visibility of result sections
    const toggleButtons = document.querySelectorAll('.toggle-section');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetSection = document.getElementById(targetId);
            
            if (targetSection.style.display === 'none') {
                targetSection.style.display = 'block';
                this.textContent = 'Hide';
            } else {
                targetSection.style.display = 'none';
                this.textContent = 'Show';
            }
        });
    });
    
    // Webhook status checker
    const webhookStatus = document.getElementById('webhook-status');
    if (webhookStatus && webhookStatus.getAttribute('data-pending') === 'true') {
        // This would check the webhook delivery status in a real implementation
        // For demo, just show success after a delay
        setTimeout(() => {
            webhookStatus.textContent = 'Delivered';
            webhookStatus.className = 'badge badge-success';
        }, 3000);
    }
});
