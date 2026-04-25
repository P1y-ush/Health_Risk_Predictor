# AI-Based Smart Health Risk Predictor

> ML-powered health risk prediction with personalized recommendations, deployed via a complete DevOps pipeline with Blue-Green Kubernetes deployment, Ansible automation, Vault secrets management, and ELK monitoring.

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│   Web UI    │───▶│  FastAPI App  │───▶│  ML Model    │
│  (HTML/JS)  │    │  (Python)    │    │ (RandomForest)│
└─────────────┘    └──────────────┘    └──────────────┘
                          │
              ┌───────────▼───────────┐
              │    Docker Container   │
              └───────────┬───────────┘
                          │
    ┌─────────────────────▼─────────────────────┐
    │           Kubernetes (Minikube)            │
    │  ┌──────────┐  ┌──────────┐  ┌────────┐  │
    │  │   BLUE   │  │  GREEN   │  │  HPA   │  │
    │  │ (stable) │  │  (new)   │  │(scale) │  │
    │  └────┬─────┘  └────┬─────┘  └────────┘  │
    │       └──────┬──────┘                     │
    │         ┌────▼────┐                       │
    │         │ Service │                       │
    │         └─────────┘                       │
    └───────────────────────────────────────────┘
```

## 🚀 Features

1. **Health Risk Prediction** — ML model predicts Low / Normal / High risk (95.2% accuracy)
2. **Personalized Recommendations** — Context-aware health advice based on input parameters
3. **Beautiful Web UI** — Dark-themed, responsive design with animated risk gauge
4. **Blue-Green Deployment** — Zero-downtime updates in Kubernetes
5. **Horizontal Pod Autoscaler (HPA)** — Auto-scales 2-6 replicas based on CPU/memory
6. **DevSecOps** — Trivy container vulnerability scanning
7. **ELK Monitoring** — Centralized logging with Elasticsearch + Kibana
8. **Ansible Roles** — Modular configuration management
9. **HashiCorp Vault** — Secure secrets storage for credentials
10. **GitHub Webhook** — Auto-trigger Jenkins pipeline on push

## 📁 Project Structure

```
Health_risk_predictor/
├── app/                          # FastAPI web application
│   ├── main.py                   #   API + recommendation engine
│   ├── templates/index.html      #   Web UI
│   └── static/                   #   CSS + JS
├── ml/                           # Machine learning
│   ├── train.py                  #   Model training with evaluation
│   ├── dataset.csv               #   102-sample training dataset
│   └── model.pkl                 #   Trained RandomForest model
├── tests/                        # Unit tests (10 tests)
│   └── test_app.py
├── kubernetes/                   # K8s Blue-Green + HPA
│   ├── blue-deployment.yaml
│   ├── green-deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml                  #   Horizontal Pod Autoscaler
│   ├── switch-to-green.sh
│   └── rollback-to-blue.sh
├── ansible/                      # Configuration management
│   ├── deploy.yml                #   Main playbook
│   ├── inventory/hosts           #   Inventory
│   └── roles/
│       ├── docker/               #   Build & push Docker image
│       ├── kubernetes/           #   Deploy to K8s cluster
│       └── monitoring/           #   Start ELK Stack
├── vault/                        # Secrets management
│   ├── docker-compose.yml        #   Vault server
│   └── setup-vault.sh            #   Initialize secrets
├── elk/                          # ELK Stack
│   ├── docker-compose.yml
│   ├── logstash.conf
│   └── filebeat.yml
├── jenkins/
│   └── Jenkinsfile               #   Full CI/CD pipeline
├── Dockerfile
├── .dockerignore
├── requirements.txt
└── README.md
```

## 🏃 Quick Start

### Local Development
```bash
pip install -r requirements.txt
python ml/train.py
uvicorn app.main:app --reload --port 8000
```
Open http://localhost:8000

### Docker
```bash
docker build -t health-risk-predictor .
docker run -p 8000:8000 health-risk-predictor
```

### Kubernetes Blue-Green Deployment
```bash
kubectl apply -f kubernetes/blue-deployment.yaml
kubectl apply -f kubernetes/green-deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/hpa.yaml
minikube service health-app-service
```

### Ansible Deployment
```bash
ansible-playbook -i ansible/inventory/hosts ansible/deploy.yml
```

### Vault Setup
```bash
cd vault && docker compose up -d
./setup-vault.sh
```

### ELK Monitoring
```bash
cd elk && docker compose up -d
```
Kibana: http://localhost:5601

## 🔧 CI/CD Pipeline (Jenkins)

```
Clone → Install Deps → Train Model → Unit Tests → Build Docker
→ Security Scan (Trivy) → Fetch Secrets (Vault) → Push DockerHub
→ Deploy (Ansible) → Blue-Green Deploy + HPA → Email Notification
```

### Jenkins Setup
1. Add DockerHub credentials (ID: `dockerhub-creds`)
2. Add Vault token (ID: `vault-token`)
3. Create Pipeline job → Script Path: `jenkins/Jenkinsfile`
4. Configure GitHub webhook (via ngrok for local Jenkins)

## 🔐 HashiCorp Vault

Vault securely stores:
- DockerHub credentials (`secret/dockerhub`)
- Application secrets (`secret/health-app`)
- Kubernetes config (`secret/kubernetes`)

Jenkins fetches credentials from Vault at runtime with fallback to Jenkins credentials.

## 📈 Horizontal Pod Autoscaler

```yaml
Min Replicas: 2
Max Replicas: 6
CPU Target:   60%
Memory Target: 75%
```

Check HPA status: `kubectl get hpa`

## 🧪 Running Tests
```bash
python -m pytest tests/ -v
```

## 📊 Input Parameters

| Parameter   | Range    | Unit  |
|-------------|----------|-------|
| Age         | 1-120    | years |
| BP          | 40-250   | mmHg  |
| Sugar       | 30-500   | mg/dL |
| Cholesterol | 80-500   | mg/dL |
| Heart Rate  | 30-200   | bpm   |
| BMI         | 10-60    | —     |

## 🛡️ DevSecOps

- **Trivy**: Docker image vulnerability scanning (HIGH/CRITICAL)
- **Vault**: Secure credential storage (no hardcoded secrets)
- **Non-root container**: App runs as unprivileged user
- **Input validation**: Pydantic schema enforcement
- **Health checks**: Kubernetes liveness/readiness probes

## 🔗 DevOps Tools Used

| Tool | Purpose |
|------|---------|
| Git + GitHub | Version control |
| Jenkins | CI/CD automation |
| Docker | Containerization |
| Kubernetes | Orchestration & scaling |
| Ansible (Roles) | Configuration management |
| HashiCorp Vault | Secrets management |
| ELK Stack | Monitoring & logging |
| Trivy | Container security scanning |
| ngrok | Webhook tunnel |
