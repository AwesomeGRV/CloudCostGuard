import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import parser
from core.database import get_db
from models.cost_models import KubernetesMetrics
from models.schemas import KubernetesMetricsCreate
import structlog

logger = structlog.get_logger()


class KubernetesMetricsCollector:
    def __init__(self, prometheus_url: str):
        self.prometheus_url = prometheus_url.rstrip('/')
    
    async def query_prometheus(self, query: str, time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Query Prometheus API
        """
        try:
            params = {'query': query}
            if time:
                params['time'] = time.timestamp()
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.prometheus_url}/api/v1/query"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"Prometheus query failed: {response.status}")
        
        except Exception as e:
            logger.error(f"Error querying Prometheus: {str(e)}")
            raise
    
    async def query_prometheus_range(self, query: str, start: datetime, end: datetime, step: str = "1h") -> Dict[str, Any]:
        """
        Query Prometheus range API
        """
        try:
            params = {
                'query': query,
                'start': start.timestamp(),
                'end': end.timestamp(),
                'step': step
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.prometheus_url}/api/v1/query_range"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"Prometheus range query failed: {response.status}")
        
        except Exception as e:
            logger.error(f"Error querying Prometheus range: {str(e)}")
            raise
    
    async def get_namespace_metrics(self, namespace: str = None) -> List[Dict[str, Any]]:
        """
        Get Kubernetes metrics by namespace
        """
        try:
            namespace_filter = f'namespace="{namespace}"' if namespace else ""
            
            queries = {
                'cpu_requests': f'sum(kube_pod_container_resource_requests{{resource="cpu", {namespace_filter}}}) by (namespace, pod)',
                'cpu_limits': f'sum(kube_pod_container_resource_limits{{resource="cpu", {namespace_filter}}}) by (namespace, pod)',
                'cpu_usage': f'sum(rate(container_cpu_usage_seconds_total{{container!="POD", {namespace_filter}}}[5m])) by (namespace, pod)',
                'memory_requests': f'sum(kube_pod_container_resource_requests{{resource="memory", {namespace_filter}}}) by (namespace, pod)',
                'memory_limits': f'sum(kube_pod_container_resource_limits{{resource="memory", {namespace_filter}}}) by (namespace, pod)',
                'memory_usage': f'sum(container_memory_working_set_bytes{{container!="POD", {namespace_filter}}}) by (namespace, pod)',
                'storage_requests': f'sum(kube_persistentvolumeclaim_resource_requests_storage_bytes{{{namespace_filter}}}) by (namespace, persistentvolumeclaim)',
                'storage_usage': f'sum(kubelet_volume_stats_used_bytes{{{namespace_filter}}}) by (namespace, persistentvolumeclaim)'
            }
            
            metrics = {}
            for metric_name, query in queries.items():
                try:
                    result = await self.query_prometheus(query)
                    if result['status'] == 'success' and result['data']['result']:
                        metrics[metric_name] = result['data']['result']
                    else:
                        metrics[metric_name] = []
                except Exception as e:
                    logger.warning(f"Failed to get {metric_name}: {str(e)}")
                    metrics[metric_name] = []
            
            # Combine metrics into unified format
            combined_metrics = []
            namespace_data = {}
            
            # Process CPU and memory metrics
            for metric_type, data in metrics.items():
                if metric_type in ['cpu_requests', 'cpu_limits', 'cpu_usage', 
                                 'memory_requests', 'memory_limits', 'memory_usage']:
                    for item in data:
                        namespace = item['metric'].get('namespace', 'unknown')
                        pod = item['metric'].get('pod', 'unknown')
                        value = float(item['value'][1])
                        
                        key = f"{namespace}:{pod}"
                        if key not in namespace_data:
                            namespace_data[key] = {
                                'namespace': namespace,
                                'pod_name': pod,
                                'deployment_name': self._extract_deployment_name(item['metric']),
                                'cpu_requests': 0.0,
                                'cpu_limits': 0.0,
                                'cpu_usage': 0.0,
                                'memory_requests': 0.0,
                                'memory_limits': 0.0,
                                'memory_usage': 0.0,
                                'storage_requests': 0.0,
                                'storage_usage': 0.0,
                                'labels': item['metric']
                            }
                        
                        namespace_data[key][metric_type] = value
            
            # Process storage metrics
            for metric_type, data in metrics.items():
                if metric_type in ['storage_requests', 'storage_usage']:
                    for item in data:
                        namespace = item['metric'].get('namespace', 'unknown')
                        pvc = item['metric'].get('persistentvolumeclaim', 'unknown')
                        value = float(item['value'][1])
                        
                        # For storage, we aggregate by namespace
                        key = f"{namespace}:storage"
                        if key not in namespace_data:
                            namespace_data[key] = {
                                'namespace': namespace,
                                'pod_name': 'storage-aggregate',
                                'deployment_name': '',
                                'cpu_requests': 0.0,
                                'cpu_limits': 0.0,
                                'cpu_usage': 0.0,
                                'memory_requests': 0.0,
                                'memory_limits': 0.0,
                                'memory_usage': 0.0,
                                'storage_requests': 0.0,
                                'storage_usage': 0.0,
                                'labels': item['metric']
                            }
                        
                        namespace_data[key][metric_type] += value
            
            combined_metrics = list(namespace_data.values())
            logger.info(f"Collected {len(combined_metrics)} Kubernetes metric records")
            return combined_metrics
            
        except Exception as e:
            logger.error(f"Error collecting Kubernetes metrics: {str(e)}")
            raise
    
    def _extract_deployment_name(self, labels: Dict[str, Any]) -> str:
        """
        Extract deployment name from pod labels
        """
        return labels.get('deployment', labels.get('app', labels.get('k8s-app', '')))
    
    async def store_metrics(self, db: AsyncSession, metrics: List[Dict[str, Any]], cluster_name: str):
        """
        Store collected metrics in the database
        """
        try:
            stored_count = 0
            for metric_data in metrics:
                metrics_record = KubernetesMetricsCreate(
                    namespace=metric_data['namespace'],
                    pod_name=metric_data['pod_name'],
                    deployment_name=metric_data['deployment_name'],
                    cpu_requests=metric_data['cpu_requests'],
                    cpu_limits=metric_data['cpu_limits'],
                    cpu_usage=metric_data['cpu_usage'],
                    memory_requests=metric_data['memory_requests'],
                    memory_limits=metric_data['memory_limits'],
                    memory_usage=metric_data['memory_usage'],
                    storage_requests=metric_data['storage_requests'],
                    storage_usage=metric_data['storage_usage'],
                    timestamp=datetime.utcnow(),
                    cluster_name=cluster_name,
                    labels=metric_data['labels']
                )
                
                db_metrics = KubernetesMetrics(**metrics_record.dict())
                db.add(db_metrics)
                stored_count += 1
            
            await db.commit()
            logger.info(f"Stored {stored_count} Kubernetes metric records in database")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error storing Kubernetes metrics: {str(e)}")
            raise
    
    async def run_collection(self, cluster_name: str = "default", namespace: str = None):
        """
        Run the complete metrics collection process
        """
        logger.info(f"Starting Kubernetes metrics collection for cluster {cluster_name}")
        
        try:
            # Collect metrics
            metrics = await self.get_namespace_metrics(namespace)
            
            # Store in database
            async for db in get_db():
                await self.store_metrics(db, metrics, cluster_name)
            
            logger.info("Kubernetes metrics collection completed successfully")
            
        except Exception as e:
            logger.error(f"Kubernetes metrics collection failed: {str(e)}")
            raise


async def schedule_kubernetes_collection(prometheus_url: str, cluster_name: str = "default"):
    """
    Scheduled task for Kubernetes metrics collection
    """
    collector = KubernetesMetricsCollector(prometheus_url)
    await collector.run_collection(cluster_name)
