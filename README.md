# CloudCostGuard

Open-source FinOps platform for Kubernetes and Azure cost management.

## Overview

CloudCostGuard provides comprehensive cost intelligence for your cloud infrastructure, helping teams:

- Track Azure spending across subscriptions and resource groups
- Monitor Kubernetes resource usage and costs by namespace
- Generate month-on-month cost comparisons
- Receive AI-powered optimization recommendations
- Visualize cost trends and patterns

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Azure Cost    │    │   Kubernetes   │    │   Prometheus   │
│ Management API  │    │     Metrics     │    │   Metrics      │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    CloudCostGuard Backend                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐  │
│  │ Cost       │ │ Analytics   │ │ Optimization          │  │
│  │ Collectors │ │ Engine     │ │ Recommendation Engine │  │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘  │
│                        │                        │              │
│                        ▼                        ▼              │
│              ┌─────────────────────────────────────────┐              │
│              │         PostgreSQL Database           │              │
│              └─────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    React Frontend                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐  │
│  │ Overview   │ │ Cost        │ │ Recommendations       │  │
│  │ Dashboard  │ │ Analysis    │ │ Management           │  │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Features

### Cost Collection
- **Azure Cost Management API Integration**: Automatically fetch billing data
- **Kubernetes Metrics Collection**: Pull resource usage from Prometheus
- **Scheduled Sync**: Configurable collection intervals

### Cost Analysis
- **Namespace-wise Allocation**: Map costs to Kubernetes namespaces
- **Resource Breakdown**: CPU, memory, storage, and network costs
- **Trend Analysis**: Month-over-month comparisons

### Optimization
- **AI-Powered Recommendations**: Identify over-provisioned resources
- **Right-Sizing Suggestions**: Optimal resource configurations
- **Cost Savings Estimates**: Potential savings calculations

### Visualization
- **Interactive Dashboards**: Real-time cost monitoring
- **Trend Charts**: Historical cost patterns
- **Resource Utilization**: Efficiency metrics

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Azure Subscription (for cost data)
- Kubernetes cluster with Prometheus (optional)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/your-org/cloudcostguard.git
cd cloudcostguard
```

2. **Configure environment**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your Azure credentials
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Production Deployment

#### Using Helm

1. **Add the Helm repository**
```bash
helm repo add cloudcostguard https://charts.cloudcostguard.io
helm repo update
```

2. **Install the chart**
```bash
helm install cloudcostguard cloudcostguard/cloudcostguard \
  --namespace cloudcostguard \
  --create-namespace \
  --set azure.subscriptionId=$AZURE_SUBSCRIPTION_ID \
  --set azure.clientId=$AZURE_CLIENT_ID \
  --set azure.clientSecret=$AZURE_CLIENT_SECRET \
  --set azure.tenantId=$AZURE_TENANT_ID
```

#### Manual Installation

1. **Deploy PostgreSQL**
```bash
kubectl apply -f deployments/postgres.yaml
```

2. **Deploy Redis**
```bash
kubectl apply -f deployments/redis.yaml
```

3. **Deploy Backend**
```bash
kubectl apply -f deployments/backend.yaml
```

4. **Deploy Frontend**
```bash
kubectl apply -f deployments/frontend.yaml
```

## Configuration

### Backend Configuration

Key environment variables:

| Variable | Description | Required |
|----------|-------------|-----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID | Yes |
| `AZURE_CLIENT_ID` | Azure service principal ID | Yes |
| `AZURE_CLIENT_SECRET` | Azure service principal secret | Yes |
| `AZURE_TENANT_ID` | Azure tenant ID | Yes |
| `PROMETHEUS_URL` | Prometheus server URL | Yes |
| `SECRET_KEY` | JWT secret key | Yes |

### Frontend Configuration

| Variable | Description | Default |
|----------|-------------|----------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:8000/api/v1` |

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints

#### Cost Management
- `GET /api/v1/costs/overview` - Cost overview summary
- `GET /api/v1/costs/namespaces` - Namespace-wise costs
- `GET /api/v1/costs/trends` - Cost trends over time
- `GET /api/v1/costs/azure-resources` - Azure resource costs

#### Recommendations
- `GET /api/v1/recommendations/` - Optimization recommendations
- `PUT /api/v1/recommendations/{id}/status` - Update recommendation status
- `POST /api/v1/recommendations/generate` - Generate new recommendations

#### Analytics
- `GET /api/v1/analytics/comparisons` - Cost comparisons
- `GET /api/v1/analytics/efficiency-metrics` - Resource efficiency
- `GET /api/v1/analytics/cost-forecast` - Cost forecasting

## Development

### Backend Development

1. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Run database migrations**
```bash
alembic upgrade head
```

3. **Start the development server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. **Run tests**
```bash
pytest
```

### Frontend Development

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Start the development server**
```bash
npm start
```

3. **Run tests**
```bash
npm test
```

4. **Build for production**
```bash
npm run build
```

## Monitoring

### Health Checks

- Backend: `GET /health`
- Database: Connection pool monitoring
- Redis: Connection status

### Metrics

The application exposes metrics for monitoring:

- Cost collection status
- API response times
- Error rates
- Resource utilization

## Security

### Authentication

- JWT-based authentication
- Secure secret management
- Role-based access control (RBAC)

### Data Protection

- Encrypted database connections
- Secure API communication
- Environment variable protection

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow clean architecture principles
- Write comprehensive tests
- Update documentation
- Use conventional commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: [docs.cloudcostguard.io](https://docs.cloudcostguard.io)
- Issues: [GitHub Issues](https://github.com/your-org/cloudcostguard/issues)
- Discussions: [GitHub Discussions](https://github.com/your-org/cloudcostguard/discussions)


## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://reactjs.org/) - Frontend framework
- [Prometheus](https://prometheus.io/) - Metrics collection
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Helm](https://helm.sh/) - Kubernetes package manager
