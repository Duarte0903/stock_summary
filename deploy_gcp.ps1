param (
    [string]$ProjectId = "gen-lang-client-0008334327",
    [string]$FunctionName = "stock-summary-service",
    [string]$Region = "us-central1",
    [string]$SchedulerName = "daily-trigger",
    [string]$TopicName = "daily-trigger-topic",
    [string]$SAName = "cloud-fn-pubsub"
)

gcloud config set project $ProjectId

gcloud services enable `
    cloudfunctions.googleapis.com `
    cloudscheduler.googleapis.com `
    pubsub.googleapis.com `
    iam.googleapis.com

$SAEmail = "$SAName@$ProjectId.iam.gserviceaccount.com"
$saExists = gcloud iam service-accounts list --filter="email=$SAEmail" --format="value(email)"
if (-not $saExists) {
    Write-Host "Service account $SAEmail not found. Creating..."
    gcloud iam service-accounts create $SAName --display-name "Cloud Functions Pub/Sub Invoker"
} else {
    Write-Host "Service account $SAEmail already exists."
}

gcloud functions deploy $FunctionName `
    --source . `
    --runtime python311 `
    --entry-point main `
    --trigger-http `
    --allow-unauthenticated `
    --region $Region `
    --timeout 540s `
    --memory 1Gi `
    --service-account $SAEmail

$FunctionURL = gcloud functions describe $FunctionName --region $Region --format="value(serviceConfig.uri)"

$Cron = "0 9 * * *"
$jobExists = gcloud scheduler jobs list --location $Region --filter="name~$SchedulerName" --format="value(name)"
if (-not $jobExists) {
    Write-Host "Creating Scheduler job..."
    gcloud scheduler jobs create http $SchedulerName `
        --schedule "$Cron" `
        --uri "$FunctionURL" `
        --http-method GET `
        --time-zone "Europe/Lisbon" `
        --location $Region `
        --quiet
} else {
    Write-Host "Job do Scheduler $SchedulerName already exists."
}

Write-Host "Function '$FunctionName' will be triggered daily at 09:00 UTC via Cloud Scheduler."
