import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter, Language
import tiktoken
import streamlit.components.v1 as components
from ebooklib import epub
from bs4 import BeautifulSoup
import tempfile
import os

# -------------------------
# PWA Configuration (Streamlit Cloud Optimized)
# -------------------------
def register_pwa():
    """Streamlit-specific PWA setup with base path handling"""
    base_path = st._config.get_option("server.baseUrlPath").strip("/")
    
    st.markdown(f"""
    <link rel="manifest" href="/static/manifest.json?v=3">
    <meta name="theme-color" content="#f63366">
    <link rel="apple-touch-icon" href="/static/icons/icon-192x192.png">
    """, unsafe_allow_html=True)

    components.html(f"""
    <script>
    if ('serviceWorker' in navigator) {{
        const basePath = "{base_path}";
        window.addEventListener('load', () => {{
            navigator.serviceWorker.register(basePath + '/static/service-worker.js', {{ 
                scope: basePath + '/' 
            }})
            .then(reg => console.log('ServiceWorker registered for scope:', reg.scope))
            .catch(err => console.log('ServiceWorker registration failed:', err));
        }});
    }}
    </script>
    """, height=0, width=0)

def add_install_prompt():
    """Enhanced install prompt with Streamlit styling"""
    components.html("""
    <script>
    let deferredPrompt;
    const installButton = document.createElement('button');
    
    function showInstallButton() {
        installButton.style.display = 'block';
    }
    
    function hideInstallButton() {
        installButton.style.display = 'none';
    }

    // Styling matching Streamlit's theme
    installButton.innerHTML = '📱 Install App';
    installButton.style.display = 'none';
    installButton.style.position = 'fixed';
    installButton.style.bottom = '20px';
    installButton.style.right = '20px';
    installButton.style.zIndex = '999999';
    installButton.style.padding = '10px 20px';
    installButton.style.background = '#f63366';
    installButton.style.color = 'white';
    installButton.style.border = 'none';
    installButton.style.borderRadius = '4px';
    installButton.style.fontFamily = 'Source Sans Pro, sans-serif';
    installButton.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';
    document.body.appendChild(installButton);

    window.addEventListener('beforeinstallprompt', (e) => {{
        e.preventDefault();
        deferredPrompt = e;
        showInstallButton();
        
        // Auto-hide after 30 seconds
        setTimeout(hideInstallButton, 30000);
    }});

    installButton.addEventListener('click', async () => {{
        if(!deferredPrompt) return;
        const {{ outcome }} = await deferredPrompt.prompt();
        if(outcome === 'accepted') {{
            console.log('User installed PWA');
            hideInstallButton();
        }}
        deferredPrompt = null;
    }});
    </script>
    """, height=0, width=0)

# Initialize PWA components
register_pwa()
add_install_prompt()

# -------------------------
# Original Application Logic 
# ------------------------- 
# [Keep all your existing text processing code unchanged]
# [Include the exact same code for extract_chapters, session state management, UI components, etc.]

# ... (Rest of your existing application code remains identical)