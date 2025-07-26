from app.database import data_collection

result = data_collection.delete_many({})
print(f"Đã xóa {result.deleted_count} document trong collection 'memory'.")
