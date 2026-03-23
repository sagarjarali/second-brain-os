def check_crop_season(crop, season):
    if crop == "jowar" and season == "kharif":
        return "jowar is perfect for kharif"
    elif crop == "wheat" and season == "rabi":
        return "wheat is perfect for rabi"
    else:
        return "season suitability unknown"

result1 = check_crop_season("jowar","kharif")
print(result1)

result2 = check_crop_season("wheat","rabi")
print(result2)
    
result3 = check_crop_season("cotton","zaid")
print(result3)