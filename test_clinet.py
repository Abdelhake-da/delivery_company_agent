from dotenv import load_dotenv
load_dotenv()

from api_client import ShippingAPIClient

client = ShippingAPIClient.from_env()


print(f'{"-"*20} Health Check {"-"*20}')
print("Health check:", client.health_check())


print(f'{"-"*20} Get Shipments {"-"*20}')
print("Get shipments:", client.get_shipments())


print(f'{"-"*20} Get Delayed Shipments {"-"*20}')
print("Get delayed shipments:", client.get_delayed_shipments())


print(f'{"-"*20} Get Returned Shipments {"-"*20}')
print("Get returned shipments:", client.get_returned_shipments())


print(f'{"-"*20} Get Payments Summary {"-"*20}')
print("Get payments summary:", client.get_payments_summary())


print(f'{"-"*20} Get Branches Performance {"-"*20}')
print("Get branches performance:", client.get_branches_performance())


print(f'{"-"*20} Get Management Overview {"-"*20}')
print("Get management overview:", client.get_management_overview())