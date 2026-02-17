import asyncio
from celery import Celery
from datetime import datetime
from cost_collectors.azure_collector import schedule_azure_collection
from cost_collectors.kubernetes_collector import schedule_kubernetes_collection
from analyzers.cost_analyzer import schedule_cost_analysis
from analyzers.comparison_engine import schedule_cost_comparison
from recommendations.recommendation_engine import schedule_recommendation_generation
from core.config import settings
import structlog

logger = structlog.get_logger()

# Initialize Celery
celery_app = Celery(
    "cloudcostguard",
    broker=settings.redis_url,
    backend=settings.redis_url
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "collect-azure-costs": {
            "task": "scheduler.tasks.collect_azure_costs",
            "schedule": 3600.0,  # Every hour
        },
        "collect-kubernetes-metrics": {
            "task": "scheduler.tasks.collect_kubernetes_metrics",
            "schedule": 300.0,  # Every 5 minutes
        },
        "analyze-costs": {
            "task": "scheduler.tasks.analyze_costs",
            "schedule": 1800.0,  # Every 30 minutes
        },
        "compare-costs": {
            "task": "scheduler.tasks.compare_costs",
            "schedule": 3600.0,  # Every hour
        },
        "generate-recommendations": {
            "task": "scheduler.tasks.generate_recommendations",
            "schedule": 7200.0,  # Every 2 hours
        },
    },
)


@celery_app.task(bind=True, max_retries=3)
def collect_azure_costs(self):
    """
    Scheduled task to collect Azure cost data
    """
    try:
        logger.info("Starting Azure cost collection task")
        
        if not settings.azure_subscription_id:
            logger.warning("Azure subscription ID not configured, skipping collection")
            return
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(
            schedule_azure_collection(settings.azure_subscription_id)
        )
        
        logger.info("Azure cost collection completed successfully")
        
    except Exception as exc:
        logger.error(f"Azure cost collection failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def collect_kubernetes_metrics(self):
    """
    Scheduled task to collect Kubernetes metrics
    """
    try:
        logger.info("Starting Kubernetes metrics collection task")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(
            schedule_kubernetes_collection(settings.prometheus_url)
        )
        
        logger.info("Kubernetes metrics collection completed successfully")
        
    except Exception as exc:
        logger.error(f"Kubernetes metrics collection failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def analyze_costs(self):
    """
    Scheduled task to analyze costs and allocate to namespaces
    """
    try:
        logger.info("Starting cost analysis task")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(
            schedule_cost_analysis()
        )
        
        logger.info("Cost analysis completed successfully")
        
    except Exception as exc:
        logger.error(f"Cost analysis failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def compare_costs(self):
    """
    Scheduled task to compare costs between periods
    """
    try:
        logger.info("Starting cost comparison task")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(
            schedule_cost_comparison()
        )
        
        logger.info("Cost comparison completed successfully")
        
    except Exception as exc:
        logger.error(f"Cost comparison failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def generate_recommendations(self):
    """
    Scheduled task to generate optimization recommendations
    """
    try:
        logger.info("Starting recommendation generation task")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(
            schedule_recommendation_generation()
        )
        
        logger.info("Recommendation generation completed successfully")
        
    except Exception as exc:
        logger.error(f"Recommendation generation failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


# Manual trigger tasks for testing and on-demand execution
@celery_app.task
def manual_azure_collection():
    """
    Manually trigger Azure cost collection
    """
    return collect_azure_costs()


@celery_app.task
def manual_kubernetes_collection():
    """
    Manually trigger Kubernetes metrics collection
    """
    return collect_kubernetes_metrics()


@celery_app.task
def manual_cost_analysis():
    """
    Manually trigger cost analysis
    """
    return analyze_costs()


@celery_app.task
def manual_cost_comparison():
    """
    Manually trigger cost comparison
    """
    return compare_costs()


@celery_app.task
def manual_recommendation_generation():
    """
    Manually trigger recommendation generation
    """
    return generate_recommendations()
