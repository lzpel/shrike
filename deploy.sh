git add .
git commit -m a
git push
gcloud app deploy --project shrike-237211 --version 1
gcloud app deploy cron.yaml --project shrike-237211 --version 1
gcloud app deploy index.yaml --project shrike-237211 --version 1