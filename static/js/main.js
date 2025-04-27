/**
 * OSINT Microagent - Main JavaScript
 * Handles UI interactions and search form submission
 */

document.addEventListener('DOMContentLoaded', function() {
    // Search form handling
    const searchForm = document.getElementById('search-form');
    const loadingSpinner = document.getElementById('loading-spinner');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            // Show loading spinner while search is processing
            loadingSpinner.style.display = 'block';
            
            // Form will submit normally, no need to prevent default
        });
    }
    
    // Terminal animation effect
    const terminalContent = document.getElementById('terminal-content');
    if (terminalContent) {
        const messages = [
            { text: "$ osint-agent --initialize", type: "command" },
            { text: "Initializing OSINT modules...", type: "output" },
            { text: "Loading search engine scrapers... Done.", type: "output" },
            { text: "Loading API connectors... Done.", type: "output" },
            { text: "Loading WHOIS lookup... Done.", type: "output" },
            { text: "Loading parsers... Done.", type: "output" },
            { text: "Loading exporters... Done.", type: "output" },
            { text: "OSINT Microagent Ready.", type: "output" },
            { text: "$ ", type: "prompt" }
        ];
        
        let i = 0;
        const typewriter = setInterval(function() {
            if (i < messages.length) {
                const message = messages[i];
                const line = document.createElement('div');
                line.className = 'terminal-line';
                
                if (message.type === 'command') {
                    line.innerHTML = `<span class="terminal-prompt">$</span><span class="terminal-command">${message.text.substring(2)}</span>`;
                } else if (message.type === 'output') {
                    line.innerHTML = `<span class="terminal-output">${message.text}</span>`;
                } else if (message.type === 'prompt') {
                    line.innerHTML = `<span class="terminal-prompt blink">${message.text}</span>`;
                }
                
                terminalContent.appendChild(line);
                terminalContent.scrollTop = terminalContent.scrollHeight;
                i++;
            } else {
                clearInterval(typewriter);
            }
        }, 300);
    }
    
    // Nav tabs handling
    const navTabs = document.querySelectorAll('.nav-tab');
    navTabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            // This would be extended in a real app to handle tab switching
            // Currently just for UI demonstration
        });
    });
    
    // Example of a cyber progress bar animation
    const progressBars = document.querySelectorAll('.cyber-progress-bar');
    progressBars.forEach(bar => {
        const targetWidth = bar.getAttribute('data-width') || '100';
        setTimeout(() => {
            bar.style.width = `${targetWidth}%`;
        }, 300);
    });
    
    // Helper function to create a typing effect for headers
    function initTypewriterEffect() {
        const elements = document.querySelectorAll('.typing-effect');
        elements.forEach(element => {
            const text = element.textContent;
            element.textContent = '';
            element.classList.add('typing');
            
            let i = 0;
            const typing = setInterval(() => {
                if (i < text.length) {
                    element.textContent += text.charAt(i);
                    i++;
                } else {
                    clearInterval(typing);
                    element.classList.remove('typing');
                }
            }, 50);
        });
    }
    
    // Initialize typing effect for elements with that class
    initTypewriterEffect();
    
    // Add pulse effect to action buttons
    const actionButtons = document.querySelectorAll('.cyber-button');
    actionButtons.forEach(button => {
        button.classList.add('pulse');
    });
});
