"""
Simple demo server for CloudCostGuard
This provides a basic demonstration without complex dependencies
"""

import json
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time


class CloudCostGuardHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            response = {
                "message": "Welcome to CloudCostGuard Demo Server",
                "version": "1.0.0-demo",
                "status": "running",
                "endpoints": [
                    "/api/v1/costs/overview",
                    "/api/v1/costs/namespaces",
                    "/api/v1/recommendations/",
                    "/api/v1/analytics/comparisons",
                    "/health"
                ]
            }
        elif path == '/health':
            response = {
                "status": "healthy",
                "version": "1.0.0-demo",
                "timestamp": datetime.datetime.now().isoformat()
            }
        elif path == '/api/v1/costs/overview':
            response = {
                "total_cost": 12543.67,
                "azure_cost": 8234.45,
                "kubernetes_cost": 4309.22,
                "period": "current_month",
                "currency": "USD",
                "change_percentage": 12.5,
                "last_updated": datetime.datetime.now().isoformat()
            }
        elif path == '/api/v1/costs/namespaces':
            response = {
                "namespaces": [
                    {
                        "name": "production",
                        "cost": 2345.67,
                        "percentage": 54.3,
                        "resources": {
                            "cpu_cost": 1234.56,
                            "memory_cost": 890.11,
                            "storage_cost": 220.00
                        }
                    },
                    {
                        "name": "staging",
                        "cost": 1234.56,
                        "percentage": 28.6,
                        "resources": {
                            "cpu_cost": 678.90,
                            "memory_cost": 456.78,
                            "storage_cost": 98.88
                        }
                    },
                    {
                        "name": "development",
                        "cost": 728.99,
                        "percentage": 16.9,
                        "resources": {
                            "cpu_cost": 345.67,
                            "memory_cost": 289.12,
                            "storage_cost": 94.20
                        }
                    }
                ],
                "total": 4309.22,
                "currency": "USD"
            }
        elif path == '/api/v1/recommendations/':
            response = {
                "recommendations": [
                    {
                        "id": 1,
                        "type": "right_sizing",
                        "title": "Right-size production namespace CPU",
                        "description": "CPU utilization is consistently below 30%, consider reducing CPU allocation",
                        "potential_savings": 234.56,
                        "confidence": 85,
                        "priority": "high",
                        "resource_type": "cpu",
                        "namespace": "production",
                        "status": "pending",
                        "created_at": datetime.datetime.now().isoformat()
                    },
                    {
                        "id": 2,
                        "type": "storage_optimization",
                        "title": "Optimize storage in staging namespace",
                        "description": "Unused persistent volumes detected, cleanup can save costs",
                        "potential_savings": 123.45,
                        "confidence": 92,
                        "priority": "medium",
                        "resource_type": "storage",
                        "namespace": "staging",
                        "status": "pending",
                        "created_at": datetime.datetime.now().isoformat()
                    },
                    {
                        "id": 3,
                        "type": "schedule_optimization",
                        "title": "Implement non-production scaling schedules",
                        "description": "Scale down development resources during non-working hours",
                        "potential_savings": 456.78,
                        "confidence": 78,
                        "priority": "medium",
                        "resource_type": "compute",
                        "namespace": "development",
                        "status": "pending",
                        "created_at": datetime.datetime.now().isoformat()
                    }
                ],
                "total_recommendations": 3,
                "total_potential_savings": 814.79,
                "currency": "USD"
            }
        elif path == '/api/v1/analytics/comparisons':
            response = {
                "comparisons": [
                    {
                        "period": "current_month",
                        "cost": 12543.67,
                        "previous_period": "last_month",
                        "previous_cost": 11156.82,
                        "change_percentage": 12.5,
                        "change_amount": 1386.85,
                        "currency": "USD"
                    },
                    {
                        "period": "last_month",
                        "cost": 11156.82,
                        "previous_period": "two_months_ago",
                        "previous_cost": 10890.45,
                        "change_percentage": 2.4,
                        "change_amount": 266.37,
                        "currency": "USD"
                    }
                ],
                "trend": "increasing",
                "average_monthly_change": 7.45
            }
        else:
            response = {"error": "Endpoint not found"}

        self.wfile.write(json.dumps(response, indent=2).encode())

    def do_POST(self):
        """Handle POST requests"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/api/v1/recommendations/generate':
            response = {
                "message": "Recommendations generation started",
                "task_id": "demo-task-123",
                "status": "in_progress"
            }
        else:
            response = {"error": "Endpoint not found"}

        self.wfile.write(json.dumps(response, indent=2).encode())

    def do_PUT(self):
        """Handle PUT requests"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if '/api/v1/recommendations/' in path and '/status' in path:
            response = {
                "message": "Recommendation status updated successfully",
                "status": "acknowledged"
            }
        else:
            response = {"error": "Endpoint not found"}

        self.wfile.write(json.dumps(response, indent=2).encode())

    def log_message(self, format, *args):
        """Custom log messages"""
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")


def run_server():
    """Run the demo server"""
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CloudCostGuardHandler)
    print("🚀 CloudCostGuard Demo Server Starting...")
    print("📊 Server running on http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/api/v1/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down CloudCostGuard Demo Server...")
        httpd.server_close()


if __name__ == '__main__':
    run_server()
