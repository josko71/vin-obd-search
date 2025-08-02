from vozila.models import CarModel
total_models = CarModel.objects.count()
print(f"Skupno število modelov v bazi je: {total_models}")
exit() # Za izhod iz Django shella