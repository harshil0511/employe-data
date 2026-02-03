from fastapi import APIRouter
from app.core.logger import mongo_logger

router = APIRouter(tags=["Logs"])

@router.get("/logs")
def get_logs(limit: int = 50, log_type: str = None):
    """
    Retrieve logs from MongoDB.
    Optional filter: log_type (e.g., 'audit_log')
    """
    if not mongo_logger.enabled:
        return {"error": "MongoDB logging is not enabled or connected."}
    
    try:
        query = {}
        if log_type:
            query["details.type"] = log_type
            
        logs_cursor = mongo_logger.collection.find(query).sort("timestamp", -1).limit(limit)
        logs = []
        for log in logs_cursor:
            log["_id"] = str(log["_id"])
            log["timestamp"] = log["timestamp"].isoformat()
            logs.append(log)
        return logs
    except Exception as e:
        return {"error": f"Failed to fetch logs: {e}"}

@router.delete("/logs")
def clear_logs():
    """
    Clear all logs from MongoDB.
    """
    if not mongo_logger.enabled:
        return {"error": "MongoDB logging is not enabled or connected."}
    
    try:
        result = mongo_logger.collection.delete_many({})
        return {"message": f"Deleted {result.deleted_count} logs."}
    except Exception as e:
        return {"error": f"Failed to delete logs: {e}"}
