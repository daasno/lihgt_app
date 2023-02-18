mkdir -p ~/.streamlit/

echo "\
[server]\n\
port = $PORT\n\
enableCORS = false\n\
headless = true\n\
maxUploadSize = 10000\n\
\n\
" > ~/.streamlit/config.toml