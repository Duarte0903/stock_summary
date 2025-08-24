param (
    [string]$ProjectId = "gen-lang-client-0008334327",
    [string]$FunctionName = "stock-summary-service",
    [string]$Region = "us-central1",
    [string]$SchedulerName = "daily-trigger",
    [string]$TopicName = "daily-trigger-topic",
    [string]$SAName = "cloud-fn-pubsub"
)

gcloud config set project $ProjectId

# activate APIs
gcloud services enable `
    cloudfunctions.googleapis.com `
    cloudscheduler.googleapis.com `
    pubsub.googleapis.com `
    iam.googleapis.com

# create service account if it doesn't exist
$SAEmail = "$SAName@$ProjectId.iam.gserviceaccount.com"
$saExists = gcloud iam service-accounts list --filter="email=$SAEmail" --format="value(email)"
if (-not $saExists) {
    Write-Host "Service account $SAEmail não encontrada. A criar..."
    gcloud iam service-accounts create $SAName --display-name "Cloud Functions Pub/Sub Invoker"
} else {
    Write-Host "Service account $SAEmail já existe."
}

# give Pub/Sub permissions to the service account
gcloud projects add-iam-policy-binding $ProjectId `
    --member "serviceAccount:$SAEmail" `
    --role "roles/pubsub.publisher"

gcloud projects add-iam-policy-binding $ProjectId `
    --member "serviceAccount:$SAEmail" `
    --role "roles/pubsub.subscriber"

gcloud projects add-iam-policy-binding $ProjectId `
    --member "serviceAccount:$SAEmail" `
    --role "roles/cloudfunctions.invoker"

# create Pub/Sub topic if it doesn't exist
$topicExists = gcloud pubsub topics list --filter="name~$TopicName" --format="value(name)"
if (-not $topicExists) {
    Write-Host "Tópico $TopicName não existe. A criar..."
    gcloud pubsub topics create $TopicName
} else {
    Write-Host "Tópico $TopicName já existe."
}

# deploy cloud run function
gcloud functions deploy $FunctionName `
    --source . `
    --runtime python311 `
    --entry-point main `
    --trigger-topic $TopicName `
    --region $Region `
    --timeout 540s `
    --memory 1Gi `
    --service-account $SAEmail `

# create Scheduler job
$Cron = "0 9 * * *"
$jobExists = gcloud scheduler jobs list --location $Region --filter="name~$SchedulerName" --format="value(name)"
if (-not $jobExists) {
    Write-Host "A criar job do Scheduler..."
    gcloud scheduler jobs create pubsub $SchedulerName `
        --schedule "$Cron" `
        --topic $TopicName `
        --message-body "{}" `
        --time-zone "Europe/Lisbon" `
        --location $Region `
        --quiet
} else {
    Write-Host "Job do Scheduler $SchedulerName já existe."
}

Write-Host "Função '$FunctionName' será acionada diariamente às 09:00 UTC através do Pub/Sub com a service account $SAEmail."
