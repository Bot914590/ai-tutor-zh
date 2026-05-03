
Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue

$env:OLLAMA_NUM_GPU = "999"
Write-Host " Запуск Ollama с GPU-оффлоадом..." -ForegroundColor Cyan
Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden

Start-Sleep -Seconds 8

$body = @{
    model = "qwen3.5:4b"
    messages = @(@{role="user"; content="Скажи 'Привет' и верни только это слово."})
    stream = $false
} | ConvertTo-Json -Depth 3

$res = Invoke-RestMethod -Uri "http://localhost:11434/v1/chat/completions" -Method Post -Headers @{"Content-Type"="application/json"} -Body $body
Write-Host "Ответ: $($res.choices[0].message.content)" -ForegroundColor Green

# Stop-Process -Name "ollama" -Force