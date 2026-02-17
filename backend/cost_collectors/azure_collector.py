import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from azure.identity import DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import QueryDefinition, QueryTimeframe, QueryType, QueryAggregation, QueryGrouping
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from models.cost_models import AzureCostData
from models.schemas import AzureCostDataCreate
import structlog

logger = structlog.get_logger()


class AzureCostCollector:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.client = CostManagementClient(credential=self.credential)
    
    async def collect_cost_data(
        self, 
        start_date: datetime, 
        end_date: datetime,
        resource_group: str = None
    ) -> List[Dict[str, Any]]:
        """
        Collect cost data from Azure Cost Management API
        """
        try:
            query_definition = QueryDefinition(
                type=QueryType.ACTUAL_COST,
                timeframe=QueryTimeframe.CUSTOM,
                time_period={
                    "from_property": start_date.isoformat(),
                    "to_property": end_date.isoformat()
                },
                dataset={
                    "granularity": "daily",
                    "aggregation": {
                        "totalCost": QueryAggregation(name="PreTaxCost", function="Sum")
                    },
                    "grouping": [
                        QueryGrouping(type="Dimension", name="ResourceGroupName"),
                        QueryGrouping(type="Dimension", name="ResourceType"),
                        QueryGrouping(type="Dimension", name="ServiceName"),
                        QueryGrouping(type="Dimension", name="ResourceLocation")
                    ]
                }
            )
            
            scope = f"/subscriptions/{self.subscription_id}"
            if resource_group:
                scope = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}"
            
            result = self.client.query.usage(scope, query_definition)
            
            cost_data = []
            if result.rows:
                for row in result.rows:
                    cost_data.append({
                        "date": row[0],
                        "resource_group": row[1],
                        "resource_type": row[2],
                        "service_name": row[3],
                        "location": row[4],
                        "currency": row[5],
                        "cost": row[6]
                    })
            
            logger.info(f"Collected {len(cost_data)} cost records from Azure")
            return cost_data
            
        except Exception as e:
            logger.error(f"Error collecting Azure cost data: {str(e)}")
            raise
    
    async def get_resource_details(self, resource_group: str, resource_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific resource
        """
        try:
            # This would involve Azure Resource Manager API calls
            # For now, returning basic structure
            return {
                "resource_group": resource_group,
                "resource_name": resource_name,
                "tags": {}
            }
        except Exception as e:
            logger.error(f"Error getting resource details: {str(e)}")
            return {}
    
    async def store_cost_data(self, db: AsyncSession, cost_data: List[Dict[str, Any]]):
        """
        Store collected cost data in the database
        """
        try:
            stored_count = 0
            for data in cost_data:
                # Get resource details for tags
                resource_details = await self.get_resource_details(
                    data["resource_group"], 
                    data.get("resource_name", "")
                )
                
                cost_record = AzureCostDataCreate(
                    subscription_id=self.subscription_id,
                    resource_group=data["resource_group"],
                    resource_name=data.get("resource_name", ""),
                    resource_type=data["resource_type"],
                    service_name=data["service_name"],
                    cost=data["cost"],
                    currency=data["currency"],
                    date=data["date"],
                    billing_period=f"{data['date'].year}-{data['date'].month:02d}",
                    tags=resource_details.get("tags", {})
                )
                
                db_cost = AzureCostData(**cost_record.dict())
                db.add(db_cost)
                stored_count += 1
            
            await db.commit()
            logger.info(f"Stored {stored_count} cost records in database")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error storing cost data: {str(e)}")
            raise
    
    async def run_collection(self, days_back: int = 30):
        """
        Run the complete collection process
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        logger.info(f"Starting Azure cost collection for period {start_date} to {end_date}")
        
        try:
            # Collect cost data
            cost_data = await self.collect_cost_data(start_date, end_date)
            
            # Store in database
            async for db in get_db():
                await self.store_cost_data(db, cost_data)
            
            logger.info("Azure cost collection completed successfully")
            
        except Exception as e:
            logger.error(f"Azure cost collection failed: {str(e)}")
            raise


async def schedule_azure_collection(subscription_id: str):
    """
    Scheduled task for Azure cost collection
    """
    collector = AzureCostCollector(subscription_id)
    await collector.run_collection()
