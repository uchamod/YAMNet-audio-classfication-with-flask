gcloud run deploy audio-classifier \
  --image gcr.io/safe-journey-app-597b3/audio-classifier \
  --memory 2Gi \
  --timeout 300 \
  --port 8080 \
  --allow-unauthenticated

  gcloud run deploy audio-classifier `
  --image gcr.io/safe-journey-app-597b3/audio-classifier `
  --memory 2Gi `
  --timeout 300 `
  --port 8080 `
  --allow-unauthenticated `
  --platform managed `
  --region asia-southeast1

  gcloud run deploy audio-classifier --image asia-southeast1-docker.pkg.dev/safe-journey-app-597b3/audio-classifier-repo/audio-classifier --memory 2Gi --cpu 2 --timeout 900 --concurrency 1 --max-instances 1 --port 8080 --allow-unauthenticated --platform managed --region asia-southeast1


  --build docker with cloud run--
  # Config
  gcloud auth configure-docker
  # build
  docker build -t gcr.io/safe-journey-app-597b3/audio-classifier .
  # push
  docker push gcr.io/safe-journey-app-597b3/audio-classifier
  # verify
  gcloud container images list --repository=gcr.io/safe-journey-app-597b3
  # deploy
  gcloud run deploy audio-classifier --image gcr.io/safe-journey-app-597b3/audio-classifier --memory 2Gi --timeout 600 --port 8080 --allow-unauthenticated --platform managed --region asia-southeast1
