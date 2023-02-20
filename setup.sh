mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
maxUploadSize = 10000\n\
\n\
" > ~/.streamlit/config.toml