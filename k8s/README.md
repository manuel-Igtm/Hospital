# Hospital Backend - Kubernetes Manifests

This directory contains Kubernetes manifests for deploying the Hospital Backend application.

## Directory Structure

```
k8s/
├── namespace.yaml      # Namespace definition
├── configmap.yaml      # Application configuration
├── secret.yaml         # Sensitive data (credentials, keys)
├── deployment.yaml     # Backend + Celery worker deployments
├── service.yaml        # Service definitions
├── ingress.yaml        # Ingress configuration
├── database.yaml       # PostgreSQL StatefulSet + Redis Deployment
└── hpa.yaml            # Horizontal Pod Autoscaler + PDB
```

## Prerequisites

- Kubernetes cluster (1.25+)
- kubectl configured
- Nginx Ingress Controller installed
- (Optional) cert-manager for TLS

## Quick Deploy

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy secrets (EDIT FIRST with real values!)
kubectl apply -f k8s/secret.yaml

# Deploy config
kubectl apply -f k8s/configmap.yaml

# Deploy database (for dev/test only)
kubectl apply -f k8s/database.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l component=postgres -n hospital --timeout=120s

# Deploy application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Deploy ingress
kubectl apply -f k8s/ingress.yaml

# (Optional) Deploy HPA
kubectl apply -f k8s/hpa.yaml
```

## Verify Deployment

```bash
# Check pods
kubectl get pods -n hospital

# Check services
kubectl get svc -n hospital

# Check ingress
kubectl get ingress -n hospital

# View logs
kubectl logs -f deployment/hospital-backend -n hospital

# Port forward for local testing
kubectl port-forward svc/hospital-backend 8000:80 -n hospital
```

## Production Considerations

### Secrets Management
- Use **External Secrets Operator** or **Sealed Secrets** instead of plain Kubernetes secrets
- Consider **HashiCorp Vault** for enterprise-grade secret management

### Database
- Use managed PostgreSQL (AWS RDS, GCP Cloud SQL, Azure Database for PostgreSQL)
- Update `DATABASE_HOST` in ConfigMap to point to managed instance
- Remove `database.yaml` from production deployments

### TLS/SSL
- Uncomment cert-manager annotations in `ingress.yaml`
- Install cert-manager: `kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml`
- Create ClusterIssuer for Let's Encrypt

### Monitoring
- Deploy Prometheus + Grafana for metrics
- Application exposes `/metrics` endpoint (configure in Django)
- Use Kubernetes events and pod logs for debugging

### Scaling
- HPA configured for CPU/memory autoscaling
- PDB ensures high availability during updates
- Consider using Kubernetes VPA for right-sizing

## Environment-Specific Deployments

For different environments, use Kustomize overlays or Helm:

```bash
# Using Kustomize
kubectl apply -k k8s/overlays/production

# Using Helm (if available)
helm install hospital ./helm/hospital -f values-production.yaml
```

## Troubleshooting

```bash
# Check pod events
kubectl describe pod <pod-name> -n hospital

# Check deployment status
kubectl rollout status deployment/hospital-backend -n hospital

# Restart deployment
kubectl rollout restart deployment/hospital-backend -n hospital

# Scale manually
kubectl scale deployment/hospital-backend --replicas=5 -n hospital

# Run migrations manually
kubectl exec -it deployment/hospital-backend -n hospital -- python manage.py migrate

# Create superuser
kubectl exec -it deployment/hospital-backend -n hospital -- python manage.py createsuperuser
```
