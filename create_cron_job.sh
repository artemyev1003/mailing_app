crontab -l | { cat; echo "0 8 * * * curl http://localhost:5000/send-mail"; } | crontab -

