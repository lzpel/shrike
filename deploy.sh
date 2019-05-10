git add .
git commit -m a
git push
gcloud app deploy app.yaml cron.yaml index.yaml queue.yaml --version 1